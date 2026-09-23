## Models used
- Claude Opus 5.5 (claude.ai): walked me through the lab step by step, drafted scripts and docs (details below)
- Chat GPT 5 in a fresh chat with no prior context: Task 2 AI cleaning


## Task 2: AI cleaning (ChatGPT, output/ai_clean.csv)
ChatGPT was used to clean the same CSV so I could compare it to the regex script. The prompt given was:

```
Clean this messy clinical dataset. Return ONLY a CSV with no explanation, using exactly these columns:
sample_id,patient_name,dob,dob_flag,sex,site,glucose_mg_dl,glucose_flag,notes

Rules:
- sample_id: format S0001
- patient_name: title case
- dob: YYYY-MM-DD
- sex: M, F, or Unknown
- site: A, B, or C
- glucose_mg_dl: numeric, all values in mg/dL
- dob_flag and glucose_flag: note anything you changed, guessed, or couldn't resolve
- notes: keep as-is

Data:
<full contents of data/raw/messy_samples.csv pasted here>
```

Off-target result: ChatGPT multiplied all 12 "mmol/L" values by 18 (e.g. S0039 74.9 -> 1348.2 mg/dL)
without flagging them as impossible. I rejected that and kept the regex rule instead (see WRITEUP.md).

## Task 1: Regex script (clean_regex.py)
- Claude drafted clean_regex.py and explained what each regex does.
- I reviewed it, ran it on the raw data, and checked the output against the raw file.
- Decisions I made myself after inspecting the data (see NOTES.md):
  - mmol/L values over 50 are flagged, not converted, because they aren't physiologically possible
  - 2-digit years that land in the future get 100 subtracted (11.24.53 -> 1953)
- Claude also drafted environment.yml and the pandas one-liners I used to inspect the data.

## Comparison (compare.py)
- Claude drafted compare.py. I ran it and used its output (output/comparison.csv) for the write-up.

## Write-up (WRITEUP.md)
- Claude (Claude Code) checked the repo against the Lab 3 rubric, re-ran both scripts to confirm the
  outputs reproduce, and drafted WRITEUP.md from my NOTES.md findings and the comparison output.

## What I checked myself
- Ran both scripts and confirmed the output (60 rows, 48/60 glucose agreement)
- Checked the mmol/L values against normal glucose ranges from my clinical work
- Confirmed the AI output had all 60 rows and no dropped samples

