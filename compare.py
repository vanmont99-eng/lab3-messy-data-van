"""Compare regex vs AI cleaning outputs, cell by cell.

Usage: python compare.py
Reads output/regex_clean.csv + output/ai_clean.csv, writes output/comparison.csv
"""
import pandas as pd

RAW = "data/raw/messy_samples.csv"
rx = pd.read_csv("output/regex_clean.csv", dtype=str, keep_default_na=False)
ai = pd.read_csv("output/ai_clean.csv", dtype=str, keep_default_na=False)
raw = pd.read_csv(RAW, dtype=str, keep_default_na=False)
raw["sample_id"] = rx["sample_id"]  # rows are in the same order, use the clean ids

print(f"regex rows: {len(rx)}, AI rows: {len(ai)}")
missing = set(rx["sample_id"]) - set(ai["sample_id"])
if missing:
    print("AI dropped these samples:", sorted(missing))

merged = rx.merge(ai, on="sample_id", suffixes=("_regex", "_ai"))
cols = ["patient_name", "dob", "sex", "site", "glucose_mg_dl", "notes"]
diffs = []
for col in cols:
    a, b = merged[f"{col}_regex"], merged[f"{col}_ai"]
    if col == "glucose_mg_dl":  # compare as numbers so 120 == 120.0
        same = pd.to_numeric(a, errors="coerce").eq(pd.to_numeric(b, errors="coerce")) | (a.eq("") & b.eq(""))
    else:
        same = a.eq(b)
    agree = int(same.sum())
    print(f"{col:15s} agree {agree}/{len(merged)}")
    for _, r in merged[~same].iterrows():
        raw_row = raw[raw["sample_id"] == r["sample_id"]].iloc[0]
        diffs.append({
            "sample_id": r["sample_id"],
            "column": col,
            "regex": r[f"{col}_regex"],
            "ai": r[f"{col}_ai"],
            "raw_value": raw_row["glucose_value"] if col == "glucose_mg_dl" else "",
            "raw_unit": raw_row["glucose_unit"] if col == "glucose_mg_dl" else "",
        })

out = pd.DataFrame(diffs)
out.to_csv("output/comparison.csv", index=False)
print(f"\n{len(out)} disagreements written to output/comparison.csv")
if len(out):
    print(out.to_string(index=False))
