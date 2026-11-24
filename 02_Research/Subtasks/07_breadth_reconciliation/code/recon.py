import sys, os, itertools
import pandas as pd, numpy as np
ROOT='.'
sys.dont_write_bytecode=True
sys.path.insert(0, ROOT+'/02_Research/Subtasks/04_oct_pce_build/code')
import D_common as dc
eng=dc.Engine(); P=dc.P
bp, bn = eng.bea_p, eng.bea_n
specs=eng.specs('2026-09-30')
# ---- Method P from its own processed file
comp=pd.read_csv(ROOT+'/03_Data/pipelines/Price indexes/PCE/processed/components.csv')
h=comp[comp.index_name=='PCE headline'].copy()
h['ln']=h.component_id.str.extract(r'line (\d+)')[0].astype(float)
def lrule(l): return not (73<=l<=103 or 113<=l<=119 or 169<=l<=171)
c=h[h.ln.notna() & h.ln.map(lambda l: lrule(l) if l==l else False)].dropna(subset=['pct_12m_calc'])
w=c.weight_base_12m
print('P reproduce: leaves',len(c),'12m',100*w[c.pct_12m_calc>3].sum()/w.sum(),'3m',100*w[c.pct_3m_ann_calc>3].sum()/w[c.pct_3m_ann_calc.notna()].sum())
Pleaves=set(c.ln.astype(int))
Oleaves=set(l for l in eng.leaves if eng.leaf_core[l])
print('core leaf sets: P-O',sorted(Pleaves-Oleaves),'O-P',sorted(Oleaves-Pleaves), 'Pall-Oall', sorted(set(h.ln.dropna().astype(int))-set(eng.leaves)), sorted(set(eng.leaves)-set(h.ln.dropna().astype(int))))
# ---- generic breadth
T=P('2026-09')
def rate(line, end, back):
    bl=156 if line==157 else line
    s=bp[bl]; a=s.get(end); b=s.get(end-back)
    r=a/b
    return 100*(r**(12/back)-1)
def units(gran, coreset):
    """list of (line, leaf) pricing units"""
    if gran=='leaf': return [(l,l) for l in sorted(coreset)]
    return [(ln,s['leaf']) for ln,s in specs.items() if s['leaf'] in coreset]
def weight(line, leaf, month, gran):
    # nominal spending share of the unit at month (rescaling cancels in breadth)
    if gran=='leaf' or line==leaf: return bn.at[month, leaf]
    if leaf==dc.TENANT_LEAF: return bn.at[month, leaf]
    if leaf==dc.NPISH_LEAF: return bn.at[month, leaf]
    subs=[l for l,s in specs.items() if s['leaf']==leaf]
    tot=sum(bn.at[month,l] for l in subs)
    return bn.at[month,leaf]*bn.at[month,line]/tot
def breadth(gran, coreset, wmode, back, end=T, detail=False):
    rows=[]
    for line,leaf in units(gran, coreset):
        wm = end-12 if wmode=='12base' else end-back
        rows.append((line,leaf,weight(line,leaf,wm,gran),rate(line if gran!='leaf' else leaf,end,back)))
    d=pd.DataFrame(rows,columns=['line','leaf','w','r']).dropna()
    b=100*d.w[d.r>3].sum()/d.w.sum()
    return (b,d) if detail else b
if __name__=='__main__':
    for back in (12,3):
        print(f'--- {back}m Sep 2026')
        for gran in ('leaf','sub'):
            for cs,nm in ((Pleaves,'Pcore'),(Oleaves,'Ocore')):
                for wm in ('12base','winbase'):
                    print(gran,nm,wm,round(breadth(gran,cs,wm,back),3))
    # Oct check vs W file
    W=pd.read_csv(ROOT+'/02_Research/Subtasks/04_oct_pce_build/outputs/W_pce_oct_tab_lines.csv'); g=W[W.w_c!=0]
    print('Oct O from W: 12m',100*g.w12_c[g.pct_12m>3].sum()/g.w12_c.sum(),'3m w3',100*g.w3_c[g.pct_3m_ann>3].sum()/g.w3_c.sum(),'3m w12',100*g.w12_c[g.pct_3m_ann>3].sum()/g.w12_c.sum())
    print('NPISH in specs', dc.NPISH_LEAF in specs, 'n units sub core', len(units('sub',Oleaves)))
