import sys; sys.path.insert(0, sys.argv[1])
from recon import *
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',60)
for back in (12,3):
    bl_,dl=breadth('leaf',Oleaves,'winbase',back,detail=True)
    bs_,ds=breadth('sub',Oleaves,'winbase',back,detail=True)
    dl['wl']=100*dl.w/dl.w.sum(); ds['ws']=100*ds.w/ds.w.sum()
    m=ds.merge(dl[['leaf','r','wl']].rename(columns={'r':'r_leaf'}),on='leaf')
    m=m[m.line!=m.leaf]
    m['name']=m.line.map(eng.names); m['leafname']=m.leaf.map(eng.names)
    m['flip']=(m.r>3)!=(m.r_leaf>3)
    f=m[m.flip].sort_values('ws',ascending=False)
    print(f'=== {back}m: split leaves',m.leaf.nunique(),'sub-lines',len(m),'flipping sub-lines',len(f),
          'net effect on breadth (O-P) pp', round(bs_-bl_,3))
    f['sign']=np.where(f.r>3,'+','-')
    print('sum + flips',round(f.ws[f.sign=='+'].sum(),3),'sum - flips',round(f.ws[f.sign=='-'].sum(),3))
    print(m.groupby('leafname').agg(ws=('ws','sum'),r_leaf=('r_leaf','first'),n=('line','size')).sort_values('ws',ascending=False).round(2).to_string()) if back==12 else None
    print(f[['leaf','leafname','r_leaf','line','name','ws','r','sign']].head(15).round(2).to_string(index=False))
    # sub-line coverage of leaf nominal
    cov=pd.Series({lf: sum(bn.at[T-back,l] for l in g.line)/bn.at[T-back,lf] for lf,g in m.groupby('leaf') if lf!=156})
    print('sub-line nominal / leaf nominal (min,max):',round(cov.min(),3),round(cov.max(),3)); print(cov[(cov-1).abs()>0.01].round(3).to_dict())
