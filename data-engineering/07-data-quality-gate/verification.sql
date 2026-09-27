-- SQLite query over the generated artifact.
SELECT SUM(duplicate_id) AS duplicate_id, SUM(negative_amount) AS negative_amount, SUM(unknown_customer) AS unknown_customer, SUM(invalid_date) AS invalid_date FROM rule_audit;
