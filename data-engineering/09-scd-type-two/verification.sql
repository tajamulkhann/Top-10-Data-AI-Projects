-- SQLite query over the generated artifact.
SELECT region, COUNT(*) AS versions, SUM(is_current) AS current_versions FROM dim_customer GROUP BY region;
