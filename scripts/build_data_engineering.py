"""Rebuild the local engineering collection. Execute notebooks afterward."""
from pathlib import Path
import json,textwrap,uuid
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]
specs=json.loads((R/'scripts/de_project_specs.json').read_text())
HEADER='''from pathlib import Path
import json, sqlite3, hashlib, shutil, os
import numpy as np
import pandas as pd
DATA = Path(__file__).resolve().parent / 'data'
def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
'''
finish='''
    checks={k:bool(v) for k,v in checks.items()}
    assert all(checks.values()),checks
    metrics={k:float(v) for k,v in metrics.items()}
    summary.to_csv(out/'summary.csv',index=False)
    pd.DataFrame({'check':list(checks),'passed':list(checks.values())}).to_csv(out/'validation_results.csv',index=False)
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    (out/'checks.json').write_text(json.dumps(checks,indent=2))
    (out/'finding.txt').write_text(finding+'\\n')
    # Execute the checked-in SQL against the generated SQLite artifact.
    db_files=list(out.glob('*.sqlite'))
    assert len(db_files)==1
    with sqlite3.connect(db_files[0]) as con:
        sql_result=pd.read_sql_query((DATA.parent/'verification.sql').read_text(),con)
    sql_result.to_csv(out/'sql_results.csv',index=False)
    return {'metrics':metrics,'checks':checks,'summary':summary,'chart':chart,'finding':finding,'sql_result':sql_result}
'''
def md(s):return {'cell_type':'markdown','id':uuid.uuid4().hex[:8],'metadata':{},'source':s}
def code(s):return {'cell_type':'code','id':uuid.uuid4().hex[:8],'metadata':{},'execution_count':None,'outputs':[],'source':s}
for i,s in enumerate(specs):
 p=R/'data-engineering'/s['slug'];(p/'data').mkdir(parents=True,exist_ok=True);(p/'outputs').mkdir(exist_ok=True)
 gen=f'''from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng({202700+i})
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\\n'.join(json.dumps(r) for r in rows)+'\\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
'''+s['generator']+'\n'
 (p/'generate_data.py').write_text(gen);exec(compile(gen,str(p/'generate_data.py'),'exec'),{'__file__':str((p/'generate_data.py').resolve())})
 pipeline=HEADER+'\ndef run(out):\n    """Build one deterministic demonstration, including failure/replay checks."""\n    out=Path(out);out.mkdir(parents=True,exist_ok=True)\n'+textwrap.indent(s['body'],'    ')+'\n'+finish
 (p/'pipeline.py').write_text(pipeline+"\nif __name__=='__main__':\n    result=run(Path(__file__).resolve().parent/'outputs')\n    print(json.dumps(result['metrics'],indent=2))\n    print(result['finding'])\n")
 (p/'verification.sql').write_text('-- SQLite query over the generated artifact.\n'+s['sql']+'\n')
 (p/'architecture.mmd').write_text(s['flow']+'\n')
 setup='''from pathlib import Path
import json, sqlite3, hashlib, shutil, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
BASE=Path.cwd()
DATA=BASE/'data'
OUT=BASE/'outputs'
assert DATA.exists(), 'Run from this project directory'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'figure.dpi':120,'axes.spines.top':False,'axes.spines.right':False})
print('Included source fixtures:')
display(pd.DataFrame([{'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(DATA.iterdir()) if f.suffix in ['.csv','.json','.jsonl']]))
'''
 source=pipeline.replace("DATA = Path(__file__).resolve().parent / 'data'","DATA = BASE / 'data'")
 execute='''result=run(OUT)
display(pd.Series(result['metrics'],name='value').to_frame())
display(result['summary'])
print(result['finding'])
'''
 validate='''validation=pd.DataFrame({'check':list(result['checks']),'passed':list(result['checks'].values())})
display(validation)
assert validation.passed.all()
print(f"Verified {len(validation)} engineering checks")
display(result['sql_result'])
'''
 # SQL conservation check tailored to each schema.
 reconcile={0:"assert int(result['sql_result'].events.sum())==int(result['metrics']['Accepted logical events'])",1:"assert int(result['sql_result'].orders.sum())==int(result['metrics']['Warehouse orders'])",2:"assert int(result['sql_result'].orders.sum())==int(result['metrics']['Silver orders'])",3:"assert int(result['sql_result']['keys'].sum())==int(result['metrics']['Live replica rows']+result['metrics']['Tombstones'])",4:"assert int(result['sql_result'].orders.sum())==int(result['metrics']['Fact rows'])",5:"assert int(result['sql_result'].rows.sum())==int(result['metrics']['Snapshot records'])",6:"assert result['sql_result'].iloc[0].to_dict()==result['summary'].set_index('rule').failures.to_dict()",7:"assert int(result['sql_result']['keys'].sum())==int(result['metrics']['Logical keys'])",8:"assert int(result['sql_result'].versions.sum())==int(result['metrics']['Dimension versions'])",9:"assert int(result['sql_result'].rows.sum())==int(result['metrics']['Published rows'])"}[i]
 validate+='\n'+reconcile+"\nprint('SQL result reconciled against Python pipeline evidence')\n"
 charts=f'''fig,ax=plt.subplots(figsize=(10,4.8))
result['chart'].plot.bar(ax=ax,color='#246577',rot=30)
ax.set_title({s['title']!r},loc='left',fontweight='bold')
ax.set_ylabel('Record / event count')
fig.tight_layout();fig.savefig(OUT/'overview.png',bbox_inches='tight');plt.show()
fig,ax=plt.subplots(figsize=(10,3.8))
labels=[x.replace('_',' ') for x in result['checks']]
ax.barh(labels,[int(x) for x in result['checks'].values()],color='#3b7a57')
ax.set_xlim(0,1.2);ax.set_xticks([0,1],['Failed','Passed']);ax.set_title('Executed correctness checks',loc='left',fontweight='bold')
fig.tight_layout();fig.savefig(OUT/'validation.png',bbox_inches='tight');plt.show()
'''
 dashboard='''import html,base64
cards=''.join('<article><span>'+html.escape(k)+'</span><strong>'+f'{v:,.2f}'+'</strong></article>' for k,v in result['metrics'].items())
images=''.join('<img alt="'+name+'" src="data:image/png;base64,'+base64.b64encode((OUT/name).read_bytes()).decode()+'">' for name in ['overview.png','validation.png'])
page='''+repr('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TITLE</title><style>body{font:16px system-ui;background:#f4f6f7;color:#19323f;margin:0}main{max-width:1100px;margin:auto;padding:32px}header{border-bottom:3px solid #246577;margin-bottom:24px}.cards{display:flex;flex-wrap:wrap;gap:12px}article{background:white;border:1px solid #d7e0e5;padding:18px;flex:1;min-width:175px}strong{display:block;font-size:28px;margin-top:10px}img{max-width:100%;margin:20px 0}table{border-collapse:collapse;width:100%;background:white;font-size:14px}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:right}.scroll{overflow:auto}input{padding:12px;margin:14px 0}footer{margin-top:30px}</style><main><header><small>TAJAMUL KHAN · DATA ENGINEERING</small><h1>TITLE</h1><p>Local executable pipeline · Synthetic source fixtures</p></header>'''.replace('TITLE',s['title']))+'''+ '<section class="cards">'+cards+'</section><h2>Run finding</h2><p>'+html.escape(result['finding'])+'</p>'+images+'<h2>Inspect pipeline output</h2><label for="filter">Filter summary rows</label><br><input id="filter" placeholder="Search summary"><div class="scroll">'+result['summary'].to_html(index=False,border=0)+'</div><h2>Validation evidence</h2><div class="scroll">'+validation.to_html(index=False,border=0)+'</div><p>LIMITS</p><footer>Instagram @tajamul.codes · linkedin.com/in/tajamulkhann/</footer></main><script>document.getElementById("filter").addEventListener("input",function(){document.querySelectorAll("table:first-of-type tbody tr").forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(this.value.toLowerCase()))});</script></html>'
(OUT/'dashboard.html').write_text(page)
print('Saved offline dashboard with pipeline metrics, output table and validation evidence.')
'''.replace('LIMITS',s['limits'])
 # Scope row filter only to the summary table, keeping validation evidence visible.
 dashboard=dashboard.replace('table:first-of-type tbody tr','.scroll:first-of-type tbody tr')
 cells=[md(f"# {s['title']}\n\n**Tajamul Khan**\n\n{s['situation']}\n\n**Task:** {s['task']}\n\nThis notebook executes original local code on included synthetic data. It does not connect to a live cloud platform."),md('## Source contract\n\n'+s['grain']+'\n\nSee `data/README.md` for provenance, field definitions and intentional edge cases.'),code(setup),md('## Pipeline implementation\n\n'+s['action']+'\n\nThe following cell contains the full pipeline implementation, also available in `pipeline.py`.'),code(source),md('## Execute the pipeline\n\nThe run uses a fresh demonstration state and exercises recovery or correctness checks internally. Running the notebook again rebuilds the same evidence; individual SQLite tables are local to this project.'),code(execute),md('## Failure, replay and integrity checks\n\n'+s['checks']+'\n\nThe SQL query is read from `verification.sql` and executed against the saved SQLite database.'),code(validate),md('## Pipeline observability'),code(charts),md('## Offline operational dashboard\n\nCards and charts show the completed run. The search box filters summary rows only; it does not recompute metrics.'),code(dashboard),md('## Limits and production extension\n\n'+s['limits']+'\n\n**Next step:** '+s['extension']+'\n\n## Career discussion\n\nExplain the grain, key, state, failure boundary and replay contract. Use the measured result above in your STAR story. Do not describe a local fixture exercise as a production deployment or claim unmeasured throughput/cost savings.')]
 (p/'pipeline.ipynb').write_text(json.dumps({'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'nbformat':4,'nbformat_minor':5},indent=1))
 data_lines=['# Dataset contract','', '**Source:** Original synthetic fixtures generated by `generate_data.py`. No third-party data or real people are included.', '', f'**Seed:** {202700+i}. Included data is CC0-1.0 under the root DATA_LICENSE.md. All dates refer to fictional 2025 records.', '', '## Grain and field meaning','',s['grain'],'','## Fixture inventory','']
 for f in sorted((p/'data').iterdir()):
  if f.suffix=='.csv':frame=pd.read_csv(f)
  elif f.suffix=='.jsonl':frame=pd.DataFrame([json.loads(x) for x in f.read_text().splitlines()])
  elif f.suffix=='.json':obj=json.loads(f.read_text());frame=pd.DataFrame(obj['records'])
  else:continue
  data_lines += [f'### `{f.name}`',f'{len(frame):,} records.','','| Field | Type | Example |','|---|---|---|']
  for col in frame:data_lines.append(f'| `{col}` | {frame[col].dtype} | `{frame[col].dropna().iloc[0] if frame[col].notna().any() else "null"}` |')
  data_lines.append('')
 data_lines += ['## Intentional edge cases','',s['checks'],'','## Regeneration','', '`python generate_data.py` recreates the fixture files. It does not rerun the pipeline. The generator source is the authoritative construction recipe.','', '## Validation boundary','',s['limits']]
 (p/'data/README.md').write_text('\n'.join(data_lines))
print('Built',len(specs),'engineering projects')
