# Top 10 Data & AI Projects

### Build projects you can run, explain and discuss in an interview.

A career-focused collection by **Tajamul Khan** covering Data Analytics, Data Engineering, Machine Learning, Deep Learning, Generative AI and Agentic AI.

Explore **20 complete projects: 10 Data Analyst projects and 10 Data Engineering projects**. Each includes a business problem, data, reproducible code, saved notebook outputs, an offline dashboard and a STAR case study. Other collections are planned and clearly labelled.

## Explore the collections

| Folder | Collection | Status |
|---|---|---|
| [`data-analytics/`](data-analytics/) | Top 10 Data Analyst Projects | Available: 10 complete projects |
| [`data-engineering/`](data-engineering/) | Top 10 Data Engineering Projects | Available: 10 complete projects |
| [`machine-learning/`](machine-learning/) | Top 10 Machine Learning Projects | Planned |
| [`deep-learning/`](deep-learning/) | Top 10 Deep Learning Projects | Planned |
| [`generative-ai/`](generative-ai/) | Top 10 Generative AI Projects | Planned |
| [`agentic-ai/`](agentic-ai/) | Top 10 Agentic AI Projects | Planned |

## Start here: Data Analytics

| # | Project | Level | Skills |
|---|---|---|---|
| 1 | [Retail Sales and Profitability](data-analytics/01-retail-sales-profitability/) | Beginner | Data cleaning · weighted margins · monthly trends |
| 2 | [Customer RFM Segmentation](data-analytics/02-customer-rfm-segmentation/) | Intermediate | RFM · business segmentation · concentration |
| 3 | [Subscription Churn and Cohort Retention](data-analytics/03-subscription-churn-cohorts/) | Intermediate | Cohorts · retention · denominator design |
| 4 | [Marketing Channel Performance](data-analytics/04-marketing-channel-performance/) | Beginner | Attribution · CAC · ROAS · weighted rates |
| 5 | [E-commerce Funnel and Device Friction](data-analytics/05-ecommerce-funnel/) | Intermediate | Funnels · conditional conversion · device analysis |
| 6 | [Supply Chain Delivery and Inventory Risk](data-analytics/06-supply-chain-delivery/) | Intermediate | OTIF · fill rate · inventory coverage |
| 7 | [Workforce Attrition and Department Trends](data-analytics/07-workforce-attrition/) | Beginner | Workforce denominators · aggregation · ethics |
| 8 | [Financial Performance and Budget Variance](data-analytics/08-finance-budget-variance/) | Intermediate | Variance analysis · reconciliation · financial KPIs |
| 9 | [A/B Test of Checkout Conversion](data-analytics/09-ab-test-checkout/) | Advanced | Hypothesis tests · confidence intervals · SRM |
| 10 | [Customer Support SLA and Backlog](data-analytics/10-support-sla-analytics/) | Advanced | SLA logic · missing outcomes · backlog aging |

## Explore Data Engineering

| # | Project | Level | Core skills |
|---|---|---|---|
| 1 | [Streaming Event Pipeline with Replay Safety](data-engineering/01-streaming-event-pipeline/) | Intermediate | Event time · deduplication · watermark · durable state |
| 2 | [Paginated API to Warehouse ETL](data-engineering/02-api-to-warehouse-etl/) | Beginner to intermediate | Pagination · retries · validation · idempotent upserts |
| 3 | [Bronze Silver Gold Data Pipeline](data-engineering/03-medallion-lakehouse/) | Intermediate | Bronze/silver/gold · lineage · partitioning · version resolution |
| 4 | [Change Data Capture Replication](data-engineering/04-cdc-replication/) | Advanced | CDC · tombstones · stale events · atomic transactions |
| 5 | [Dimensional Warehouse with Referential Integrity](data-engineering/05-dimensional-warehouse/) | Intermediate | Surrogate keys · foreign keys · fact grain · unknown members |
| 6 | [API Snapshot Ingestion to Partitioned Storage](data-engineering/06-api-object-storage/) | Intermediate | Content addressing · checksums · partitions · manifest publish |
| 7 | [Data Quality Gate with Quarantine and Audit](data-engineering/07-data-quality-gate/) | Intermediate | Data contracts · quarantine · release gate · audit |
| 8 | [Batch and Stream Reconciliation Pipeline](data-engineering/08-batch-stream-unification/) | Advanced | Batch/stream overlap · version convergence · conflict detection |
| 9 | [SCD Type 2 Customer History](data-engineering/09-scd-type-two/) | Advanced | SCD Type 2 · intervals · historical joins · boundary checks |
| 10 | [Pipeline Orchestration with Retry and Recovery](data-engineering/10-orchestration-recovery/) | Advanced | Task dependencies · retries · rollback · checkpoints |

The engineering projects test replay safety, data quality, history modelling and recovery using local Python/SQLite implementations. Distributed/cloud tools are extension targets.

## What each completed project includes

- A business question and a detailed Situation, Task, Action and Result narrative.
- An included synthetic dataset, field dictionary, license and deterministic generator.
- Python and SQL with validation and aggregate reconciliation.
- A notebook with real execution outputs, result tables and a chart.
- An offline HTML dashboard, CSV exports and machine-readable KPIs.
- Reproduction instructions, limitations, next steps and interview prompts.

## Quick start

Download this repository as a ZIP and extract it, or clone it after it is published. From its root:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd data-analytics/01-retail-sales-profitability
python -m jupyterlab analysis.ipynb
```

Run cells from top to bottom. No database server, paid software or external data connection is required. Open a project's `outputs/dashboard.html` directly in a browser to view its offline dashboard.

## Reproducibility

```bash
# From the repository root
python scripts/execute_all.py
python scripts/verify_collection.py
python scripts/execute_all.py data-engineering
python scripts/verify_data_engineering.py
python scripts/execute_all.py data-engineering
python scripts/verify_data_engineering.py
```

Execution uses one isolated Python subprocess and an in-process IPython shell per notebook, storing actual stdout, rendered tables and PNG chart outputs. See [`execution_report.json`](execution_report.json) for the Analytics execution record, [`data-engineering/execution_report.json`](data-engineering/execution_report.json) for Engineering and [`requirements-lock.txt`](requirements-lock.txt) for tested package versions.

Regenerate a project's dataset with its `generate_data.py`. Engineering maintainers can run `scripts/build_data_engineering.py`, execute the Engineering notebooks and then run `scripts/write_de_documentation.py`. Engineering maintainers can run `scripts/build_data_engineering.py`, execute the Engineering notebooks and then run `scripts/write_de_documentation.py`. Advanced maintainers can rebuild all generated sources with `scripts/build_collection.py`, then run `execute_all.py` and `write_documentation.py` in that order. Rebuilding clears saved notebook outputs until execution completes.

## Use these projects for your career

1. Reproduce the analysis and explain the data grain and KPI formulas.
2. Investigate a new question and compare the result with the original finding.
3. Add a justified visualization or validate against appropriately licensed real data.
4. Write your own STAR narrative using measured results.
5. Cite this collection and accurately describe your contribution.

The datasets are original simulations. Do not present their findings as actual company outcomes or claim revenue, retention or efficiency improvements that were not measured. “Top 10” describes a curated teaching collection, not a research ranking.

## Data and code licensing

Original project code and documentation: [MIT](LICENSE). Included synthetic datasets: [CC0-1.0](DATA_LICENSE.md). Future external datasets retain their own terms. No third-party repository code or uploaded reference images are redistributed.

## Acknowledgements

Business-area inspiration came from the supplied “Top 8 Data analytics project examples” image collection. Implementation and simulated data were written independently. README structure follows [Tajamul Khan's Machine Learning Projects](https://github.com/tajamulkhann/Machine-Learning-Projects). Repository URLs inside the screenshots were not reliably legible and are not treated as verified code sources.

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

