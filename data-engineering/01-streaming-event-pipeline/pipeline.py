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
    rows=read_jsonl(DATA/'events.jsonl');db=out/'stream.sqlite';db.unlink(missing_ok=True)
    with sqlite3.connect(db) as con:
     con.executescript('CREATE TABLE accepted(event_id TEXT PRIMARY KEY,event_minute INTEGER,value INTEGER); CREATE TABLE seen(event_id TEXT PRIMARY KEY); CREATE TABLE late(event_id TEXT PRIMARY KEY,event_minute INTEGER,value INTEGER); CREATE TABLE state(max_minute INTEGER); INSERT INTO state VALUES(-1);')
    def consume(batch):
     counts={'accepted':0,'duplicate':0,'late':0}
     with sqlite3.connect(db) as con:
      for e in batch:
       with con:
        if con.execute('SELECT 1 FROM seen WHERE event_id=?',(e['event_id'],)).fetchone():counts['duplicate']+=1;continue
        maximum=con.execute('SELECT max_minute FROM state').fetchone()[0]
        is_late=e['event_minute']<maximum-10
        table='late' if is_late else 'accepted'
        con.execute(f'INSERT INTO {table} VALUES(?,?,?)',(e['event_id'],e['event_minute'],e['value']))
        con.execute('INSERT INTO seen VALUES(?)',(e['event_id'],))
        con.execute('UPDATE state SET max_minute=?',(max(maximum,e['event_minute']),))
        counts['late' if is_late else 'accepted']+=1
     return counts
    first=consume(rows[:80]);second=consume(rows[80:]) # new DB connections simulate consumer restart
    with sqlite3.connect(db) as con:before=pd.read_sql_query('SELECT * FROM accepted ORDER BY event_id',con)
    replay=consume(rows)
    with sqlite3.connect(db) as con:
     accepted=pd.read_sql_query('SELECT * FROM accepted ORDER BY event_id',con)
     late=pd.read_sql_query('SELECT * FROM late',con)
     summary=pd.read_sql_query('SELECT (event_minute/5)*5 AS window_start, COUNT(*) AS events, SUM(value) AS total_value FROM accepted GROUP BY window_start ORDER BY window_start',con)
    assert accepted.equals(before)
    assert len(accepted)==180 and len(late)==1 and replay['accepted']==0
    assert first['accepted']+second['accepted']+first['late']+second['late']+first['duplicate']+second['duplicate']==len(rows)
    accepted.to_csv(out/'accepted.csv',index=False);late.to_csv(out/'late_events.csv',index=False)
    checks={'restart_preserves_state':True,'replay_adds_zero_events':True,'late_route_contains_expected_id':late.event_id.tolist()==['late-1'],'input_reconciled':True}
    metrics={'Input deliveries':len(rows),'Accepted logical events':len(accepted),'Late logical events':len(late),'Duplicates on full replay':replay['duplicate']}
    chart=summary.set_index('window_start').events
    finding=f"Accepted {len(accepted)} logical events and routed {len(late)} late event; replay added no accepted rows. Monitor late-event rate before changing the lateness policy."

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
