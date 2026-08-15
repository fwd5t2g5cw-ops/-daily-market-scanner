import io, re, argparse
from pathlib import Path
import pandas as pd
import requests

NASDAQ='https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt'
OTHER='https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt'
TSX='https://www.tsx.com/files/trading/moc-eligible-stocks.txt'
HKEX='https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx'

def build_us():
    h={'User-Agent':'daily-market-scanner/1.0'}
    n=requests.get(NASDAQ,timeout=60,headers=h); n.raise_for_status()
    o=requests.get(OTHER,timeout=60,headers=h); o.raise_for_status()
    nd=pd.read_csv(io.StringIO(n.text),sep='|'); od=pd.read_csv(io.StringIO(o.text),sep='|')
    nd=nd[(nd['Test Issue']=='N')&(nd['Financial Status'].fillna('N')!='D')]
    od=od[(od['Test Issue']=='N')&(od['Exchange'].isin(['N','A','P']))]
    syms=[]
    for s in list(nd['Symbol'])+list(od['ACT Symbol']):
        s=str(s).strip().upper()
        if s and s!='NAN' and not s.startswith('FILE CREATION TIME') and re.fullmatch(r'[A-Z0-9.-]+',s): syms.append(s.replace('.','-'))
    return list(dict.fromkeys(syms))

def build_tsx():
    r=requests.get(TSX,timeout=60,headers={'User-Agent':'Mozilla/5.0'}); r.raise_for_status()
    syms=[]
    for line in r.text.splitlines():
        s=line.strip().split()[0] if line.strip() else ''
        s=s.upper().replace('.','-')
        if re.fullmatch(r'[A-Z0-9-]+',s): syms.append(s+'.TO')
    syms=list(dict.fromkeys(syms))
    if len(syms)<100: raise RuntimeError(f'TSX universe unexpectedly small: {len(syms)}')
    return syms

def build_hk():
    r=requests.get(HKEX,timeout=60,headers={'User-Agent':'Mozilla/5.0','Accept':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*'}); r.raise_for_status()
    if b'<html' in r.content[:100].lower() or b'<!doctype' in r.content[:100].lower(): raise RuntimeError('HKEX returned HTML')
    x=pd.read_excel(io.BytesIO(r.content),header=None); out=[]
    for v in x.to_numpy().ravel():
        try:
            n=int(float(v))
            if 1<=n<=99999: out.append(f'{n:04d}.HK')
        except Exception: pass
    out=list(dict.fromkeys(out))
    if len(out)<100: raise RuntimeError(f'HKEX universe unexpectedly small: {len(out)}')
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--markets',default='us,tsx,hk'); a=ap.parse_args()
    Path('data').mkdir(exist_ok=True)
    wanted={x.strip() for x in a.markets.split(',')}
    if 'us' in wanted:
        u=build_us(); Path('data/us_universe.txt').write_text('\n'.join(u)+'\n'); print('US',len(u))
    if 'tsx' in wanted:
        t=build_tsx(); Path('data/tsx_universe.txt').write_text('\n'.join(t)+'\n'); print('TSX',len(t))
    if 'hk' in wanted:
        h=build_hk(); Path('data/hk_universe.txt').write_text('\n'.join(h)+'\n'); print('HK',len(h))
if __name__=='__main__': main()
