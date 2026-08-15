from __future__ import annotations
import argparse, io, re, time
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import yfinance as yf

NASDAQ_LISTED='https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt'
OTHER_LISTED='https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt'

def as_series(v):
    if isinstance(v, pd.DataFrame):
        if v.shape[1] == 0: return pd.Series(dtype=float)
        v = v.iloc[:,0]
    return pd.to_numeric(v, errors='coerce').dropna().astype(float)

def pct_return(c,d):
    c=as_series(c)
    if len(c)<=d:return np.nan
    a,b=float(c.iloc[-d-1]),float(c.iloc[-1])
    return b/a-1 if a>0 else np.nan

def download_pipe(url):
    r=requests.get(url,timeout=45,headers={'User-Agent':'daily-market-scanner/1.0'})
    r.raise_for_status(); return pd.read_csv(io.StringIO(r.text),sep='|')

def get_us_universe():
    n=download_pipe(NASDAQ_LISTED); o=download_pipe(OTHER_LISTED)
    n=n[(n['Test Issue']=='N')&(n['Financial Status'].fillna('N')!='D')]
    o=o[(o['Test Issue']=='N')&(o['Exchange'].isin(['N','A','P']))]
    rows=[]
    for _,r in n.iterrows():
        s=str(r.get('Symbol','')).strip().upper(); name=str(r.get('Security Name','')).strip(); etf=str(r.get('ETF','')).strip().upper()=='Y'
        if s and s!='NAN' and not s.startswith('FILE CREATION TIME') and re.fullmatch(r'[A-Z0-9.-]+',s): rows.append((s.replace('.','-'),name,etf))
    for _,r in o.iterrows():
        s=str(r.get('ACT Symbol','')).strip().upper(); name=str(r.get('Security Name','')).strip(); etf=str(r.get('ETF','')).strip().upper()=='Y'
        if s and s!='NAN' and not s.startswith('FILE CREATION TIME') and re.fullmatch(r'[A-Z0-9.-]+',s): rows.append((s.replace('.','-'),name,etf))
    return pd.DataFrame(rows,columns=['symbol','security_name','is_etf']).drop_duplicates('symbol').sort_values('symbol')

def load_universe(path=None,limit=None):
    if path:
        syms=[x.strip().upper() for x in Path(path).read_text().splitlines() if x.strip() and not x.startswith('#')]
        u=pd.DataFrame({'symbol':syms,'security_name':'','is_etf':False})
    else: u=get_us_universe()
    return u.head(limit) if limit else u

def analyze(symbol,df,spy_returns):
    if df is None or len(df)<210:return None
    df=df.dropna(subset=['Close','Volume']).copy(); close,high,low,vol=map(as_series,(df.Close,df.High,df.Low,df.Volume))
    if min(map(len,(close,high,low,vol)))<210:return None
    ma50,ma150,ma200=close.rolling(50).mean(),close.rolling(150).mean(),close.rolling(200).mean()
    av=float(vol.rolling(20).mean().iloc[-1]); c=float(close.iloc[-1]); v=float(vol.iloc[-1]); h52=float(high.rolling(252,min_periods=200).max().iloc[-1]); l52=float(low.rolling(252,min_periods=200).min().iloc[-1])
    s50,s150,s200,s200old=float(ma50.iloc[-1]),float(ma150.iloc[-1]),float(ma200.iloc[-1]),float(ma200.iloc[-21]); ph20=float(high.shift(1).rolling(20).max().iloc[-1]); ph55=float(high.shift(1).rolling(55).max().iloc[-1])
    vals=[av,c,v,h52,l52,s50,s150,s200,s200old,ph20,ph55]
    if any(np.isnan(x) for x in vals):return None
    liquid=c>=5 and av>=300000 and c*av>=5000000
    trend=c>s50>s150>s200 and s200>s200old and c>=1.30*l52 and c>=.75*h52
    mandatory=liquid and trend; rv=v/av if av else 0; near=c>=.85*h52; b20=c>ph20; b55=c>ph55; surge=rv>=1.5
    def pr(d):
        lo,hi=float(low.iloc[-d:].min()),float(high.iloc[-d:].max()); return hi/lo-1 if lo>0 else np.nan
    r60,r30,r15,r7=(pr(x) for x in (60,30,15,7)); dry=float(vol.iloc[-10:].mean())<float(vol.iloc[-50:].mean())*.8
    vcp=bool(r60>r30>r15>r7 and r15<=r30*.8 and r7<=r15*.8 and dry and r15<=.15)
    pivot=float(high.shift(1).iloc[-10:].max()); to_pivot=(c/pivot-1)*100; vcp_breakout=bool(vcp and c>pivot and surge); vcp_watch=bool(vcp and not vcp_breakout and -5<=to_pivot<=1)
    window=high.iloc[-70:-20]; prior=float(window.max()); pos=int(np.argmax(window.to_numpy()))+(len(high)-70); after=high.iloc[pos+1:]; adv=float(after.max()) if len(after) else np.nan
    advpct=(adv/prior-1)*100 if prior>0 and not np.isnan(adv) else np.nan; sd=(c/prior-1)*100; low3=float(low.iloc[-3:].min()); und=(low3/prior-1)*100; reclaim=low3<prior and c>prior
    pb5=float(vol.iloc[-5:].mean()); pv20=float(vol.iloc[-25:-5].mean()); pbdry=pv20>0 and pb5<pv20*.9; peak=float(high.iloc[-20:].max()); pbpeak=(c/peak-1)*100
    op=as_series(df.Open); body=abs(c-float(op.iloc[-1]))/c; red=len(close)>=2 and c<float(close.iloc[-2])*.95 and v>av*1.2; notext=c<=s50*1.15
    structure=bool(trend and notext and 5<=advpct<=35 and pbpeak<=-2); pbwatch=bool(structure and 0<=sd<=3 and pbdry); pbtrigger=bool(structure and reclaim and -2.5<=und<0 and 0<sd<=2 and not red and body<=.08)
    entry=stop=t1=t2=np.nan; plan_type='NONE'
    if pbtrigger: entry=c; stop=low3; t1=adv; t2=low3+1.618*max(adv-low3,0); plan_type='PLAYBOOK_TRIGGER'
    elif pbwatch: entry=prior; t1=adv; plan_type='PLAYBOOK_WATCH_PENDING_TRIGGER'
    elif vcp_breakout: entry=c; stop=float(low.iloc[-7:].min()); risk=max(entry-stop,0); t1=entry+2*risk; t2=entry+3*risk; plan_type='VCP_BREAKOUT'
    elif vcp_watch: entry=pivot; plan_type='VCP_WATCH_PENDING_BREAKOUT'
    risk_amt=entry-stop if not np.isnan(entry) and not np.isnan(stop) else np.nan; risk_pct=(risk_amt/entry*100) if not np.isnan(risk_amt) and entry>0 else np.nan
    rr1=((t1-entry)/risk_amt) if not np.isnan(risk_amt) and risk_amt>0 and not np.isnan(t1) else np.nan; rr2=((t2-entry)/risk_amt) if not np.isnan(risk_amt) and risk_amt>0 and not np.isnan(t2) else np.nan
    r63,r126,r252=pct_return(close,63),pct_return(close,126),pct_return(close,252); rs=np.nan
    if not any(np.isnan(x) for x in [r63,r126,r252,spy_returns[63],spy_returns[126],spy_returns[252]]): rs=.4*(r63-spy_returns[63])+.2*(r126-spy_returns[126])+.4*(r252-spy_returns[252])
    score=sum([near,b20,b55,surge,vcp,pbwatch,pbtrigger]); sig=[]
    if vcp_breakout:sig.append('VCP_BREAKOUT')
    if vcp_watch:sig.append('VCP_WATCH')
    if pbtrigger:sig.append('PLAYBOOK_TRIGGER')
    elif pbwatch:sig.append('PLAYBOOK_WATCH')
    if not sig:sig.append('WATCH')
    rnd=lambda x: round(float(x),2) if not pd.isna(x) else np.nan
    return {'symbol':symbol,'close':rnd(c),'avg_volume_20d':int(av),'relative_volume':rnd(rv),'pct_from_52w_high':rnd((c/h52-1)*100),'mandatory_pass':mandatory,'trend_template':trend,'liquid':liquid,'breakout_20d':b20,'breakout_55d':b55,'volume_surge':surge,'vcp':vcp,'vcp_breakout':vcp_breakout,'vcp_watch':vcp_watch,'volume_dryup':dry,'pivot':rnd(pivot),'pct_to_pivot':rnd(to_pivot),'playbook_prior_high':rnd(prior),'playbook_advance_high':rnd(adv),'playbook_advance_pct':rnd(advpct),'playbook_support_distance_pct':rnd(sd),'playbook_undercut_pct':rnd(und),'playbook_pullback_volume_dryup':pbdry,'playbook_watch':pbwatch,'playbook_trigger':pbtrigger,'plan_type':plan_type,'entry':rnd(entry),'stop':rnd(stop),'target1':rnd(t1),'target2':rnd(t2),'risk_pct':rnd(risk_pct),'rr_target1':rnd(rr1),'rr_target2':rnd(rr2),'rs_raw':rs,'signals':'|'.join(sig),'score':score}

def add_grades(out):
    rs_pts=np.select([out.rs_percentile>=90,out.rs_percentile>=80,out.rs_percentile>=70],[25,20,15],default=0)
    score_pts=np.select([out.score>=5,out.score>=4,out.score>=3,out.score>=2],[20,17,14,9],default=4)
    risk_pts=np.where(out.risk_pct.notna(),np.select([out.risk_pct<=2,out.risk_pct<=3,out.risk_pct<=5],[20,17,12],default=5),0)
    rr_pts=np.where(out.rr_target1.notna(),np.select([out.rr_target1>=3,out.rr_target1>=2,out.rr_target1>=1.5],[20,16,11],default=4),0)
    vol_pts=np.select([out.volume_surge,out.relative_volume>=1.2,out.playbook_pullback_volume_dryup|out.volume_dryup],[10,8,7],default=4)
    pattern_pts=np.select([out.high_conviction,out.playbook_trigger|out.vcp_breakout],[5,5],default=2)
    out['grade_score']=(rs_pts+score_pts+risk_pts+rr_pts+vol_pts+pattern_pts).astype(int); out['trade_grade']=np.select([out.grade_score>=85,out.grade_score>=70],['A','B'],default='C')
    dist=np.where(out.vcp_watch,abs(out.pct_to_pivot),abs(out.playbook_support_distance_pct)); dist_pts=np.select([dist<=.5,dist<=1,dist<=2,dist<=3,dist<=5],[25,23,20,16,10],default=4)
    watch_rs=np.select([out.rs_percentile>=90,out.rs_percentile>=80,out.rs_percentile>=70],[30,25,20],default=8); watch_pattern=np.select([out.high_conviction,out.vcp_watch|out.playbook_watch],[20,17],default=5)
    watch_vol=np.select([out.playbook_pullback_volume_dryup|out.volume_dryup,out.relative_volume>=1.2],[15,10],default=5); watch_trend=np.select([out.breakout_55d,out.breakout_20d,out.trend_template],[10,9,8],default=0)
    out['watch_score']=(watch_rs+dist_pts+watch_pattern+watch_vol+watch_trend).astype(int); out['watch_grade']=np.select([out.watch_score>=85,out.watch_score>=70],['A','B'],default='C')
    out['trigger_distance_pct']=np.where(out.vcp_watch,abs(out.pct_to_pivot),np.where(out.playbook_watch,abs(out.playbook_support_distance_pct),np.nan))
    pending=out.plan_type.isin(['PLAYBOOK_WATCH_PENDING_TRIGGER','VCP_WATCH_PENDING_BREAKOUT']); out.loc[~pending,['watch_score','watch_grade','trigger_distance_pct']]=[np.nan,'',np.nan]; out.loc[pending,['grade_score','trade_grade']]=[np.nan,'']
    return out

def scan(universe,batch_size=100):
    spy=yf.download('SPY',period='18mo',interval='1d',auto_adjust=True,progress=False); sc=as_series(spy.Close); sr={d:pct_return(sc,d) for d in (63,126,252)}
    rows=[]; meta=universe.set_index('symbol').to_dict('index'); symbols=universe.symbol.tolist()
    for st in range(0,len(symbols),batch_size):
        b=symbols[st:st+batch_size]; print(f'Downloading {st+1}-{min(st+batch_size,len(symbols))} of {len(symbols)}...')
        try:data=yf.download(b,period='18mo',interval='1d',group_by='ticker',auto_adjust=True,threads=True,progress=False)
        except Exception as e: print('Batch failed',e); continue
        for s in b:
            try:
                r=analyze(s,data if len(b)==1 else data[s],sr)
                if r:r.update(meta.get(s,{})); rows.append(r)
            except Exception as e: print('Skipping',s,e)
        time.sleep(.5)
    if not rows:return pd.DataFrame()
    out=pd.DataFrame(rows); stockmask=~out.is_etf.fillna(False); out['rs_percentile']=np.nan
    out.loc[stockmask,'rs_percentile']=(out.loc[stockmask,'rs_raw'].rank(pct=True,method='average')*100).round(0); out.loc[~stockmask,'rs_percentile']=(out.loc[~stockmask,'rs_raw'].rank(pct=True,method='average')*100).round(0)
    out['rs_strong']=out.rs_percentile>=70; out['score']+=out.rs_strong.astype(int); out['high_conviction']=(out.vcp_breakout|out.vcp_watch)&(out.playbook_trigger|out.playbook_watch)
    return add_grades(out)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--symbols'); p.add_argument('--limit',type=int); p.add_argument('--min-score',type=int,default=1); p.add_argument('--min-rs',type=float,default=70); p.add_argument('--output',default='output/scan_results.csv'); a=p.parse_args()
    res=scan(load_universe(a.symbols,a.limit)); out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    if res.empty: res.to_csv(out,index=False); return
    sel=res[(res.mandatory_pass)&(res.rs_percentile>=a.min_rs)&(res.score>=a.min_score)].copy(); sel.to_csv(out,index=False)
    stocks=sel[~sel.is_etf.fillna(False)].copy(); etfs=sel[sel.is_etf.fillna(False)].copy()
    for prefix,d in [('',stocks),('etf_',etfs)]:
        masks={'vcp_breakout.csv':d.vcp_breakout,'vcp_watch.csv':d.vcp_watch,'playbook_trigger.csv':d.playbook_trigger,'playbook_watch.csv':d.playbook_watch,'high_conviction.csv':d.high_conviction}
        for n,m in masks.items(): d[m].to_csv(out.with_name(prefix+n),index=False)
        triggered=d[d.plan_type.isin(['PLAYBOOK_TRIGGER','VCP_BREAKOUT'])].sort_values(['grade_score','rr_target1'],ascending=[False,False])
        pending=d[d.plan_type.isin(['PLAYBOOK_WATCH_PENDING_TRIGGER','VCP_WATCH_PENDING_BREAKOUT'])].sort_values(['watch_score','trigger_distance_pct','rs_percentile'],ascending=[False,True,False])
        pd.concat([triggered,pending]).to_csv(out.with_name(prefix+'trade_plans.csv'),index=False)
        for g in ['A','B','C']:
            triggered[triggered.trade_grade==g].to_csv(out.with_name(prefix+f'grade_{g.lower()}.csv'),index=False); pending[pending.watch_grade==g].to_csv(out.with_name(prefix+f'watch_grade_{g.lower()}.csv'),index=False)
        out.with_name(prefix+'grade_a_watchlist.txt').write_text(','.join(triggered[triggered.trade_grade=='A'].symbol.tolist()))
        out.with_name(prefix+'watch_grade_a_watchlist.txt').write_text(','.join(pending[pending.watch_grade=='A'].symbol.tolist()))
    out.with_name('tradingview_watchlist.txt').write_text(','.join(stocks.symbol.astype(str).tolist()))
    print('Selected:',len(sel),'Playbook trigger:',int(stocks.playbook_trigger.sum()),'VCP breakout:',int(stocks.vcp_breakout.sum()),'High conviction:',int(stocks.high_conviction.sum()))

if __name__=='__main__': main()
