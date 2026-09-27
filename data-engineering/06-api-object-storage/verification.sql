-- SQLite query over the generated artifact.
SELECT date, COUNT(*) AS rows, COUNT(DISTINCT station_id) AS stations FROM observations GROUP BY date;
