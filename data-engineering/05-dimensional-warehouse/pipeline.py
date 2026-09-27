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
    customers=pd.read_csv(DATA/'customers.csv');products=pd.read_csv(DATA/'products.csv');orders=pd.read_csv(DATA/'orders.csv');db=out/'warehouse.sqlite';db.unlink(missing_ok=True)
    with sqlite3.connect(db) as con:
     con.execute('PRAGMA foreign_keys=ON')
     con.executescript('CREATE TABLE dim_customer(customer_sk INTEGER PRIMARY KEY,customer_id INTEGER UNIQUE,region TEXT); CREATE TABLE dim_product(product_sk INTEGER PRIMARY KEY,product_id INTEGER UNIQUE,category TEXT); CREATE TABLE fact_order(order_id INTEGER PRIMARY KEY,customer_sk INTEGER REFERENCES dim_customer(customer_sk),product_sk INTEGER REFERENCES dim_product(product_sk),quantity INTEGER CHECK(quantity>0),amount_cents INTEGER CHECK(amount_cents>=0));')
     con.execute("INSERT INTO dim_customer VALUES(0,-1,'Unknown')")
     customer_map={};product_map={}
     for sk,row in enumerate(customers.sort_values('customer_id').itertuples(),1):
      customer_map[row.customer_id]=sk;con.execute('INSERT INTO dim_customer VALUES(?,?,?)',(sk,row.customer_id,row.region))
     for sk,row in enumerate(products.sort_values('product_id').itertuples(),1):
      product_map[row.product_id]=sk;con.execute('INSERT INTO dim_product VALUES(?,?,?)',(sk,row.product_id,row.category))
     for row in orders.itertuples():con.execute('INSERT INTO fact_order VALUES(?,?,?,?,?)',(row.order_id,customer_map.get(row.customer_id,0),product_map[row.product_id],row.quantity,row.quantity*row.unit_price_cents))
     con.commit()
     fk_rejected=False
     try:
      with con:con.execute('INSERT INTO fact_order VALUES(99999,999,1,1,100)')
     except sqlite3.IntegrityError:fk_rejected=True
     facts=pd.read_sql_query('SELECT * FROM fact_order',con)
     summary=pd.read_sql_query('SELECT d.region,COUNT(*) AS orders,SUM(f.amount_cents) AS amount_cents FROM fact_order f JOIN dim_customer d USING(customer_sk) GROUP BY d.region',con)
     assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
    assert len(facts)==len(orders) and facts.amount_cents.sum()==(orders.quantity*orders.unit_price_cents).sum()
    assert (facts.customer_sk==0).sum()==5 and fk_rejected
    facts.to_csv(out/'fact_order.csv',index=False)
    checks={'foreign_key_violation_rejected':fk_rejected,'source_to_fact_amount_reconciled':True,'unknown_member_policy_applied':True,'fact_grain_unique':facts.order_id.is_unique}
    metrics={'Source orders':len(orders),'Fact rows':len(facts),'Unknown-customer facts':int((facts.customer_sk==0).sum()),'Customer dimension rows':len(customers)+1}
    chart=summary.set_index('region').orders
    finding='Published 500 facts with five unresolved customer references assigned to the explicit Unknown member; fact amounts reconcile exactly to the source.'

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
