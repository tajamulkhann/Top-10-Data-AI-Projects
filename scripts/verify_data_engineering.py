"""Verify saved execution evidence, repeatability and artifact integrity."""
from pathlib import Path
import json,re,tempfile,importlib.util
from urllib.parse import unquote
import pandas as pd
import nbformat
R=Path(__file__).resolve().parents[1]
projects=sorted((R/'data-engineering').glob('*/pipeline.ipynb'));assert len(projects)==10
count=0;cells=0;outputs=0
for nbpath in projects:
 p=nbpath.parent;nb=nbformat.read(nbpath,as_version=4);nbformat.validate(nb)
 code=[c for c in nb.cells if c.cell_type=='code'];assert all(c.execution_count is not None for c in code)
 assert not any(o.output_type=='error' for c in code for o in c.outputs)
 assert sum('image/png' in o.get('data',{}) for c in code for o in c.outputs)==2
 assert any('SQL result reconciled' in o.get('text','') for c in code for o in c.outputs)
 recorded=json.loads((p/'outputs/checks.json').read_text());assert all(recorded.values())
 # Independent script run in a clean temporary directory must reproduce recorded results.
 spec=importlib.util.spec_from_file_location('pipeline_test',p/'pipeline.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 with tempfile.TemporaryDirectory() as tmp:
  result=module.run(Path(tmp))
  assert result['metrics']==json.loads((p/'outputs/metrics.json').read_text()),p
  assert result['checks']==recorded,p
  pd.testing.assert_frame_equal(result['summary'].reset_index(drop=True),pd.read_csv(p/'outputs/summary.csv'),check_dtype=False)
 count+=len(recorded);cells+=len(code);outputs+=sum(len(c.outputs) for c in code)
 for file in ['pipeline.py','generate_data.py','architecture.mmd','verification.sql','README.md','data/README.md','outputs/dashboard.html']:
  assert (p/file).exists(),(p,file)
 for doc in [p/'README.md',p/'data/README.md']:
  for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
   if link.startswith(('https:','http:','#')):continue
   assert (doc.parent/unquote(link.split('#')[0])).exists(),(doc,link)
for doc in [R/'README.md',R/'data-engineering/README.md']:
 for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
  if link.startswith(('https:','http:','#')):continue
  assert (doc.parent/unquote(link.split('#')[0])).exists(),(doc,link)
print(json.dumps({'projects':10,'engineering_checks':count,'executed_cells':cells,'saved_outputs':outputs,'charts':20,'independent_reexecution':'passed','local_links':'passed'},indent=2))
