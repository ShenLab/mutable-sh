DROP TABLE IF EXISTS dnvs;

CREATE TABLE dnvs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chromosome INTEGER,
  position INTEGER,
  ref TEXT,
  alt TEXT,
  sample TEXT,
  status TEXT,
  cohort TEXT,
  cohort_condition TEXT,
  gene TEXT,
  consequence TEXT,
  transcript TEXT,
  aa_change TEXT,
  dna_change TEXT,
  CADD REAL,
  REVEL REAL,
  gMVP REAL,
  MisFit_D REAL,
  MisFit_S REAL,
  AlphaMissense REAL,
  spliceAI REAL,
  gnomAD4_AF REAL,
  vid TEXT UNIQUE);

  CREATE INDEX idx_sample ON dnvs (sample);