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
    raw=DATA/'transactions.csv';bronze=out/'bronze';silver=out/'silver';gold=out/'gold'
    for folder in [bronze,silver,gold]:folder.mkdir(exist_ok=True)
    shutil.copyfile(raw,bronze/'transactions.csv')
    source_hash=hashlib.sha256(raw.read_bytes()).hexdigest()
    assert source_hash==hashlib.sha256((bronze/'transactions.csv').read_bytes()).hexdigest()
    def transform():
     frame=pd.read_csv(raw);parsed=pd.to_datetime(frame.order_date,errors='coerce')
     invalid=frame.amount_cents.lt(0)|parsed.isna();bad=frame[invalid].copy()
     good=frame[~invalid].sort_values(['order_id','version']).drop_duplicates('order_id',keep='last')
     assert good.order_id.is_unique and good.amount_cents.ge(0).all()
     aggregate=good.groupby('order_date').agg(orders=('order_id','size'),amount_cents=('amount_cents','sum')).reset_index()
     assert aggregate.orders.sum()==len(good) and aggregate.amount_cents.sum()==good.amount_cents.sum()
     return frame,good,bad,aggregate
    frame,good,bad,summary=transform();_,again,_,summary_again=transform()
    assert good.equals(again) and summary.equals(summary_again)
    good.to_csv(silver/'orders.csv',index=False);bad.to_csv(out/'quarantine.csv',index=False)
    for date,part in summary.groupby('order_date'):
     dest=gold/f'order_date={date}';dest.mkdir(exist_ok=True);part.to_csv(dest/'part.csv',index=False)
    manifest={'source_sha256':source_hash,'bronze_rows':len(frame),'silver_rows':len(good),'rejected_rows':len(bad),'superseded_versions':len(frame)-len(bad)-len(good),'gold_partitions':len(summary)}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    assert len(frame)==len(good)+len(bad)+manifest['superseded_versions']
    checks={'bronze_bytes_preserved':True,'latest_version_wins':good.loc[good.order_id==1,'version'].iloc[0]==2,'gold_reconciles_to_silver':True,'deterministic_rebuild':True}
    metrics={'Bronze rows':len(frame),'Silver orders':len(good),'Rejected rows':len(bad),'Gold partitions':len(summary)}
    chart=summary.set_index('order_date').orders
    finding=f"Retained all {len(frame)} raw versions, published {len(good)} unique silver orders and reconciled {len(summary)} gold partitions."
    with sqlite3.connect(out/'lakehouse.sqlite') as con:good.to_sql('silver_orders',con,index=False,if_exists='replace')

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
