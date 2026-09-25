"""Compare regex vs AI parsing of messy_sequences.fasta.

Usage: python compare_fasta.py
Reads output/fasta_regex_clean.csv + output/fasta_ai_clean.csv,
writes output/fasta_comparison.csv
"""
import pandas as pd

rx = pd.read_csv("output/fasta_regex_clean.csv", dtype=str, keep_default_na=False)
ai = pd.read_csv("output/fasta_ai_clean.csv", dtype=str, keep_default_na=False)
rx["declared_length"] = rx["declared_length"].replace("<NA>", "")

print(f"regex records: {len(rx)}, AI records: {len(ai)}")
merged = rx.merge(ai, on="sample_id", suffixes=("_regex", "_ai"))

rows = []
# value columns: should match exactly
for col in ["organism", "gene", "declared_length", "actual_length", "note"]:
    same = merged[f"{col}_regex"].eq(merged[f"{col}_ai"])
    print(f"{col:16s} agree {int(same.sum())}/{len(merged)}")
    for _, r in merged[~same].iterrows():
        rows.append({"sample_id": r["sample_id"], "column": col,
                     "regex": r[f"{col}_regex"], "ai": r[f"{col}_ai"]})

# flag columns: wording differs, so just compare whether each one flagged anything
for col in ["gene_flag", "length_flag"]:
    rx_flagged = merged[f"{col}_regex"].ne("")
    ai_flagged = merged[f"{col}_ai"].ne("")
    same = rx_flagged.eq(ai_flagged)
    print(f"{col:16s} both flagged or both blank {int(same.sum())}/{len(merged)}")
    for _, r in merged[~same].iterrows():
        rows.append({"sample_id": r["sample_id"], "column": col,
                     "regex": r[f"{col}_regex"] or "(blank)",
                     "ai": r[f"{col}_ai"] or "(blank)"})

out = pd.DataFrame(rows)
out.to_csv("output/fasta_comparison.csv", index=False)
print(f"\n{len(out)} disagreements written to output/fasta_comparison.csv")
if len(out):
    print(out.to_string(index=False))
