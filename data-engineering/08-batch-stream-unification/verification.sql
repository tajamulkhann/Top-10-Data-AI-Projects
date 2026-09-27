-- SQLite query over the generated artifact.
SELECT version, deleted, COUNT(*) AS keys, SUM(amount_cents) AS amount_cents FROM state GROUP BY version, deleted;
