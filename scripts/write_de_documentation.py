"""Refresh engineering READMEs from verified outputs and update collection index."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
specs=json.loads((R/'scripts/de_project_specs.json').read_text());connect=(R/'scripts/connect.md').read_text()
levels=['Intermediate','Beginner to intermediate','Intermediate','Advanced','Intermediate','Intermediate','Intermediate','Advanced','Advanced','Advanced']
skills=['Event time · deduplication · watermark · durable state','Pagination · retries · validation · idempotent upserts','Bronze/silver/gold · lineage · partitioning · version resolution','CDC · tombstones · stale events · atomic transactions','Surrogate keys · foreign keys · fact grain · unknown members','Content addressing · checksums · partitions · manifest publish','Data contracts · quarantine · release gate · audit','Batch/stream overlap · version convergence · conflict detection','SCD Type 2 · intervals · historical joins · boundary checks','Task dependencies · retries · rollback · checkpoints']
extra_notes={
0:'State grows with the number of logical event keys. The local consumer deliberately retains the full deduplication set; define a retention policy before scaling. The accepted and late tables plus seen keys and watermark share a transaction.',
1:'The retry example records the planned wait without actually sleeping. Invalid amount rows are excluded; duplicate order IDs overwrite with the same payload in this fixture. Production validation should cover every field and unexpected schema changes.',
2:'Bronze is copied byte-for-byte. The manifest records source lineage and row reconciliation, but does not turn CSV folders into a transactional lakehouse. Rebuilding reuses deterministic partition paths; this fixture has a fixed seven-day set.',
3:'A delete is retained as a tombstone with its source version. Dropping this state would allow an older update to re-create the row. The fixture uses stable source versions and does not model source-version resets.',
4:'Customer key zero is a deliberate unknown member, not a real customer. Product keys must resolve. Monetary measures are integer cents, so source-to-fact sums can be reconciled without floating-point rounding.',
5:'Content-addressed partitions and landing objects make replay safe for identical payloads. Different payloads for the same business date can create multiple snapshots; serving consumers must select the intended manifest snapshot rather than blindly glob all files.',
6:'Duplicate keys invalidate all duplicate rows. Rule failure totals can overlap, so rejected-row count is calculated with a row-wise OR. The fixture uses a 2% rejection ceiling; that threshold is a teaching choice, not a universal quality standard.',
7:'Highest-version state is deterministic only when versions define ordering and equal versions have identical payloads. An explicit error rejects equal-version conflicts. Tombstones prevent older batch data from restoring deleted keys.',
8:'Intervals are valid_from inclusive and valid_to exclusive. 9999-12-31 is a text sentinel for open-ended records. Complete history is rebuilt and sorted before assigning surrogate keys; this is not an incremental surrogate-key stability guarantee.',
9:'The SQLite target and completion checkpoint are committed together. The publish log describes that committed target; CSV exports are regenerated after the run and are not part of the transaction. Run identity hashes source bytes only; a production run key must also account for transformation/configuration versions.'}
for i,s in enumerate(specs):
 p=R/'data-engineering'/s['slug'];metrics=json.loads((p/'outputs/metrics.json').read_text());checks=json.loads((p/'outputs/checks.json').read_text());finding=(p/'outputs/finding.txt').read_text().strip()
 table='\n'.join(f'| {k} | {v:,.4f} |' for k,v in metrics.items());validation='\n'.join(f'| {k.replace("_"," ")} | {"Passed" if v else "Failed"} |' for k,v in checks.items())
 fixtures='\n'.join(f'- [`data/{f.name}`](data/{f.name})' for f in sorted((p/'data').iterdir()) if f.suffix in ['.csv','.json','.jsonl'])
 database=next((p/'outputs').glob('*.sqlite')).name
 p.joinpath('README.md').write_text(f'''# {s['title']}

{s['task']}

## Overview

{s['situation']} This {levels[i].lower()} case study implements a local Data Engineering pipeline with included fixtures, persistent output artifacts, SQL verification and a notebook with saved execution outputs.

**Author:** Tajamul Khan. **Data:** Original synthetic fixtures. **Runtime:** Python and SQLite on one machine.

## Problem statement

- **Task:** {s['task']}
- **Engineering skills:** {skills[i]}.
- **Success criterion:** Correct output plus passing failure, replay or integrity assertions, rather than an unmeasured throughput target.
- **Execution scope:** Runnable local implementation. Cloud/distributed platforms are extension targets and were not deployed for these results.

## STAR case study

### Situation

{s['situation']}

### Task

{s['task']}

### Action

{s['action']} The implementation records output metrics, runs explicit correctness checks and exports evidence for inspection.

### Result

{finding}

All {len(checks)} listed engineering checks passed on the included fixtures. These are verified local test outcomes, not evidence of production scale, cost savings or business impact.

## Architecture

```mermaid
{s['flow']}
```

The diagram is also available as [`architecture.mmd`](architecture.mmd).

## Dataset

**Source:** Original synthetic data generated by [`generate_data.py`](generate_data.py), seed `{202700+i}`. No live API or external dataset is required. Included datasets are CC0-1.0; code and documentation are MIT licensed.

{s['grain']}

{fixtures}

See [`data/README.md`](data/README.md) for field types, sample values and deliberate edge cases. Fixtures describe a fictional 2025 scenario.

## Project workflow

1. Inspect source fixtures, grain and SHA-256 hashes in the notebook.
2. Run the pipeline implementation from a fresh local demonstration state.
3. Exercise the documented failure, replay or integrity scenarios.
4. Query the generated SQLite artifact using checked-in SQL.
5. Reconcile SQL counts with the pipeline evidence.
6. Export tables, charts, a validation report and an offline operational dashboard.

## Engineering decisions

{extra_notes[i]}

## Executed correctness checks

{s['checks']}

| Check | Result |
|---|---|
{validation}

The assertions run inside the pipeline and notebook. A failed assertion stops execution. [`outputs/checks.json`](outputs/checks.json) and [`outputs/validation_results.csv`](outputs/validation_results.csv) contain the recorded results.

## Verified results

| Metric | Executed value |
|---|---:|
{table}

![Pipeline output](outputs/overview.png)

![Correctness checks](outputs/validation.png)

## Files and outputs

| File | Purpose |
|---|---|
| [`pipeline.ipynb`](pipeline.ipynb) | Full implementation, executed code, rendered tables and two saved charts |
| [`pipeline.py`](pipeline.py) | Standalone pipeline implementation with assertions |
| [`generate_data.py`](generate_data.py) | Reproducible fixture generator |
| [`verification.sql`](verification.sql) | SQLite query over generated artifacts |
| [`outputs/{database}`](outputs/{database}) | Inspectable local database created by the pipeline |
| [`outputs/summary.csv`](outputs/summary.csv) | Pipeline output summary |
| [`outputs/sql_results.csv`](outputs/sql_results.csv) | Saved SQL verification output |
| [`outputs/metrics.json`](outputs/metrics.json) | Machine-readable run metrics |
| [`outputs/finding.txt`](outputs/finding.txt) | Measured result and interpretation |
| [`outputs/dashboard.html`](outputs/dashboard.html) | Offline operational dashboard |

Additional per-project artifacts include state tables, quarantines, manifests, partitioned files or task logs as applicable. See the `outputs/` directory.

## How to run

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
cd data-engineering/{s['slug']}
python -m jupyterlab pipeline.ipynb
```

Run notebook cells from top to bottom. The code cell contains the implementation itself, not just a call to an invisible package.

To rebuild pipeline tables and verification evidence without opening Jupyter:

```bash
python pipeline.py
```

The script rebuilds local demonstration state. It exercises replay/recovery internally; it is not a long-running production daemon. Execute the notebook to also regenerate charts and the HTML dashboard.

To regenerate source data:

```bash
python generate_data.py
```

To execute all ten engineering notebooks and verify their saved outputs, from the repository root:

```bash
python scripts/execute_all.py data-engineering
python scripts/verify_data_engineering.py
```

## Inspect the dashboard

Download or clone the repository and open `outputs/dashboard.html` in a browser. It is a self-contained HTML file with no external JavaScript or paid service dependency. Cards and charts are a completed-run snapshot. The filter searches summary rows only and does not recompute metrics.

GitHub renders notebook outputs but does not execute HTML dashboards in the file browser. This project does not include a PBIX or Tableau workbook.

## Operating runbook

- **Before a run:** Use the included fixtures or review the contract before replacing them. Back up any outputs you want to keep; these examples deliberately rebuild local demonstration state.
- **If an assertion fails:** Inspect the source, `verification.sql` and the failed rule. Correct the cause before rerunning; do not remove an integrity check to make the run appear successful.
- **Recovery scenario:** {s['checks']}
- **After a successful run:** Compare `metrics.json`, the SQL output and the validation report. Keep all outputs with the source version used to create them.
- **Before production:** {s['extension']}

## Limitations

{s['limits']}

No real infrastructure deployment, throughput benchmark, latency SLA or dollar savings is claimed. The included failure probes validate the stated local contracts only.

## Career and interview preparation

### Resume bullet

“Built a {s['title'].lower()} portfolio project using Python and SQLite, implemented {len(checks)} verified correctness checks and documented reproducible output evidence.”

Use only after reproducing the work and understanding the design. Replace generic wording with the specific engineering contract you can explain; describe the synthetic/local scope honestly.

### 60-second STAR answer

“In this simulated scenario, {s['situation'][0].lower()+s['situation'][1:]} My task was to {s['task'][0].lower()+s['task'][1:]} I implemented the pipeline and exercised its failure and integrity boundaries. {finding} The next production step would be to {s['extension'][0].lower()+s['extension'][1:]}”

### Questions to prepare

- What is the source grain and which key defines a duplicate or version?
- Which state survives a restart and when is it committed?
- Which failure does the test inject and what invariant must remain true?
- What changes when the source is live, data arrives late or two workers run concurrently?
- What exactly was measured here and what would require a production benchmark?

## Technologies

Python, Pandas, NumPy, SQLite, Matplotlib, IPython/Jupyter and offline HTML. Architecture diagrams use Mermaid.

{connect}
''')
rows='\n'.join(f"| {i+1} | [{s['title']}]({s['slug']}/) | {levels[i]} | {skills[i]} |" for i,s in enumerate(specs))
(R/'data-engineering/README.md').write_text(f'''# Top 10 Data Engineering Projects

Ten original, runnable engineering case studies by **Tajamul Khan**. Each includes synthetic source fixtures, a full Python pipeline, SQL verification, an executed notebook, architecture diagram, STAR README, operational runbook and offline dashboard.

These projects focus on moving, validating, modelling and recovering data. They use local Python/SQLite implementations so they can be reproduced immediately. Kafka, Spark, Delta Lake, Airflow and cloud services are documented extension targets, not claimed deployments.

| # | Project | Level | Core skills |
|---|---|---|---|
{rows}

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

{connect}
''')
p=R/'README.md';t=p.read_text()
t=t.replace('Start with **10 complete Data Analyst projects**. Each combines a business problem, an included dataset, reproducible code, saved notebook outputs, a dashboard and a STAR case study. Other collections are planned and clearly labelled.','Explore **20 complete projects: 10 Data Analyst projects and 10 Data Engineering projects**. Each includes a business problem, data, reproducible code, saved notebook outputs, an offline dashboard and a STAR case study. Other collections are planned and clearly labelled.')
t=t.replace('| Top 10 Data Engineering Projects | Planned |','| Top 10 Data Engineering Projects | Available: 10 complete projects |')
section='## Explore Data Engineering\n\n| # | Project | Level | Core skills |\n|---|---|---|---|\n'+rows.replace('](','](data-engineering/')+'\n\nThe engineering projects test replay safety, data quality, history modelling and recovery using local Python/SQLite implementations. Distributed/cloud tools are extension targets.\n\n'
if '## Explore Data Engineering' not in t:t=t.replace('## What each completed project includes',section+'## What each completed project includes')
t=t.replace('python scripts/execute_all.py\npython scripts/verify_collection.py','python scripts/execute_all.py\npython scripts/verify_collection.py\npython scripts/execute_all.py data-engineering\npython scripts/verify_data_engineering.py')
t=t.replace('for the execution record and','for the Analytics execution record, [`data-engineering/execution_report.json`](data-engineering/execution_report.json) for Engineering and')
t=t.replace('Regenerate a project\'s dataset with its `generate_data.py`.','Regenerate a project\'s dataset with its `generate_data.py`. Engineering maintainers can run `scripts/build_data_engineering.py`, execute the Engineering notebooks and then run `scripts/write_de_documentation.py`.')
p.write_text(t)
(R/'REPOSITORY_DESCRIPTION.txt').write_text('20 complete portfolio projects across Data Analytics and Data Engineering, with datasets, executed notebooks, Python, SQL, dashboards and STAR case studies. ML, Deep Learning, Generative AI and Agentic AI collections planned.\n')
print('Updated ten STAR READMEs and the main collection index')
