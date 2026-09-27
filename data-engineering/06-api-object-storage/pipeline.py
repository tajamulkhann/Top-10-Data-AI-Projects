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
    source=(DATA/'weather_snapshot.json').read_bytes();digest=hashlib.sha256(source).hexdigest();landing=out/'landing';landing.mkdir(exist_ok=True);manifest_path=out/'manifest.json'
    manifest_path.unlink(missing_ok=True)
    def ingest(payload):
     sha=hashlib.sha256(payload).hexdigest();old=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
     if sha in old:return False
     target=landing/f'{sha}.json';target.write_bytes(payload)
     assert hashlib.sha256(target.read_bytes()).hexdigest()==sha
     records=json.loads(payload)['records'];df=pd.DataFrame(records)
     assert not df.duplicated(['station_id','date']).any()
     paths=[]
     for date,part in df.groupby('date'):
      dest=out/'curated'/f'date={date}';dest.mkdir(parents=True,exist_ok=True);path=dest/f'{sha[:12]}.csv';part.to_csv(path,index=False);paths.append(str(path.relative_to(out)))
     old[sha]={'rows':len(df),'partitions':paths}
     temp=out/'manifest.tmp';temp.write_text(json.dumps(old,indent=2));os.replace(temp,manifest_path)
     return True
    assert ingest(source);assert not ingest(source)
    # Simulate corruption in a separate probe object; never overwrite committed data.
    probe=out/'corrupt_probe.json';probe.write_bytes(source+b' ')
    corruption_detected=hashlib.sha256(probe.read_bytes()).hexdigest()!=digest
    probe.unlink()
    manifest=json.loads(manifest_path.read_text());paths=manifest[digest]['partitions']
    curated=pd.concat([pd.read_csv(out/p) for p in paths],ignore_index=True)
    assert len(curated)==140 and not curated.duplicated(['station_id','date']).any()
    summary=curated.groupby('date').agg(rows=('station_id','size'),stations=('station_id','nunique')).reset_index()
    checks={'identical_snapshot_skipped':True,'checksum_detects_corruption':corruption_detected,'partition_records_reconciled':True,'station_date_grain_unique':True}
    metrics={'Snapshot records':len(curated),'Daily partitions':len(paths),'Manifest snapshots':len(manifest),'Replay new snapshots':0}
    chart=summary.set_index('date').rows
    finding='One immutable snapshot produced seven daily partitions. An identical payload was skipped and a modified probe failed checksum validation.'
    with sqlite3.connect(out/'catalog.sqlite') as con:curated.to_sql('observations',con,index=False,if_exists='replace')

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
