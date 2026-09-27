-- SQLite query over the generated artifact.
SELECT partition_date, COUNT(*) AS rows, SUM(amount_cents) AS amount_cents FROM target GROUP BY partition_date;
