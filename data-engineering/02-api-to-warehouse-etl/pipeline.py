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
    db=out/'warehouse.sqlite';db.unlink(missing_ok=True);attempt_log=[]
    with sqlite3.connect(db) as con:con.execute('CREATE TABLE orders(order_id INTEGER PRIMARY KEY,customer_id INTEGER,amount_cents INTEGER CHECK(amount_cents>=0),status TEXT)')
    def extract():
     page=1;records=[]
     while page is not None:
      for attempt in range(1,4):
       status=429 if page==2 and attempt==1 else 200
       attempt_log.append({'page':page,'attempt':attempt,'status':status,'planned_wait_seconds':2**(attempt-1) if status==429 else 0})
       if status==200:
        response=json.loads((DATA/f'page_{page}.json').read_text());break
      else:raise RuntimeError('Retry budget exhausted')
      records.extend(response['records']);page=response['next_page']
     return records
    def load(records):
     bad=[]
     with sqlite3.connect(db) as con:
      with con:
       for row in records:
        if not isinstance(row.get('amount_cents'),int) or row['amount_cents']<0:
         bad.append(dict(row,reason='invalid_amount_cents'));continue
        con.execute('INSERT INTO orders VALUES(?,?,?,?) ON CONFLICT(order_id) DO UPDATE SET customer_id=excluded.customer_id,amount_cents=excluded.amount_cents,status=excluded.status',(row['order_id'],row['customer_id'],row['amount_cents'],row['status']))
     return bad
    records=extract();bad=load(records)
    with sqlite3.connect(db) as con:before=pd.read_sql_query('SELECT * FROM orders ORDER BY order_id',con)
    load(records)
    with sqlite3.connect(db) as con:
     after=pd.read_sql_query('SELECT * FROM orders ORDER BY order_id',con)
     summary=pd.read_sql_query('SELECT customer_id,COUNT(*) AS orders,SUM(amount_cents) AS amount_cents FROM orders GROUP BY customer_id',con)
    assert after.equals(before) and len(after)==240 and len(bad)==1
    assert sum(r['amount_cents'] for r in {r['order_id']:r for r in records if r['amount_cents']>=0}.values())==summary.amount_cents.sum()
    pd.DataFrame(bad).to_csv(out/'quarantine.csv',index=False);pd.DataFrame(attempt_log).to_csv(out/'request_attempts.csv',index=False);after.to_csv(out/'orders.csv',index=False)
    checks={'transient_failure_retried':any(r['status']==429 for r in attempt_log),'replay_preserves_rows_and_values':True,'negative_amount_quarantined':True,'source_amount_reconciled':True}
    metrics={'Source records':len(records),'Warehouse orders':len(after),'Quarantined records':len(bad),'Request attempts':len(attempt_log)}
    chart=summary.set_index('customer_id').orders
    finding=f"Loaded {len(after)} distinct orders with one invalid record quarantined. Full replay left both row count and values unchanged."

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
