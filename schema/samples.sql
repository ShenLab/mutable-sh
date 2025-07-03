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
  twin BOOLEAN,
  zygosity TEXT,
  phenotype TEXT,
  hpo TEXT,
  hpo_id TEXT,
  published BOOLEAN,
  dnv_count INTEGER
);
