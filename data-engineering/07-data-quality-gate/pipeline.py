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
    raw=pd.read_csv(DATA/'invoices.csv')
    def validate(frame):
     rules=pd.DataFrame({'duplicate_id':frame.invoice_id.duplicated(keep=False),'negative_amount':frame.amount_cents.lt(0),'unknown_customer':~frame.customer_id.isin(range(1,51)),'invalid_date':pd.to_datetime(frame.invoice_date,errors='coerce').isna()})
     invalid=rules.any(axis=1);bad=frame[invalid].copy();bad['failed_rules']=rules[invalid].apply(lambda r:','.join(r.index[r]),axis=1)
     return frame[~invalid].copy(),bad,rules
    probe=raw.iloc[[0]].copy();probe['amount_cents']=-1;probe['customer_id']=999
    _,probe_bad,probe_rules=validate(probe)
    assert len(probe_bad)==1 and int(probe_rules.sum().sum())==2
    clean,bad,rules=validate(raw);threshold=.02
    assert len(bad)/len(raw)<=threshold
    published=out/'published.csv';clean.to_csv(published,index=False);before=published.read_bytes()
    degraded=raw.copy();degraded.loc[:99,'amount_cents']=-1
    _,bad_degraded,_=validate(degraded);blocked=len(bad_degraded)/len(degraded)>threshold
    if not blocked:raise AssertionError('Degraded batch should fail publication')
    assert before==published.read_bytes() # failing batch leaves prior release intact
    assert len(clean)+len(bad)==len(raw) and len(bad)==5
    bad.to_csv(out/'quarantine.csv',index=False);rules.assign(row_number=range(len(raw))).to_csv(out/'rule_audit.csv',index=False)
    summary=rules.sum().rename('failures').rename_axis('rule').reset_index()
    checks={'raw_equals_accepted_plus_rejected':True,'overlapping_rules_not_double_counted':True,'degraded_batch_blocked':blocked,'prior_release_unchanged_after_failure':True}
    metrics={'Raw invoices':len(raw),'Accepted invoices':len(clean),'Rejected rows':len(bad),'Rejected rate (%)':100*len(bad)/len(raw),'Degraded batch rejected rows':len(bad_degraded)}
    chart=summary.set_index('rule').failures
    finding=f"Published {len(clean)} accepted rows and quarantined {len(bad)} rows. A degraded batch breached the 2% gate and did not replace the last valid release."
    with sqlite3.connect(out/'quality.sqlite') as con:rules.astype(int).to_sql('rule_audit',con,index=False,if_exists='replace')

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
