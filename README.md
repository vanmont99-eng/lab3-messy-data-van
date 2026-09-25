# Lab 3: Parsing Messy Health Data

Cleans `messy_samples.csv` (60 synthetic clinical records) two ways, with a regex
script and with a generative AI tool, then compares the results.

## Setup
```
conda env create -f environment.yml
conda activate lab3
```

## Run
```
python clean_regex.py     # data/raw/messy_samples.csv -> output/regex_clean.csv
python compare.py         # regex vs AI outputs -> output/comparison.csv
```
`clean_regex.py` also takes optional paths: `python clean_regex.py <input.csv> <output.csv>`

To regenerate the raw data (seeded, identical every time):
```
cd data/raw && python generate_data.py
```

## Files
- `data/raw/` raw messy data + the instructor's generator script
- `clean_regex.py` regex cleaning script
- `output/regex_clean.csv` regex output
- `output/ai_clean.csv` AI output (prompt in AI_USAGE.md)
- `compare.py` cell by cell comparison of the two
- `output/comparison.csv` every cell where they disagree
- `NOTES.md` data inventory, cleaning decisions, failure mode notes
- `WRITEUP.md` comparison write-up
- `AI_USAGE.md` AI use log

## Output columns
sample_id, patient_name, dob (YYYY-MM-DD), dob_flag, sex (M/F/Unknown),
site (A/B/C), glucose_mg_dl, glucose_flag, notes

The flag columns record every guess or judgment call the script made.

## Extra credit (graduate addendum)
```
python clean_fasta_regex.py      # data/raw/messy_sequences.fasta -> output/fasta_regex_clean.csv
python compare_fasta.py          # regex vs AI -> output/fasta_comparison.csv
python build_feature_table.py    # output/regex_clean.csv -> output/feature_table.csv
```
- `clean_fasta_regex.py` regex parser for the FASTA headers
- `output/fasta_regex_clean.csv` FASTA regex output
- `output/fasta_ai_clean.csv` FASTA AI output (prompt in AI_USAGE.md)
- `compare_fasta.py` / `output/fasta_comparison.csv` FASTA comparison
- `build_feature_table.py` / `output/feature_table.csv` samples x features x metadata table
- Write-up for all of this is at the bottom of WRITEUP.md
