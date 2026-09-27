from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202704)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
write_csv('customers.csv',[{'customer_id':i,'region':['North','South','East','West'][i%4]} for i in range(1,51)])
write_csv('products.csv',[{'product_id':i,'category':['Home','Tech','Food'][i%3]} for i in range(1,21)])
write_csv('orders.csv',[{'order_id':i,'customer_id':999 if i%100==0 else int(rng.integers(1,51)),'product_id':int(rng.integers(1,21)),'quantity':int(rng.integers(1,6)),'unit_price_cents':int(rng.integers(200,10000))} for i in range(1,501)])
