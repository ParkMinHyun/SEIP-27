import pandas as pd, numpy as np, sys
pd.set_option('display.width',250,'display.max_rows',200)
order=['DEP','DEP_P','mean1','mean3','mean5','mean10','max3','max5','max10','cmean3','cmax5','mean3+50','mean3+100','mean3+150','mean3+200','mean3+300','ALWAYS']
def summ(R):
    out=[]
    for (cond,arm),d in R.groupby(['cond','armname']):
        base=d[d.seed==-1]
        seeds=d[d.seed>=0].groupby('seed').apply(lambda x:(x.margin<0).sum(),include_groups=False)
        out.append(dict(cond=cond,arm=arm,runs=base.groupby(['dev','run']).ngroups,
            miss_caps=(base.margin<0).sum(), miss_runs=base[base.margin<0].groupby(['dev','run']).ngroups,
            miss_seed_range=f'{seeds.min()}-{seeds.max()}' if len(seeds) else '',
            thin_lt70=(base.margin<70).sum(), min_margin=base.margin.min(),
            M_pct=100*base.bokeh.mean(), S_pct=100*base.filt.mean()))
    s=pd.DataFrame(out); s['o']=s.arm.map({a:i for i,a in enumerate(order)})
    return s.sort_values(['cond','o']).drop(columns='o')
for mode in sys.argv[1:]:
    R=pd.read_pickle(f'arms_{mode}.pkl')
    s=summ(R); s.to_csv(f'summary_{mode}.csv',index=False)
    print('== ready-time:',mode); print(s.round(1).to_string(index=False))
