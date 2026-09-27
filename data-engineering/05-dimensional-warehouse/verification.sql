-- SQLite query over the generated artifact.
SELECT d.region, COUNT(*) AS orders, SUM(f.amount_cents) AS amount_cents FROM fact_order f JOIN dim_customer d USING(customer_sk) GROUP BY d.region;
