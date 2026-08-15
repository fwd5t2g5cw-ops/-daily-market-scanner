from pathlib import Path
import pandas as pd
OUT=Path('output'); PREV=Path('previous')
PAIRS=[('grade_a.csv','NEW_A_TRADE'),('watch_grade_a.csv','NEW_A_WATCH'),('etf_grade_a.csv','NEW_ETF_A_TRADE'),('etf_watch_grade_a.csv','NEW_ETF_A_WATCH')]
def symbols(path):
    try:
        df=pd.read_csv(path); return set(df['symbol'].dropna().astype(str).str.upper()) if 'symbol' in df else set()
    except Exception:return set()
def find_previous(name):
    hits=list(PREV.rglob(name)); return hits[0] if hits else None
summary=[]
for name,label in PAIRS:
    cur=OUT/name
    if not cur.exists():continue
    df=pd.read_csv(cur); old=symbols(find_previous(name)) if find_previous(name) else set()
    if 'symbol' not in df:continue
    df['history_status']=df['symbol'].astype(str).str.upper().map(lambda s:'NEW' if s not in old else 'EXISTING'); df.to_csv(cur,index=False)
    new=df[df.history_status=='NEW'].copy(); new.to_csv(OUT/f'new_{name}',index=False)
    summary.append({'category':label,'new_count':len(new),'existing_count':len(df)-len(new),'new_symbols':','.join(new.symbol.astype(str))})
pd.DataFrame(summary).to_csv(OUT/'new_signal_summary.csv',index=False)
(OUT/'new_signal_summary.txt').write_text('\n'.join(['# New Signal Summary','']+[f"- {x['category']}: {x['new_count']} new — {x['new_symbols'] or 'None'}" for x in summary])+'\n')
