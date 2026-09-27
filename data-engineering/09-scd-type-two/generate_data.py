from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202708)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
changes=[]
for i in range(1,61):
 changes += [{'customer_id':i,'effective_date':'2025-01-01','region':'North'},{'customer_id':i,'effective_date':'2025-03-01','region':'South' if i<=20 else 'North'}]
write_csv('customer_changes.csv',changes)
write_csv('orders.csv',[{'order_id':i,'customer_id':i%60+1,'order_date':['2025-02-28','2025-03-01','2025-04-15'][i%3],'amount_cents':100+i} for i in range(1,301)])
