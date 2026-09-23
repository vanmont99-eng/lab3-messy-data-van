# Lab 3 write-up: regex vs AI cleaning of messy_samples.csv

Dataset: `data/raw/messy_samples.csv` (60 records). Regex output: `output/regex_clean.csv`.
AI output (ChatGPT, prompt in `AI_USAGE.md`): `output/ai_clean.csv`. Cell by cell diff: `output/comparison.csv`.

## Agreement and disagreement

| Column | Agree (of 60) |
|---|---|
| patient_name, dob, sex, site, notes | 60 |
| glucose_mg_dl | 48 |

Both approaches handled every format variant in the file the same way:
- **IDs:** `s-0003`, `s-0008`, `s-0011` etc. became `S0003`, `S0008`, `S0011`.
- **Dates:** all 4 formats, e.g. `11.24.53` became 1953-11-24 (S0003), `21-Jun-1997` became 1997-06-21 (S0008).
- **Sex and site:** `Male`/`m`/`M` became M. `site_a`/`SITE-A` became A. `Site  C` (double space) and `Site C ` (trailing space) became C (S0010, S0017).
- **Glucose:** `N/A` became missing (S0012, S0056). The trailing `*` was stripped (S0032 `112.3*`, S0043 `223.1*`).

The only disagreements were the 12 rows labeled `mmol/L` that had a number: S0006, S0011, S0014, S0015,
S0016, S0017, S0024, S0033, S0035, S0038, S0039, S0046. The AI multiplied each one by 18 (S0017: 249.2 became
4485.6 mg/dL). The regex kept the number and flagged the label as wrong. The 13th mmol/L row, S0056, is `N/A`, so both left it missing.

## Which caught more edge cases

**The regex caught the one edge case that matters.** All of its values fall between 74.9 and 249.3 mg/dL, while the AI's converted
values run from 1348 to 4486 mg/dL. The instructor's `generate_data.py` confirms the regex was right. It draws every
glucose value from 70–250 and assigns the unit label at random, so "mmol/L" is noise and the number is really mg/dL.

**The AI's flags were richer in wording but less usable.** It wrote the actual inferred year
("assumed 1953 from 2-digit year") where the regex just says "2-digit year inferred". But its flags are
inconsistent. `dob_flag` has 14 distinct strings, and the same situation gets different text: S0012 says "missing/N/A; could not
resolve" while S0056 says "missing/N/A; could not convert from mmol/L". It also put "reformatted" on 30 rows
where nothing was guessed, which buries the real flags. The regex uses a fixed vocabulary and flags only
judgment calls, so you can filter on it.

## Time/effort

- **AI:** one prompt, output in about 5 minutes, plus about 15 minutes checking it. It looked finished immediately,
  and that's the risk: the 12 wrong values look like ordinary numbers until you check the range.
- **Regex:** about 1-2 hours to write, run, and fix. More work up front, but it's rerunnable, deterministic, and
  every decision (the <50 mmol/L threshold, the 2-digit year rule) is visible in `clean_regex.py`.

## Failure modes

1. **S0039, AI wrong: physiologically impossible conversion.** Raw `74.9 mmol/L`. The AI output 1348.2 mg/dL with
   the flag "converted from mmol/L to mg/dL". It applied the textbook ×18 factor without checking whether the result
   was plausible. Normal glucose is about 4–6 mmol/L and even DKA rarely goes past about 30, so 74.9 mmol/L can't be real. The prompt said to
   flag anything it "couldn't resolve", but the AI didn't see a conflict to resolve. It followed the label.
   The regex handled it only because I added a rule (`num < 50`) after looking at the data. A regex without that rule
   would have made the same mistake.

2. **S0060 and S0001, both ambiguous: day vs month order.** `02.09.06` and `07/09/1962` were read month-first by
   both approaches (Feb 9 2006, Jul 9 1962), but day-first (Sep 2, Sep 7) is just as valid. 12 of 60 DOBs have both
   parts ≤12 and different (S0046 `12.12.09` reads the same either way), so they have this problem: S0001, S0010, S0015, S0016, S0031, S0034, S0037, S0039, S0044, S0052, S0058, S0060.
   The 60/60 agreement doesn't show that either approach is right. They share the same US-centric assumption,
   so they fail together. Month-first is right here only because the generator uses `%m`. With real data you couldn't tell from the file.
   S0060 also has a century problem: `06` could be 1906 or 2006. Both chose 2006.

3. **Both: "Unknown" sex erases information.** `U` (9 rows), `unknown` (6), and blank (4) all collapsed to Unknown.
   A recorded "unknown" and a field nobody filled in are different kinds of missingness, and after cleaning you can't
   tell them apart.

## Which I'd trust for a real dataset

The regex, used together with a human check. It's reproducible, auditable, and it fails loudly (unparsed values become
`None` with a flag) instead of producing plausible-looking wrong numbers. The AI was useful for a fast first pass and
for spotting format variants, but its output needs a range check before anyone uses it. Its most serious error here looked
exactly like a correct value. In both cases the domain knowledge (what glucose values are possible) came from
me, not from either tool.
