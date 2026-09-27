from pathlib import Path
import json, sqlite3, hashlib, shutil, os
import numpy as np
import pandas as pd
DATA = Path(__file__).resolve().parent / 'data'
def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def run(out):
    """Build one deterministic demonstration, including failure/replay checks."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    batch=pd.read_csv(DATA/'batch.csv').to_dict('records');stream=pd.read_csv(DATA/'stream.csv').to_dict('records')
    def merge(rows):
     state={}
     for row in rows:
      key=row['order_id'];old=state.get(key)
      if old and old['version']==row['version']:
       if old!=row:raise ValueError('Conflicting equal-version payload')
       continue
      if old is None or row['version']>old['version']:state[key]=row.copy()
     return pd.DataFrame(state.values()).sort_values('order_id').reset_index(drop=True)
    state=merge(batch+stream);reverse=merge(list(reversed(stream))+list(reversed(batch)))
    assert state.equals(reverse)
    replay=merge(state.to_dict('records')+batch+stream);assert state.equals(replay)
    conflict_rejected=False
    try:merge([batch[0],dict(batch[0],amount_cents=-1)])
    except ValueError:conflict_rejected=True
    assert conflict_rejected and len(state)==230 and state.deleted.sum()==10
    live=state[state.deleted==0];state.to_csv(out/'unified_state.csv',index=False);live.to_csv(out/'serving_orders.csv',index=False)
    summary=state.groupby(['version','deleted']).agg(keys=('order_id','size'),amount_cents=('amount_cents','sum')).reset_index()
    checks={'arrival_order_converges':True,'full_replay_idempotent':True,'equal_version_conflict_rejected':conflict_rejected,'delete_tombstones_retained':int(state.deleted.sum())==10}
    metrics={'Batch rows':len(batch),'Stream deliveries':len(stream),'Logical keys':len(state),'Serving live orders':len(live),'Tombstones':int(state.deleted.sum())}
    chart=summary.groupby('version')['keys'].sum()
    finding='The combined feeds converge to 230 keys and 220 live orders regardless of tested arrival order; conflicting equal-version payloads are rejected.'
    with sqlite3.connect(out/'unified.sqlite') as con:state.to_sql('state',con,index=False,if_exists='replace')

    checks={k:bool(v) for k,v in checks.items()}
    assert all(checks.values()),checks
    metrics={k:float(v) for k,v in metrics.items()}
    summary.to_csv(out/'summary.csv',index=False)
    pd.DataFrame({'check':list(checks),'passed':list(checks.values())}).to_csv(out/'validation_results.csv',index=False)
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    (out/'checks.json').write_text(json.dumps(checks,indent=2))
    (out/'finding.txt').write_text(finding+'\n')
    # Execute the checked-in SQL against the generated SQLite artifact.
    db_files=list(out.glob('*.sqlite'))
    assert len(db_files)==1
    with sqlite3.connect(db_files[0]) as con:
        sql_result=pd.read_sql_query((DATA.parent/'verification.sql').read_text(),con)
    sql_result.to_csv(out/'sql_results.csv',index=False)
    return {'metrics':metrics,'checks':checks,'summary':summary,'chart':chart,'finding':finding,'sql_result':sql_result}

if __name__=='__main__':
    result=run(Path(__file__).resolve().parent/'outputs')
    print(json.dumps(result['metrics'],indent=2))
    print(result['finding'])
