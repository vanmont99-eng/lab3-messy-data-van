"""Build a samples x features x metadata table from the regex-cleaned CSV.

Usage: python build_feature_table.py
Reads output/regex_clean.csv, writes output/feature_table.csv
"""
import pandas as pd

REF_DATE = pd.Timestamp("2026-01-01")  # fixed date so age is reproducible

clean = pd.read_csv("output/regex_clean.csv", keep_default_na=False, na_values=[""])
clean["dob"] = pd.to_datetime(clean["dob"])

# features: numeric columns a model would use, one row per sample
features = pd.DataFrame({
    "sample_id": clean["sample_id"],
    "age_years": ((REF_DATE - clean["dob"]).dt.days / 365.25).round(1),
    "glucose_mg_dl": clean["glucose_mg_dl"].astype(float),
})

# metadata: who/where the sample came from + data quality flags
metadata = pd.DataFrame({
    "sample_id": clean["sample_id"],
    "sex": clean["sex"].astype("category"),
    "site": clean["site"].astype("category"),
    "glucose_missing": clean["glucose_mg_dl"].isna(),
    "glucose_unit_suspect": clean["glucose_flag"].fillna("").str.contains("not converted"),
    "glucose_asterisk": clean["glucose_flag"].fillna("").str.contains("asterisk"),
    "dob_year_inferred": clean["dob_flag"].fillna("").str.contains("2-digit"),
    "notes": clean["notes"].fillna(""),
})

table = features.merge(metadata, on="sample_id", how="left", validate="one_to_one")
table.to_csv("output/feature_table.csv", index=False)

print(f"Wrote {len(table)} rows x {table.shape[1]} columns to output/feature_table.csv\n")
print("Column types:")
print(table.dtypes.to_string(), "\n")
print("Missing values:")
print(table.isna().sum()[table.isna().sum() > 0].to_string(), "\n")
print("Quality flags:")
for col in ["glucose_unit_suspect", "glucose_asterisk", "dob_year_inferred"]:
    print(f"  {col}: {int(table[col].sum())} samples")
print(f"  sex == Unknown: {int((table['sex'] == 'Unknown').sum())} samples")
print(f"  age under 18: {int((table['age_years'] < 18).sum())} samples")
