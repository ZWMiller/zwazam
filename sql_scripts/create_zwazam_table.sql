CREATE TABLE IF NOT EXISTS zwazam(
  track varchar,
  hash bigint,
  PRIMARY KEY (track, hash)
  );

CREATE INDEX hash_index
ON zwazam (hash)
