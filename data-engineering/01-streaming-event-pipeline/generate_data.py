from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202700)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
rows=[{'event_id':f'e{i:04d}','event_minute':i,'value':int(rng.integers(1,20))} for i in range(180)]
rows.insert(30,dict(rows[12]));rows.insert(95,{'event_id':'late-1','event_minute':3,'value':8});rows.extend([dict(rows[40]),dict(rows[100])])
write_jsonl('events.jsonl',rows)
