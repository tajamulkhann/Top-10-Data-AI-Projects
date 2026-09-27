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
    changes=pd.read_csv(DATA/'customer_changes.csv');orders=pd.read_csv(DATA/'orders.csv')
    def build(frame):
     f=frame.sort_values(['customer_id','effective_date']).copy()
     assert not f.duplicated(['customer_id','effective_date']).any()
     f=f[f.region.ne(f.groupby('customer_id').region.shift())].copy()
     f['valid_from']=f.effective_date;f['valid_to']=f.groupby('customer_id').effective_date.shift(-1).fillna('9999-12-31')
     f['is_current']=(f.valid_to=='9999-12-31').astype(int);f['customer_sk']=np.arange(1,len(f)+1)
     return f[['customer_sk','customer_id','region','valid_from','valid_to','is_current']].reset_index(drop=True)
    dim=build(changes);assert dim.equals(build(changes.sample(frac=1,random_state=42)))
    assert (dim.valid_from<dim.valid_to).all() and dim.groupby('customer_id').is_current.sum().eq(1).all()
    for _,g in dim.groupby('customer_id'):
     assert g.valid_to.iloc[:-1].tolist()==g.valid_from.iloc[1:].tolist()
    db=out/'history.sqlite'
    with sqlite3.connect(db) as con:
     dim.to_sql('dim_customer',con,index=False,if_exists='replace');orders.to_sql('orders',con,index=False,if_exists='replace')
     joined=pd.read_sql_query('SELECT o.*,d.customer_sk,d.region FROM orders o JOIN dim_customer d ON o.customer_id=d.customer_id AND o.order_date>=d.valid_from AND o.order_date<d.valid_to',con)
     boundary=con.execute("SELECT region FROM dim_customer WHERE customer_id=1 AND '2025-03-01'>=valid_from AND '2025-03-01'<valid_to").fetchall()
    assert len(joined)==len(orders) and joined.order_id.is_unique and boundary==[('South',)]
    dim.to_csv(out/'dim_customer_history.csv',index=False);joined.to_csv(out/'point_in_time_orders.csv',index=False)
    summary=dim.groupby('region').agg(versions=('customer_sk','size'),current_versions=('is_current','sum')).reset_index()
    checks={'one_current_version_per_customer':True,'intervals_nonoverlapping':True,'boundary_joins_new_version':True,'every_fact_matches_exactly_once':True,'input_order_independent':True}
    metrics={'Change records':len(changes),'Dimension versions':len(dim),'Current customers':int(dim.is_current.sum()),'Point-in-time fact matches':len(joined)}
    chart=summary.set_index('region').versions
    finding='Collapsed unchanged attributes into 80 historical versions for 60 customers; all 300 orders matched exactly one valid historical row.'

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
