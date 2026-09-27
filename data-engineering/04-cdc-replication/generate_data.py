from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202703)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
rows=[{'customer_id':i,'source_version':1,'op':'I','balance_cents':int(rng.integers(100,10000))} for i in range(1,151)]
rows += [{'customer_id':i,'source_version':2,'op':'U','balance_cents':20000+i} for i in range(1,51)]
rows += [{'customer_id':i,'source_version':3,'op':'D','balance_cents':None} for i in range(1,16)]
rows += [{'customer_id':i,'source_version':2,'op':'U','balance_cents':1} for i in range(1,16)]
rows += [dict(rows[170])]
write_jsonl('cdc.jsonl',rows)
