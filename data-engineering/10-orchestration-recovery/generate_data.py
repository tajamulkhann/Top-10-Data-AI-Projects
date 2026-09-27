from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202709)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
write_csv('daily_orders.csv',[{'record_id':i,'partition_date':f'2025-04-{i%5+1:02d}','amount_cents':int(rng.integers(100,20000))} for i in range(1,401)])
