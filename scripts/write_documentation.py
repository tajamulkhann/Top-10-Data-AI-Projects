from pathlib import Path
import json,importlib.metadata
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
specs=json.loads((ROOT/'scripts/project_specs.json').read_text());connect=(ROOT/'scripts/connect.md').read_text()
levels=['Beginner','Intermediate','Intermediate','Beginner','Intermediate','Intermediate','Beginner','Intermediate','Advanced','Advanced']
skills=['Data cleaning · weighted margins · monthly trends','RFM · business segmentation · concentration','Cohorts · retention · denominator design','Attribution · CAC · ROAS · weighted rates','Funnels · conditional conversion · device analysis','OTIF · fill rate · inventory coverage','Workforce denominators · aggregation · ethics','Variance analysis · reconciliation · financial KPIs','Hypothesis tests · confidence intervals · SRM','SLA logic · missing outcomes · backlog aging']
for i,s in enumerate(specs):
 p=ROOT/'data-analytics'/s['slug'];metrics=json.loads((p/'outputs/metrics.json').read_text());summary=pd.read_csv(p/'outputs/summary.csv')
 results='\n'.join(f'| {k} | {v:,.4f} |' for k,v in metrics.items())
 values='; '.join(f'{k}: {v:,.4f}' for k,v in metrics.items())
 # Describe evidence rather than asserting business uplift.
 result_story=f'The executed analysis produced {values}. The notebook also exports a group-level summary and an SQL reconciliation. These are measured analytical outputs from synthetic data; no operational improvement has been demonstrated.'
 next_action=s['extension']
 finding=(p/'outputs/recommendation.txt').read_text().replace('\\n','').strip()
 readme=f'''# {s['title']}

{s['question']}

## Overview

{s['situation']} This {levels[i].lower()} portfolio case study contains an original dataset, executable Python and SQL, a notebook with saved outputs and an offline dashboard. It is designed for learning, portfolio development and interview practice.

**Data status:** Synthetic. **Observation period:** Fictional 2025. **Author:** Tajamul Khan.

## Problem statement

- **Business question:** {s['question']}
- **Task:** {s['task']}
- **Skills demonstrated:** {skills[i]}.
- **Decision supported:** Prioritize an investigation or controlled test using reproducible evidence.

## STAR case study

### Situation
{s['situation']}

### Task
{s['task']}

### Action
{s['action']} The workflow includes source profiling, explicit metric definitions, Python calculations, SQL checks and a documented handoff.

### Result
{result_story}

## Dataset

- **Availability:** Included at [`data/raw.csv`](data/raw.csv).
- **Source:** Original simulation in [`generate_data.py`](generate_data.py), seed `{202600+i}`.
- **Dictionary and grain:** [`data/README.md`](data/README.md).
- **License:** Included synthetic data is CC0-1.0; code is MIT licensed.
- No external data download, credentials or personal records are required.
- Simulated relationships are teaching assumptions, not facts about an industry.

## KPI definitions and analytical decisions

{s['definitions']}

{s['action']}

## Project workflow

1. Read the source and inspect its grain, missing values and duplicates.
2. Validate the data contract and handle fields according to their business meaning.
3. Calculate the defined metrics and segment-level summaries.
4. Run SQLite aggregation and reconcile shared measures against Python.
5. Generate the chart, CSV exports and standalone HTML dashboard.
6. Interpret the evidence, document limits and propose a next validation step.

## Verified results

The notebook was executed against the included dataset with an isolated in-process IPython session. Tables, printed checks and chart outputs remain embedded in the notebook.

| Metric | Executed value |
|---|---:|
{results}

These values describe this synthetic dataset and dependency environment. They are a reproducibility record, not a production benchmark or a causal effect unless explicitly defined in the randomized experiment.

![Analysis overview](outputs/overview.png)

## Evidence-based recommendation

{finding}

![Supporting analysis](outputs/detail.png)

The notebook contains the supporting breakdown in `outputs/detail.csv`. This recommendation is an investigation or validation step, not a claim of achieved impact.

## Dashboard and output files

Download or clone the project and open [`outputs/dashboard.html`](outputs/dashboard.html) in a browser. It works offline and provides KPI cards, a chart and a searchable summary table. The text filter only filters table rows; it does not recompute cards or charts. GitHub's file view does not execute HTML dashboards.

| File | Purpose |
|---|---|
| [`analysis.ipynb`](analysis.ipynb) | Narrative analysis with executed code, tables and chart |
| [`analysis.py`](analysis.py) | Script companion with the same analysis code |
| [`analysis.sql`](analysis.sql) | SQLite aggregation over validated `facts` |
| [`outputs/metrics.json`](outputs/metrics.json) | Machine-readable verified KPIs |
| [`outputs/summary.csv`](outputs/summary.csv) | Group-level analysis for Excel or BI tools |
| [`outputs/analysis_ready.csv`](outputs/analysis_ready.csv) | Validated analysis facts |
| [`outputs/sql_results.csv`](outputs/sql_results.csv) | SQL query results |
| [`outputs/data_quality.csv`](outputs/data_quality.csv) | Source profiling evidence |

## How to run

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
cd data-analytics/{s['slug']}
python -m jupyterlab analysis.ipynb
```

Run notebook cells from top to bottom. To execute as a script from the project directory:

```bash
python analysis.py
```

To rebuild the original dataset:

```bash
python generate_data.py
```

From the repository root, execute all notebooks and save their real outputs:

```bash
python scripts/execute_all.py
```

## Power BI / Tableau extension

Import `outputs/analysis_ready.csv` and `outputs/summary.csv`. Rebuild the specified measures with ratio-of-sums where relevant, add segment filters and reconcile the unfiltered totals to `outputs/metrics.json`. This package includes an HTML dashboard, not a PBIX or Tableau workbook.

## Limitations

{s['limit']}

## Recommended next step

{next_action}

## Interview preparation

- What decision does this analysis support and what is the unit of analysis?
- Why did you choose this denominator and how could another denominator mislead?
- What did the data checks and SQL reconciliation establish?
- Which finding would you investigate first and what evidence would change your recommendation?
- What does this dataset prevent you from concluding?

### Resume bullet template

“Built a reproducible {s['title'].lower()} portfolio case study using Python and SQL, validated business metrics and delivered an offline dashboard with documented findings and limitations.”

Use this only after completing and understanding the project. Add a verified analysis metric if useful; do not describe simulated results as employer impact or claim an unmeasured percentage improvement.

### 60-second STAR answer

“In this simulated case study, {s['situation'][0].lower()+s['situation'][1:]} My task was to {s['task'][0].lower()+s['task'][1:]} I used Python and SQL to validate the source, calculate defined metrics and communicate the results through a dashboard. The resulting metrics are recorded above. I would next {s['extension'][0].lower()+s['extension'][1:]}”

## Technologies

Python, Pandas, NumPy, SQLite, Matplotlib, Jupyter and HTML. The A/B testing project additionally uses SciPy.

{connect}
'''
 (p/'README.md').write_text(readme)
rows='\n'.join(f"| {i+1} | [{s['title']}]({s['slug']}/) | {levels[i]} | {skills[i]} |" for i,s in enumerate(specs))
(ROOT/'data-analytics/README.md').write_text(f'''# Top 10 Data Analyst Projects

Ten complete business case studies by **Tajamul Khan**. Each includes a synthetic CSV dataset, source dictionary, original analysis code, SQL, an executed notebook, exported results, an offline dashboard and a STAR-based README.

“Top 10” is the collection title: these are ten selected portfolio ideas, not an empirical ranking.

| # | Project | Level | Skills |
|---|---|---|---|
{rows}

## Suggested learning order

Start with retail, marketing and workforce reporting. Continue with finance, RFM, funnels, supply chain and retention. Finish with the experiment and support SLA projects, where uncertainty and incomplete outcomes require more care.

## Portfolio standard

Reproduce the notebook, explain every denominator, change at least one assumption and write your own recommendation. A convincing portfolio demonstrates independent reasoning and transparent limits. Synthetic datasets make these examples immediately runnable; extend them with appropriately licensed real data for additional experience.

[Return to main collection](../README.md)

{connect}
''')
collections=[('data-analytics','Top 10 Data Analyst Projects','Available: 10 complete projects'),('data-engineering','Top 10 Data Engineering Projects','Planned'),('machine-learning','Top 10 Machine Learning Projects','Planned'),('deep-learning','Top 10 Deep Learning Projects','Planned'),('generative-ai','Top 10 Generative AI Projects','Planned'),('agentic-ai','Top 10 Agentic AI Projects','Planned')]
for folder,title,status in collections[1:]:
 (ROOT/folder).mkdir(exist_ok=True)
 (ROOT/folder/'README.md').write_text(f'# {title}\n\n**Status: Planned.** This folder reserves the collection structure; no completed projects are included yet.\n\nFuture projects will include reproducible code, data provenance, executed evidence and STAR case studies.\n\n[Back to main repository](../README.md)\n')
description='Career-focused Data and AI projects with datasets, executed notebooks, SQL, dashboards and STAR case studies. Explore Data Analytics, Data Engineering, Machine Learning, Deep Learning, Generative AI and Agentic AI. Starting with 10 complete Data Analyst projects.'
(ROOT/'REPOSITORY_DESCRIPTION.txt').write_text(description+'\n')
table='\n'.join(f'| [`{folder}/`]({folder}/) | {title} | {status} |' for folder,title,status in collections)
(ROOT/'README.md').write_text(f'''# Top 10 Data & AI Projects

### Build projects you can run, explain and discuss in an interview.

A career-focused collection by **Tajamul Khan** covering Data Analytics, Data Engineering, Machine Learning, Deep Learning, Generative AI and Agentic AI.

Start with **10 complete Data Analyst projects**. Each combines a business problem, an included dataset, reproducible code, saved notebook outputs, a dashboard and a STAR case study. Other collections are planned and clearly labelled.

## Explore the collections

| Folder | Collection | Status |
|---|---|---|
{table}

## Start here: Data Analytics

{rows.replace('](','](data-analytics/')}

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
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
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
```

Execution uses one isolated Python subprocess and an in-process IPython shell per notebook, storing actual stdout, rendered tables and PNG chart outputs. See [`execution_report.json`](execution_report.json) for the execution record and [`requirements-lock.txt`](requirements-lock.txt) for tested package versions.

Regenerate a project's dataset with its `generate_data.py`. Advanced maintainers can rebuild all generated sources with `scripts/build_collection.py`, then run `execute_all.py` and `write_documentation.py` in that order. Rebuilding clears saved notebook outputs until execution completes.

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

{connect}
''')
# Insert missing header for projects table.
p=ROOT/'README.md';t=p.read_text().replace('## Start here: Data Analytics\n\n','## Start here: Data Analytics\n\n| # | Project | Level | Skills |\n|---|---|---|---|\n');p.write_text(t)
(ROOT/'requirements.txt').write_text('numpy>=1.24,<3\npandas>=2.0,<3\nmatplotlib>=3.7,<4\nscipy>=1.10,<2\nipython>=8,<10\nnbformat>=5.9,<6\njupyterlab>=4,<5\n')
packages=['numpy','pandas','matplotlib','scipy','ipython','nbformat']
(ROOT/'requirements-lock.txt').write_text('# Tested direct analysis/execution dependencies, Python 3.12.\n# JupyterLab is optional for interactive editing and is specified in requirements.txt.\n'+'\n'.join(f'{x}=={importlib.metadata.version(x)}' for x in packages)+'\n')
(ROOT/'.gitignore').write_text('.venv/\n__pycache__/\n.ipynb_checkpoints/\n.DS_Store\n*.pyc\n')
(ROOT/'DATA_LICENSE.md').write_text('# Synthetic dataset license\n\nAll generated CSV datasets in this collection are dedicated to the public domain under CC0 1.0 Universal: https://creativecommons.org/publicdomain/zero/1.0/\n\nThese are fictional teaching records, not actual customers, employees or financial accounts. No warranty is provided. Original code and documentation are covered by the separate MIT license.\n')
(ROOT/'LICENSE').write_text('''MIT License

Copyright (c) 2026 Tajamul Khan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''')
(ROOT/'LINKEDIN_POST.md').write_text('''A dashboard becomes a stronger portfolio project when you can explain the decision behind it.

Here are 10 Data Analyst projects to build and discuss in interviews:

1. Retail Sales and Profitability
Find where sales growth hides weak margins.

2. Customer RFM Segmentation
Identify valuable customers and groups that need attention.

3. Subscription Churn and Cohort Retention
Compare retention at the same customer age.

4. Marketing Channel Performance
Calculate CAC and ROAS with consistent denominators.

5. E-commerce Funnel Analysis
Locate the steps where sessions drop out.

6. Supply Chain Delivery and Inventory Risk
Track OTIF, fill rate and stock coverage.

7. Workforce Attrition
Measure employee exits with an explicit headcount denominator.

8. Financial Performance and Budget Variance
Explain the gap between planned and actual operating profit.

9. A/B Testing
Estimate conversion lift and show the uncertainty around it.

10. Customer Support SLA Analytics
Separate response delays from unresolved backlog.

I have put together a collection with datasets, Python, SQL, executed notebooks, offline dashboards and detailed STAR case studies.

The datasets are clearly labelled simulations so you can run every project immediately and understand how it works.

For each project, explain:
• Situation: What business problem are you investigating?
• Task: What question must you answer?
• Action: How did you validate and analyse the data?
• Result: What did you measure and what decision does it support?

Pick one. Reproduce it. Add your own question and recommendation.

Save this list for your next portfolio project.

#DataAnalytics #DataAnalyst #SQL #Python #PortfolioProjects
''')
(ROOT/'PUBLISHING.md').write_text('''# GitHub publishing checklist

Suggested repository: `Top-10-Data-AI-Projects` under `tajamulkhann`.

1. Create the repository and paste `REPOSITORY_DESCRIPTION.txt` into its description.
2. Upload the contents of this extracted folder so `README.md` is at repository root, not inside an extra wrapper directory.
3. Preserve the `outputs/` folders and executed `.ipynb` files.
4. Inspect the main README, collection links and one rendered notebook.
5. Add your actual published repository URL to the LinkedIn post before posting.

This package does not establish that the GitHub repository has been created or uploaded. GitHub shows notebook outputs but does not run HTML dashboards in the file browser; download those to open locally.
''')
print('Wrote project documentation, root README and launch post')
