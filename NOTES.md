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
  and set unit_flag = "label likely wrong"
- Blindly multiplying by 18 would give values like 2541.6 mg/dL for S0006, which
  is not physically possible

## 2 digit years
Python's %y reads 00-68 as 2000s and 69-99 as 1900s. So 11.24.53 -> 2053, which is
in the future and can't be a birthday. Rule: if the parsed year is after the
current year, subtract 100.
