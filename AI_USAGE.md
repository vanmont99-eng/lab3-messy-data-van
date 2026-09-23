## Chat GPT was used to check the csv to see how it would clean it and the prompt given was 
``` Clean this messy clinical dataset. Return ONLY a CSV with no explanation, using exactly these columns:
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

Data: pasted 

``` 


