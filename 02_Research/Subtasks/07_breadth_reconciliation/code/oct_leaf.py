import sys; sys.path.insert(0, sys.argv[1])
from recon import *
L=pd.read_csv(ROOT+'/02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv')
print(L.columns.tolist()[:30])
lp=L.groupby('leaf').apply(lambda g:(g.sub_share*g.pi).sum()/g.sub_share.sum(), include_groups=False)
O=P('2026-10')
res={}
for back in (12,3):
    rows=[]
    for lf in sorted(Oleaves):
        s=bp[lf]; i_oct=s[T]*(1+lp[lf]/100)
        r=100*((i_oct/s[O-back])**(12/back)-1)
        for wm,mon in (('12base',O-12),('winbase',O-back)): rows.append((wm,lf,bn.at[mon,lf],r))
    d=pd.DataFrame(rows,columns=['wm','lf','w','r'])
    for wm,g in d.groupby('wm'): print('Oct leaf',back,wm,round(100*g.w[g.r>3].sum()/g.w.sum(),3))
