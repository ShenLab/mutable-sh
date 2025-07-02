DROP TABLE IF EXISTS samples;

CREATE TABLE samples (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sample TEXT UNIQUE,
  family TEXT,
  father TEXT,
  mother TEXT,
  sex TEXT,
  status TEXT,
  syndromic BOOLEAN,
  cohort TEXT,
  cohort_condition TEXT,
  batch TEXT,
  dup_id TEXT,
  prev_studies TEXT,
  twin BOOLEAN,
  zygosity TEXT,
  twin_aff BOOLEAN,
  twin_partic BOOLEAN,
  phenotype TEXT,
  hpo TEXT,
  hpo_id TEXT,
  genetic_data BOOLEAN,
  dnv_callable BOOLEAN,
  published BOOLEAN,
  dnv_count INTEGER
);
