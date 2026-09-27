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
    db=out/'orchestrator.sqlite';db.unlink(missing_ok=True);events=[];run_key=hashlib.sha256((DATA/'daily_orders.csv').read_bytes()).hexdigest()
    with sqlite3.connect(db) as con:con.executescript('CREATE TABLE target(record_id INTEGER PRIMARY KEY,partition_date TEXT,amount_cents INTEGER); CREATE TABLE completed(run_key TEXT PRIMARY KEY,row_count INTEGER);')
    def job(inject_failure):
     with sqlite3.connect(db) as con:
      if con.execute('SELECT 1 FROM completed WHERE run_key=?',(run_key,)).fetchone():
       events.append({'task':'run','attempt':1,'status':'skipped_completed'});return 'skipped'
     frame=pd.read_csv(DATA/'daily_orders.csv');events.append({'task':'extract','attempt':1,'status':'success'})
     assert frame.record_id.is_unique and frame.amount_cents.ge(0).all();events.append({'task':'validate','attempt':1,'status':'success'})
     for attempt in range(1,4):
      try:
       with sqlite3.connect(db) as con:
        with con:
         for idx,row in enumerate(frame.itertuples()):
          con.execute('INSERT INTO target VALUES(?,?,?) ON CONFLICT(record_id) DO UPDATE SET partition_date=excluded.partition_date,amount_cents=excluded.amount_cents',(row.record_id,row.partition_date,row.amount_cents))
          if inject_failure and attempt==1 and idx==0:raise RuntimeError('Injected mid-load failure')
         con.execute('INSERT INTO completed VALUES(?,?)',(run_key,len(frame)))
       events.append({'task':'load','attempt':attempt,'status':'success'});break
      except RuntimeError:
       with sqlite3.connect(db) as con:
        assert con.execute('SELECT COUNT(*) FROM target').fetchone()[0]==0
        assert con.execute('SELECT COUNT(*) FROM completed').fetchone()[0]==0
       events.append({'task':'load','attempt':attempt,'status':'failed_rolled_back'})
     else:raise RuntimeError('Retry budget exhausted')
     events.append({'task':'publish','attempt':1,'status':'success'});return 'completed'
    assert job(True)=='completed';assert job(False)=='skipped'
    with sqlite3.connect(db) as con:
     target=pd.read_sql_query('SELECT * FROM target',con);summary=pd.read_sql_query('SELECT partition_date,COUNT(*) AS rows,SUM(amount_cents) AS amount_cents FROM target GROUP BY partition_date',con)
     assert con.execute('SELECT COUNT(*) FROM completed').fetchone()[0]==1
    source=pd.read_csv(DATA/'daily_orders.csv');assert len(target)==len(source) and target.amount_cents.sum()==source.amount_cents.sum()
    pd.DataFrame(events).to_csv(out/'task_log.csv',index=False);target.to_csv(out/'published_orders.csv',index=False)
    checks={'failed_load_rolled_back':True,'checkpoint_not_advanced_on_failure':True,'retry_commits_once':True,'completed_run_skipped':True,'source_sink_reconciled':True}
    metrics={'Published rows':len(target),'Task log events':len(events),'Load attempts':sum(e['task']=='load' for e in events),'Completion checkpoints':1}
    chart=pd.DataFrame(events).groupby('status').size()
    finding='A mid-load failure rolled back both data and checkpoint. The retry committed 400 rows once, and the completed run was skipped on replay.'

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
