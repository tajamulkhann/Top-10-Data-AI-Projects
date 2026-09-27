from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202702)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
rows=[{'order_id':i,'version':1,'order_date':f'2025-01-{i%7+1:02d}','amount_cents':int(rng.integers(100,50000))} for i in range(1,301)]
rows += [dict(r,version=2,amount_cents=r['amount_cents']+100) for r in rows[:25]]
rows += [{'order_id':1001,'version':1,'order_date':'2025-01-01','amount_cents':-3},{'order_id':1002,'version':1,'order_date':'bad-date','amount_cents':200}]
write_csv('transactions.csv',rows)
