"""Regex-based parser for messy_sequences.fasta headers.

Usage: python clean_fasta_regex.py [input_fasta] [output_csv]
Defaults: data/raw/messy_sequences.fasta -> output/fasta_regex_clean.csv
"""
import os
import re
import sys

import pandas as pd

IN_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/raw/messy_sequences.fasta"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "output/fasta_regex_clean.csv"

KNOWN_GENES = ["BRCA1", "TP53", "EGFR"]


def read_fasta(path):
    # returns a list of (header, sequence) pairs
    records = []
    for line in open(path):
        line = line.strip()
        if line.startswith(">"):
            records.append([line, ""])
        elif records:
            records[-1][1] += line
    return records


def parse_id(header):
    # any word (sample, Sample, SAMPLE, seq), optional _ or -, then the number
    m = re.match(r">\s*[A-Za-z]+[_-]?(\d+)", header)
    return f"sample_{int(m.group(1)):03d}" if m else None


def parse_organism(header):
    # Homo_sapiens, Homo sapiens, H.sapiens, Hsapiens
    if re.search(r"homo[\s_]?sapiens|\bh\.?\s?sapiens", header, re.IGNORECASE):
        return "Homo sapiens"
    return None


def parse_gene(header):
    # labeled first (gene= / gene: / target=), then fall back to known gene names
    m = re.search(r"(?:gene|target)\s*[=:]\s*([A-Za-z0-9]+)", header, re.IGNORECASE)
    if m:
        return m.group(1).upper(), ""
    for g in KNOWN_GENES:
        if re.search(rf"\b{g}\b", header):
            return g, "gene not labeled, matched by name"
    return None, "gene not found"


def parse_declared_length(header):
    # len=120, length=150bp, len:NA, 130 bp
    m = re.search(r"len(?:gth)?\s*[=:]\s*(\d+|NA)|(\d+)\s*bp", header, re.IGNORECASE)
    if not m:
        return None
    value = m.group(1) or m.group(2)
    return None if value.upper() == "NA" else int(value)


def parse_note(header):
    m = re.search(r"note\s*[=:]\s*([^|;]+)", header, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def main():
    rows = []
    for header, seq in read_fasta(IN_PATH):
        gene, gene_flag = parse_gene(header)
        declared = parse_declared_length(header)
        actual = len(seq)
        if declared is None:
            length_flag = "no declared length"
        elif declared != actual:
            length_flag = f"header says {declared}, sequence is {actual}"
        else:
            length_flag = ""
        rows.append({
            "sample_id": parse_id(header),
            "organism": parse_organism(header),
            "gene": gene,
            "gene_flag": gene_flag,
            "declared_length": declared,
            "actual_length": actual,
            "length_flag": length_flag,
            "note": parse_note(header),
            "raw_header": header,
        })
    out = pd.DataFrame(rows)
    out["declared_length"] = out["declared_length"].astype("Int64")  # keeps ints with missing values
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    out.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(out)} records to {OUT_PATH}")
    print(out.drop(columns="raw_header").to_string(index=False))


if __name__ == "__main__":
    main()
