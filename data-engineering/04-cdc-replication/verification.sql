-- SQLite query over the generated artifact.
SELECT deleted, COUNT(*) AS keys, SUM(balance_cents) AS balance_cents FROM state GROUP BY deleted;
