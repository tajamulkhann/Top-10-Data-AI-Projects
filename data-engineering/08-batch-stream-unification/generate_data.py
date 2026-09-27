from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202707)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
batch=[{'order_id':i,'version':1,'amount_cents':int(rng.integers(100,10000)),'deleted':0} for i in range(1,201)]
stream=[dict(r) for r in batch[150:]]+[{'order_id':i,'version':2,'amount_cents':15000+i,'deleted':0} for i in range(1,41)]+[{'order_id':i,'version':1,'amount_cents':1000+i,'deleted':0} for i in range(201,231)]+[{'order_id':i,'version':3,'amount_cents':0,'deleted':1} for i in range(1,11)]
write_csv('batch.csv',batch);write_csv('stream.csv',stream)
