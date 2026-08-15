import argparse, os, subprocess, sys
from pathlib import Path
import pandas as pd

p=argparse.ArgumentParser()
p.add_argument('--market', choices=['us','tsx','hkex'], required=True)
a=p.parse_args()
market=a.market
out=Path('combined_results')/market
out.mkdir(parents=True, exist_ok=True)

# Build only the requested universe where applicable.
if market in ('tsx','hkex'):
    subprocess.run([sys.executable,'build_universes.py','--markets',market],check=True)

# Run legacy Playbook/VCP scanner for one market.
legacy_args=[sys.executable,'scanner.py','--market',market,'--output-dir',str(out/'legacy')]
subprocess.run(legacy_args,check=True)

# Run Big Zone for the same market only.
bz_args=[sys.executable,'big_zone_scanner.py','--market',market,'--output-dir',str(out/'big_zone')]
subprocess.run(bz_args,check=True)

def load_first(paths):
    for x in paths:
        q=Path(x)
        if q.exists() and q.stat().st_size:
            try: return pd.read_csv(q)
            except Exception: pass
    return pd.DataFrame()

legacy=load_first([out/'legacy'/'scan_results.csv',out/'legacy'/'trade_plans.csv'])
bz=load_first([out/'big_zone'/'big_zone_all.csv'])

def symcol(df):
    for c in ['Symbol','symbol','Ticker','ticker']:
        if c in df.columns:return c
    return None
ls,bs=symcol(legacy),symcol(bz)
if ls: legacy['_symbol']=legacy[ls].astype(str).str.upper()
if bs: bz['_symbol']=bz[bs].astype(str).str.upper()

def scorecol(df):
    for c in ['Score','score','Total Score','total_score']:
        if c in df.columns:return c
    return None
lc,bc=scorecol(legacy),scorecol(bz)
if lc: legacy['_legacy_score']=pd.to_numeric(legacy[lc],errors='coerce').fillna(0)
else: legacy['_legacy_score']=0
if bc: bz['_big_zone_score']=pd.to_numeric(bz[bc],errors='coerce').fillna(0)
else: bz['_big_zone_score']=0

if ls and bs:
    merged=pd.merge(legacy,bz,on='_symbol',how='outer',suffixes=('_legacy','_bigzone'))
else:
    merged=pd.DataFrame()
if not merged.empty:
    merged['_legacy_score']=pd.to_numeric(merged.get('_legacy_score',0),errors='coerce').fillna(0)
    merged['_big_zone_score']=pd.to_numeric(merged.get('_big_zone_score',0),errors='coerce').fillna(0)
    merged['overlap']=(merged['_legacy_score']>0)&(merged['_big_zone_score']>0)
    # Overlap bonus deliberately makes multi-signal names rank above otherwise similar single-signal names.
    merged['combined_score']=merged['_legacy_score']+merged['_big_zone_score']+merged['overlap'].astype(int)*3
    merged=merged.sort_values(['combined_score','overlap','_big_zone_score','_legacy_score'],ascending=False)
    merged.to_csv(out/'combined_all.csv',index=False)
    merged.head(12).to_csv(out/'top12.csv',index=False)
    merged[merged.overlap].sort_values('combined_score',ascending=False).to_csv(out/'overlap.csv',index=False)
    print('\nTOP 12')
    print(merged[['_symbol','combined_score','overlap','_legacy_score','_big_zone_score']].head(12).to_string(index=False))
    print('\nOVERLAP')
    print(merged.loc[merged.overlap,['_symbol','combined_score','_legacy_score','_big_zone_score']].head(30).to_string(index=False))
else:
    pd.DataFrame().to_csv(out/'top12.csv',index=False)
    pd.DataFrame().to_csv(out/'overlap.csv',index=False)
