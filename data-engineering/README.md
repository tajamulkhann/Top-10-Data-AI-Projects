# Top 10 Data Engineering Projects

Ten original, runnable engineering case studies by **Tajamul Khan**. Each includes synthetic source fixtures, a full Python pipeline, SQL verification, an executed notebook, architecture diagram, STAR README, operational runbook and offline dashboard.

These projects focus on moving, validating, modelling and recovering data. They use local Python/SQLite implementations so they can be reproduced immediately. Kafka, Spark, Delta Lake, Airflow and cloud services are documented extension targets, not claimed deployments.

| # | Project | Level | Core skills |
|---|---|---|---|
| 1 | [Streaming Event Pipeline with Replay Safety](01-streaming-event-pipeline/) | Intermediate | Event time · deduplication · watermark · durable state |
| 2 | [Paginated API to Warehouse ETL](02-api-to-warehouse-etl/) | Beginner to intermediate | Pagination · retries · validation · idempotent upserts |
| 3 | [Bronze Silver Gold Data Pipeline](03-medallion-lakehouse/) | Intermediate | Bronze/silver/gold · lineage · partitioning · version resolution |
| 4 | [Change Data Capture Replication](04-cdc-replication/) | Advanced | CDC · tombstones · stale events · atomic transactions |
| 5 | [Dimensional Warehouse with Referential Integrity](05-dimensional-warehouse/) | Intermediate | Surrogate keys · foreign keys · fact grain · unknown members |
| 6 | [API Snapshot Ingestion to Partitioned Storage](06-api-object-storage/) | Intermediate | Content addressing · checksums · partitions · manifest publish |
| 7 | [Data Quality Gate with Quarantine and Audit](07-data-quality-gate/) | Intermediate | Data contracts · quarantine · release gate · audit |
| 8 | [Batch and Stream Reconciliation Pipeline](08-batch-stream-unification/) | Advanced | Batch/stream overlap · version convergence · conflict detection |
| 9 | [SCD Type 2 Customer History](09-scd-type-two/) | Advanced | SCD Type 2 · intervals · historical joins · boundary checks |
| 10 | [Pipeline Orchestration with Retry and Recovery](10-orchestration-recovery/) | Advanced | Task dependencies · retries · rollback · checkpoints |

## Learning path

Begin with API ETL and the dimensional warehouse. Continue with storage ingestion, medallion layers and quality gates. Then tackle event replay, CDC, batch/stream convergence, SCD history and orchestration recovery.

## Reproduce the collection

From the repository root after installing `requirements.txt`:

```bash
python scripts/execute_all.py data-engineering
python scripts/verify_data_engineering.py
```

See [`execution_report.json`](execution_report.json) for saved execution evidence. Source generators and pipeline implementations are committed alongside every notebook. Dashboards open locally in a browser; notebooks display saved outputs on GitHub.

## Inspiration and originality

Business areas were inspired by the supplied “Top 8 Data Engineering Projects” reference images, credited to Abhishek Sahu in those images. All pipeline code and datasets here are original. Screenshots and third-party repository code are not redistributed; no exact repository URL was reliably identifiable from the images.

“Top 10” is a curated collection title, not an empirical ranking. Results reflect synthetic local fixtures and must not be presented as real employer outcomes.

[Back to all collections](../README.md)

## Author

**Tajamul Khan**

[GitHub](https://github.com/tajamulkhann) · [LinkedIn](https://www.linkedin.com/in/tajamulkhann/) · [Instagram](https://www.instagram.com/tajamul.codes/) · [Mentorship](https://topmate.io/tajamulkhan)

## Let's Connect

<div align="center">
<a href="https://www.linkedin.com/in/tajamulkhann/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a>
<a href="https://www.instagram.com/tajamul.codes/"><img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white"></a>
<a href="https://topmate.io/tajamulkhan"><img src="https://img.shields.io/badge/Topmate-FF0000?style=for-the-badge"></a>
<a href="https://www.whatsapp.com/channel/0029VaYs05jJkK7JKCesw42f"><img src="https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white"></a>
<a href="https://t.me/tajamul_khan"><img src="https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white"></a>
<a href="https://substack.com/@tajamulkhan"><img src="https://img.shields.io/badge/Substack-FF6719?style=for-the-badge&logo=substack&logoColor=white"></a>
<a href="https://www.kaggle.com/tajamulkhan"><img src="https://img.shields.io/badge/Kaggle-035a7d?style=for-the-badge&logo=kaggle&logoColor=white"></a>
<a href="https://github.com/tajamulkhann"><img src="https://img.shields.io/badge/GitHub-12100E?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="https://medium.com/@tajamulkhan"><img src="https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white"></a>
</div>

