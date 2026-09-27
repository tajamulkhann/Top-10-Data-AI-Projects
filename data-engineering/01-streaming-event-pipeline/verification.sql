-- SQLite query over the generated artifact.
SELECT (event_minute / 5) * 5 AS window_start, COUNT(*) AS events, SUM(value) AS total_value FROM accepted GROUP BY window_start ORDER BY window_start;
