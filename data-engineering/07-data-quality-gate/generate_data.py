from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202706)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
rows=[{'invoice_id':i,'customer_id':int(rng.integers(1,51)),'amount_cents':int(rng.integers(1,50000)),'invoice_date':'2025-03-01'} for i in range(1,301)]
rows[3]['amount_cents']=-5;rows[8]['customer_id']=999;rows[15]['invoice_date']='invalid';rows.append(dict(rows[30]))
write_csv('invoices.csv',rows)
