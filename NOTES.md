# Lab 3 data inventory (messy_samples.csv)

## What's messy
- sample_id: mostly S0001 style, some s-0003 style -> standardize to S0003
- patient_name: some all caps -> title case
- sex: M, Male, m / F, Female, f / U, unknown, blank -> M, F, Unknown
- site: Site A, SITE-A, site_a / Site B, siteB / Site  C (double space), Site C (trailing space) -> A, B, C
- units: mg/dL, mg/dl, MG/DL, mmol/L -> everything in mg/dL
- dob: 4 formats
  - MM/DD/YYYY (01/20/1965)
  - YYYY-MM-DD (1960-10-28)
  - DD-Mon-YYYY (06-Feb-1951)
  - MM.DD.YY (11.24.53) <- 2 digit year, ambiguous (1953 or 2053?)
- glucose_value: N/A x2 (S0012, S0056), trailing * x2 (S0032, S0043)

## mmol/L problem
13 rows are labeled mmol/L but the values are 74.9 to 249.2. Normal glucose is
about 4-6 mmol/L and even DKA is usually under 30-ish. 74.9 mmol/L would be about
1350 mg/dL. These values are in the same 70-250 range as the mg/dL rows, so the
unit label is almost definitely wrong, not the number.

## Decision
- If unit is mmol/L and value is under 50, convert to mg/dL (x18)
- If unit is mmol/L and value is over 50, don't convert. Keep the value as mg/dL
  and set glucose_flag = "labeled mmol/L but only plausible as mg/dL, not converted"
- Blindly multiplying by 18 would give values like 2541.6 mg/dL for S0006, which
  is not physically possible

## 2 digit years
Python's %y reads 00-68 as 2000s and 69-99 as 1900s. So 11.24.53 -> 2053, which is
in the future and can't be a birthday. Rule: if the parsed year is after the
current year, subtract 100.

# Failure Modes of the AI - 2 records 

## Failure mode 1: Converted impossible values

S0039, raw 74.9 mmol/L. The AI output 1348.2 mg/dL, and regex kept 74.9 with a flag.
- Did the textbook conversion but never asked whether it made sense or not, as 74.9 mmol/L is an impossible glucose level and did not flag it and still did the conversion. I wrote a rule for regex to flag those ones. 

## Failure Mode 2: Both

Records: S0060 02.09.06 and S0001 07/09/1962
Both approaches read these as month first (Feb 9, July 9). But either could just as easily be day first (Sept 2, Sept 7). European and a lot of international records use day first.
12 of 60 DOBs (20%) have both numbers ≤12, so they're ambiguous in the same way: S0001, S0010, S0015, S0016, S0031, S0034, S0037, S0039, S0044, S0052, S0058, S0060.
Why it matters: 60/60 agreement looks like proof both are right. It isn't. They made the same assumption, so they agree. Agreement between two methods only tells you something when they fail independently.
Honest caveat: the generator script does use month first, so both are correct here. But you only know that because you can read the generator. With real data, you'd have no way to tell from the file alone.

## Failure Mode 3: "Unknown" erases information (both did it)
Raw sex values: U (9), unknown (6), and blank (4). Both approaches collapsed all 19 into Unknown.
Why it matters: U means someone recorded that it's unknown. Blank might mean nobody entered anything. Those aren't the same missingness, and after cleaning you can't tell them apart anymore.
# FASTA inventory (messy_sequences.fasta)

## What's messy
- sample_id: sample_001, Sample002, sample-003, SAMPLE_004, sample005, seq6, Sample_007, sample-8
  -> standardize to sample_001 ... sample_008. seq6 doesn't say "sample" so match on the number.
- separators: | or space or ; or mixed (" | ", space + |)
- organism: Homo_sapiens, Homo sapiens, H.sapiens, Hsapiens -> Homo sapiens
- gene: gene=, gene:, target=, or no label at all (003, 005, seq6)
  -> match the gene name itself (BRCA1, TP53, EGFR) instead of the label
- length: len=120, length=150bp, 130 bp, len:NA, or missing (002, 004, seq6, 007)
- note: only sample 7 has one (note:re-sequenced)

## Length problem
Declared length in the header doesn't always match the actual sequence:
- sample-003 says 150bp, actual 157
- sample005 says 130 bp, actual 144
- sample_001 says 120, actual 120 (matches)
The sequence is the real data, the header is something someone typed. So actual length wins.

## Decisions
- Keep both declared_length and actual_length columns, add length_flag when they
  don't match or when there's no declared length
- len:NA -> declared_length is missing, not the text "NA"

## FASTA comparison + failure modes
Values matched 8/8 on everything (organism, gene, declared length, actual length, note).
All the disagreements were in the flags.

1. Header length is wrong (both caught it): sample_003 says 150bp but the sequence is 157,
   sample005 says 130 bp but it's 144. Anyone who trusted the header would have the wrong
   length. Same idea as the mmol/L labels in the CSV, the metadata is wrong and the actual
   data is right. The AI got every actual length right [CHECK: did it run code to count?].

2. AI didn't flag its guesses: 003, 005, and seq6 have no gene label, the gene name is just
   sitting there. The AI got all 3 right but left gene_flag blank, so you can't tell which
   genes it read from a label and which it inferred. Regex flagged all 3.

3. My regex lumped two kinds of missing together: sample-8 says len:NA (someone recorded
   that it's unknown) but 002, 004, seq6, and 007 just never had a length. Regex called all 5
   "no declared length." The AI only flagged sample 8. Same problem as U vs blank for sex
   in the CSV, except this time my script is the one that lost the info.

4. Regex limit: the gene fallback only works because BRCA1, TP53, and EGFR are hardcoded.
   An unlabeled KRAS would come back "gene not found." Regex only knows what I tell it.
