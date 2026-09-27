from pathlib import Path
import json
import numpy as np
import pandas as pd
DATA=Path(__file__).resolve().parent/'data'
DATA.mkdir(exist_ok=True)
rng=np.random.default_rng(202705)
def write_json(name,content):
    (DATA/name).write_text(json.dumps(content,indent=2))
def write_jsonl(name,rows):
    (DATA/name).write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(DATA/name,index=False)
write_json('weather_snapshot.json',{'records':[{'station_id':f'S{s:03d}','date':f'2025-02-{d:02d}','temperature_c':round(float(rng.normal(22,5)),2)} for d in range(1,8) for s in range(1,21)]})
