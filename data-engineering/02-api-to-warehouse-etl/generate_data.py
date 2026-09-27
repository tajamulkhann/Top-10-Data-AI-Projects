from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202701)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
rows=[{'order_id':i,'customer_id':int(rng.integers(1,50)),'amount_cents':int(rng.integers(500,90000)),'status':'paid'} for i in range(1,241)]
rows+= [dict(rows[10]),{'order_id':999,'customer_id':2,'amount_cents':-100,'status':'paid'}]
for j in range(0,len(rows),60):write_json(f'page_{j//60+1}.json',{'records':rows[j:j+60],'next_page':j//60+2 if j+60<len(rows) else None})
