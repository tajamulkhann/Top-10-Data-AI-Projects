"""Verify deliverable contracts, notebook execution and local Markdown links."""
from pathlib import Path
import json,re
from urllib.parse import unquote
import nbformat
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
projects=sorted((ROOT/'data-analytics').glob('*/analysis.ipynb'))
assert len(projects)==10
outputs=0
for path in projects:
    p=path.parent;nb=nbformat.read(path,as_version=4);nbformat.validate(nb)
    for f in ['README.md','analysis.py','analysis.sql','generate_data.py','data/raw.csv','data/README.md','outputs/metrics.json','outputs/summary.csv','outputs/detail.csv','outputs/sql_results.csv','outputs/dashboard.html','outputs/overview.png','outputs/detail.png']:
        assert (p/f).is_file(),(p,f)
    codes=[c for c in nb.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in codes),p
    assert all(o.output_type!='error' for c in codes for o in c.outputs),p
    images=[o for c in codes for o in c.outputs if 'image/png' in o.get('data',{})]
    assert len(images)>=2,p
    stdout=''.join(o.get('text','') for c in codes for o in c.outputs)
    assert 'SQL / Python reconciliation passed' in stdout,p
    assert 'Synthetic teaching data' in (p/'outputs/dashboard.html').read_text()
    assert (p/'outputs/dashboard.html').read_text().count('data:image/png;base64,')==2
    assert len(pd.read_csv(p/'data/raw.csv'))>100
    outputs+=sum(len(c.outputs) for c in codes)
for md in ROOT.rglob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',md.read_text()):
        if target.startswith(('http:','https:','#','mailto:')):continue
        assert (md.parent/unquote(target.split('#')[0])).exists(),(md,target)
print(json.dumps({'projects':len(projects),'executed_code_cells':sum(sum(c.cell_type=='code' for c in nbformat.read(p,as_version=4).cells) for p in projects),'saved_outputs':outputs,'embedded_charts':20,'local_markdown_links':'passed'},indent=2))
