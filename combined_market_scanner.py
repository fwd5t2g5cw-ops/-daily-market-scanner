import argparse, subprocess, sys
from pathlib import Path
import pandas as pd

p=argparse.ArgumentParser()
p.add_argument('--market',choices=['us','tsx','hkex'],required=True)
a=p.parse_args(); market=a.market
out=Path('combined_results')/market
legacy_dir=out/'legacy'; bz_dir=out/'big_zone'
legacy_dir.mkdir(parents=True,exist_ok=True); bz_dir.mkdir(parents=True,exist_ok=True)

# build_universes.py calls Hong Kong "hk", while this combined scanner calls it "hkex".
# Build the correct fresh universe for every market before either scanner runs.
universe_market={'us':'us','tsx':'tsx','hkex':'hk'}[market]
subprocess.run([sys.executable,'build_universes.py','--markets',universe_market],check=True)

symbol_files={'tsx':'data/tsx_universe.txt','hkex':'data/hk_universe.txt'}
legacy_output=legacy_dir/'scan_results.csv'
legacy_args=[sys.executable,'scanner.py','--output',str(legacy_output)]
if market in symbol_files:
    legacy_args += ['--symbols',symbol_files[market]]
subprocess.run(legacy_args,check=True)

# Big Zone has file-based market inputs. Point unwanted markets at empty files.
empty=out/'empty_symbols.txt'; empty.write_text('')
if market=='us':
    bz_args=[sys.executable,'big_zone_scanner.py','--us-file','data/us_universe.txt','--tsx-file',str(empty),'--hk-file',str(empty),'--outdir',str(bz_dir)]
elif market=='tsx':
    bz_args=[sys.executable,'big_zone_scanner.py','--us-file',str(empty),'--tsx-file','data/tsx_universe.txt','--hk-file',str(empty),'--outdir',str(bz_dir)]
else:
    bz_args=[sys.executable,'big_zone_scanner.py','--us-file',str(empty),'--tsx-file',str(empty),'--hk-file','data/hk_universe.txt','--outdir',str(bz_dir)]
subprocess.run(bz_args,check=True)

def load_csv(path):
    q=Path(path)
    if not q.exists() or q.stat().st_size==0:return pd.DataFrame()
    try:return pd.read_csv(q)
    except Exception:return pd.DataFrame()

legacy=load_csv(legacy_output); bz=load_csv(bz_dir/'big_zone_all.csv')

def symcol(df):
    for c in ['symbol','Symbol','Ticker','ticker']:
        if c in df.columns:return c
    return None
ls,bs=symcol(legacy),symcol(bz)
if ls:legacy['_symbol']=legacy[ls].astype(str).str.upper()
if bs:bz['_symbol']=bz[bs].astype(str).str.upper()

# Use scanner score and Big Zone score, with a bonus when both scanners select the name.
if 'score' in legacy.columns:legacy['_legacy_score']=pd.to_numeric(legacy['score'],errors='coerce').fillna(0)
elif 'Score' in legacy.columns:legacy['_legacy_score']=pd.to_numeric(legacy['Score'],errors='coerce').fillna(0)
else:legacy['_legacy_score']=0
if 'Score' in bz.columns:bz['_big_zone_score']=pd.to_numeric(bz['Score'],errors='coerce').fillna(0)
elif 'score' in bz.columns:bz['_big_zone_score']=pd.to_numeric(bz['score'],errors='coerce').fillna(0)
else:bz['_big_zone_score']=0

if ls and bs:
    merged=pd.merge(legacy,bz,on='_symbol',how='outer',suffixes=('_legacy','_bigzone'))
elif ls:
    merged=legacy.copy(); merged['_big_zone_score']=0
elif bs:
    merged=bz.copy(); merged['_legacy_score']=0
else:
    merged=pd.DataFrame(columns=['_symbol','_legacy_score','_big_zone_score'])

for c in ['_legacy_score','_big_zone_score']:
    if c not in merged.columns:merged[c]=0
    merged[c]=pd.to_numeric(merged[c],errors='coerce').fillna(0)
merged['overlap']=(merged['_legacy_score']>0)&(merged['_big_zone_score']>0)
merged['combined_score']=merged['_legacy_score']+merged['_big_zone_score']+merged['overlap'].astype(int)*3
merged=merged.sort_values(['combined_score','overlap','_big_zone_score','_legacy_score'],ascending=False)
merged.to_csv(out/'combined_all.csv',index=False)
merged.head(12).to_csv(out/'top12.csv',index=False)
merged[merged.overlap].sort_values('combined_score',ascending=False).to_csv(out/'overlap.csv',index=False)
print('\nTOP 12')
print(merged[['_symbol','combined_score','overlap','_legacy_score','_big_zone_score']].head(12).to_string(index=False))
print('\nOVERLAP')
print(merged.loc[merged.overlap,['_symbol','combined_score','_legacy_score','_big_zone_score']].head(30).to_string(index=False))
