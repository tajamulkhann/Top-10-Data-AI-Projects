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
    rows=read_jsonl(DATA/'cdc.jsonl');db=out/'replica.sqlite';db.unlink(missing_ok=True)
    with sqlite3.connect(db) as con:con.executescript('CREATE TABLE state(customer_id INTEGER PRIMARY KEY,source_version INTEGER,balance_cents INTEGER,deleted INTEGER); CREATE TABLE audit(customer_id INTEGER,source_version INTEGER,op TEXT);')
    def apply(events,fail=False):
     applied=0;skipped=0
     with sqlite3.connect(db) as con:
      with con:
       for e in events:
        old=con.execute('SELECT source_version FROM state WHERE customer_id=?',(e['customer_id'],)).fetchone()
        if old and old[0]>=e['source_version']:skipped+=1;continue
        con.execute('INSERT INTO state VALUES(?,?,?,?) ON CONFLICT(customer_id) DO UPDATE SET source_version=excluded.source_version,balance_cents=excluded.balance_cents,deleted=excluded.deleted',(e['customer_id'],e['source_version'],e['balance_cents'],int(e['op']=='D')))
        if fail:raise RuntimeError('Injected failure before audit insert')
        con.execute('INSERT INTO audit VALUES(?,?,?)',(e['customer_id'],e['source_version'],e['op']));applied+=1
     return applied,skipped
    apply(rows[:150])
    try:apply(rows[150:151],fail=True)
    except RuntimeError:pass
    with sqlite3.connect(db) as con:assert con.execute('SELECT source_version FROM state WHERE customer_id=1').fetchone()[0]==1
    apply(rows[150:]);applied_replay,skipped=apply(rows)
    with sqlite3.connect(db) as con:
     state=pd.read_sql_query('SELECT * FROM state ORDER BY customer_id',con);audit=pd.read_sql_query('SELECT * FROM audit',con)
    assert state.deleted.sum()==15 and len(state[state.deleted==0])==135 and applied_replay==0 and len(audit)==215
    state.to_csv(out/'replica_state.csv',index=False);audit.to_csv(out/'applied_events.csv',index=False)
    summary=state.groupby('deleted').agg(keys=('customer_id','size'),balance_cents=('balance_cents','sum')).reset_index()
    checks={'failed_transaction_rolled_back':True,'deleted_keys_not_resurrected':state.loc[state.customer_id<=15,'deleted'].eq(1).all(),'replay_applies_zero_changes':True,'audit_matches_applied_changes':len(audit)==215}
    metrics={'Source messages':len(rows),'Live replica rows':135,'Tombstones':15,'Applied source changes':len(audit)}
    chart=summary.set_index('deleted')['keys']
    finding='Replica contains 135 live rows and 15 tombstones. A stale update could not resurrect a deleted key, and an injected apply failure rolled back.'

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
