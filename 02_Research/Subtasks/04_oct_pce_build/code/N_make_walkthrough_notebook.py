"""Builds oct2026_pce_walkthrough.ipynb (in the subtask folder) from the cells below.

Run from the project root:
    python3 "02_Research/Subtasks/04_oct_pce_build/code/N_make_walkthrough_notebook.py"
The notebook calls the audited engine (code/D_common.py and friends) step by step. It reads saved files only,
downloads nothing and writes nothing to outputs/.
"""
import os
import nbformat as nbf

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.join(os.path.dirname(HERE), 'oct2026_pce_walkthrough.ipynb')

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip('\n')))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip('\n')))

# ------------------------------------------------------------------------------------------------ 0. intro
md(r"""
# October 2026 PCE, built bottom-up: a walkthrough

UMD College Fed Challenge, national finals. Built Nov 13, 2026.

BEA publishes October 2026 PCE on **Nov 25**. Our data cutoff is **Nov 18**. This notebook estimates October core and headline PCE ourselves, the way BEA builds it: price each PCE component from the October CPI or PPI series **BEA itself names**, weight by September spending shares, and add up.

**What it does, in order**

1. Loads the inputs.
2. Shows the component map: how many components come straight from CPI or PPI, how many need our own seasonal adjustment, how many are composites with derived weights, and how many are carried forward.
3. Prices one component of each type for October 2026, step by step.
4. Adds the components up to core and headline for October 2026.
5. Shows the regressions: the seasonality test, the composite-weight fit, the core-CPI benchmark.
6. Runs the identity test: BEA's own components through our formula.
7. Reruns the backtest live (Dec 2025 – Sep 2026) and applies the decision rule.
8. Reports October 2026: monthly, 3-month, 6-month and 12-month rates, with bands.

**How to run.** In VS Code, pick the `/opt/anaconda3` Python kernel and click *Run All*. It takes well under a minute. Nothing is downloaded and nothing in `outputs/` is overwritten.

**Where the code lives.** Every number comes from the same engine the audited scripts use (`code/D_common.py`). Where the method matters, the notebook prints that function's source code next to its result.
""")

code(r"""
import os, sys, inspect, warnings
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
warnings.filterwarnings('ignore')
sys.dont_write_bytecode = True

def find_subtask():
    here = os.path.abspath('')
    for c in (here, os.path.join(here, '02_Research', 'Subtasks', '04_oct_pce_build'), os.path.dirname(here)):
        if os.path.exists(os.path.join(c, 'code', 'D_common.py')):
            return c
    raise FileNotFoundError('Open this notebook from 02_Research/Subtasks/04_oct_pce_build/')

SUB = find_subtask()
OUT = os.path.join(SUB, 'outputs')
sys.path.insert(0, os.path.join(SUB, 'code'))
import D_common as dc

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_colwidth', 60)
pd.set_option('display.float_format', lambda x: f'{x:,.4f}')

def check(label, live, saved, tol=5e-5):
    ok = abs(live - saved) <= tol
    print(f"{'MATCH ' if ok else 'DIFFERS'}  {label}: live {live:.4f} | audited file {saved:.4f}")

def show_source(fn):
    print(inspect.getsource(fn))

print('Subtask folder:', SUB)
""")

# ------------------------------------------------------------------------------------------------ inputs
md(r"""
## 0. Inputs

Two snapshots of the CPI and PPI component data are used, on purpose:

- **Nov 11 snapshot**: the data the backtest was run and audited on. Section 7 reruns the backtest on it, so the numbers reproduce the audited results.
- **Nov 13 snapshot**: the same pull plus **October PPI**, released this morning at 8:30 ET. Sections 2–4 and 8 use it for the October estimate.

Between the two, BLS also revised June – September PPI. That's why the backtest stays on the snapshot it was audited on.
""")

code(r"""
HIST_NOV11 = os.path.join(OUT, 'component_series_history_2026-11-11.csv')
HIST_NOV13 = os.path.join(OUT, 'component_series_history.csv')

def make_engine(history_file):
    dc.HISTORY = history_file          # the engine reads its CPI/PPI history from this file
    return dc.Engine()

eng_oct = make_engine(HIST_NOV13)      # October 2026 estimate
eng_bt = make_engine(HIST_NOV11)       # backtest, on the audited inputs

inputs = pd.DataFrame([
    ('BEA Table 2.4.4U-D, "Price Indexes for PCE: Source Data"', 'which CPI/PPI BEA uses for each PCE line, and its seasonal status', 'table dated 2026-09-30 (plus the Feb 2026 and Feb 2025 versions for older months)'),
    ('BEA underlying detail U20404 / U20405', 'PCE price index and nominal spending for every line', 'vintage 2026-11-10 (data through Sep 2026)'),
    ('BLS API: 284 CPI and PPI component series', 'the October inputs and their history', 'Nov 11 pull (backtest); Nov 13 pull (adds October PPI)'),
    ('ALFRED: PCEPILFE, PCEPI, CPILFESL', 'what BEA and BLS first published each month', 'all vintages, retrieved 2026-11-11'),
    ('BLS PPI Detailed Reports (archived PDFs)', 'first-release portfolio-management PPIs', 'Nov 2025 – Jul 2026 reports'),
    ('Cleveland Fed inflation nowcast', 'benchmark', 'chart files as of 2026-11-10'),
], columns=['source', 'used for', 'vintage'])
display(inputs)

h13 = pd.read_csv(HIST_NOV13)
ppi = h13[h13.series_id.str.startswith(('PCU', 'WPU'))]
last = ppi.dropna(subset=['value']).assign(m=lambda d: d.year.astype(str) + '-' + d.period.str[1:]).groupby('series_id').m.max()
print(f'PPI series with an October 2026 value in the Nov 13 snapshot: {(last == "2026-10").sum()} of {len(last)}')
""")

# ------------------------------------------------------------------------------------------------ 1. idea
md(r"""
## 1. The idea in one line

$$\pi_t \;\approx\; \sum_i w_{i,t-1}\,\pi_{i,t}$$

- $\pi_{i,t}$ is component $i$'s price change in month $t$, taken from the CPI or PPI series BEA names for it.
- $w_{i,t-1}$ is its share of consumer spending the month before (September for an October estimate).
- Core uses the same formula over the core components, with shares rescaled to sum to one within core.

BEA itself uses a chained Fisher formula; this is the standard close approximation. Section 6 measures how close.
""")

# ------------------------------------------------------------------------------------------------ 2. map
md(r"""
## 2. The component map

Two questions about every PCE line, from BEA's source table:

- **Where does October's price change come from?** One CPI series, one PPI series, a composite of several series, or nothing at all (carried forward).
- **How is the seasonal pattern removed?** BLS already adjusted the series; BEA uses it unadjusted because it has no seasonal pattern; or BEA adjusts it itself without publishing how, so we estimate BEA's adjustment (section 3b).

The grid crosses the two. Shares are September 2026 spending shares, as used for October.
""")

code(r"""
T = '2026-10'
wc_saved = pd.read_csv(os.path.join(OUT, 'backtest_window_choice.csv'))
K = int(wc_saved[wc_saved.chosen & (wc_saved.measure == 'core')].window.iloc[0])   # carry-forward window (section 7 re-derives it)
version = dc.table_version(T)
summ_oct, df_oct = eng_oct.estimate(T, k=K, version=version)

def line_type(r):
    cat = r['cat']
    if cat == 'assumed':
        return '5. Carried forward (assumed)'
    if cat == 'proxied':
        return '4. Proxied'
    if cat == 'blend':
        ws = str(r['weight_source'])
        how = 'CPI relative importance' if 'relative' in ws else ('fitted on BEA history' if 'fitted' in ws else 'equal weights (fallback)')
        return f'3. Composite, weights: {how}'
    src = 'CPI' if str(r['inputs']).startswith('CU') else 'PPI'
    if cat == 'observed_needs_seasonal':
        return f'2. {src} direct, needs our seasonal adjustment'
    return f'1. {src} direct, used as published'

df_oct['type'] = df_oct.apply(line_type, axis=1)
df_oct['our_seasonal_adj'] = (df_oct.seasonal == 'SAbyBEA') & (df_oct.cat != 'assumed')

def source_of(r):
    if r['cat'] == 'assumed':
        return 'Carried forward (no October data)'
    if r['cat'] == 'proxied':
        return 'Proxied'
    if r['cat'] == 'blend':
        return 'Composite'
    return 'CPI direct' if str(r['inputs']).startswith('CU') else 'PPI direct'

df_oct['source'] = df_oct.apply(source_of, axis=1)
def handling(r):
    if r['cat'] == 'assumed':
        return 'n/a'
    st = r['seasonal']
    if st == 'SAbyBEA':
        return 'our own adjustment'
    if st == 'SA':
        return 'BLS-adjusted'
    if st == 'NSA':
        return 'unadjusted, as BEA does'
    # composites: BEA states the status per input; CUSR = BLS seasonally adjusted, everything else unadjusted
    ins = str(r['inputs']).split(';')
    sa_flags = {i.startswith('CUSR') for i in ins}
    if sa_flags == {True}:
        return 'BLS-adjusted'
    if sa_flags == {False}:
        return 'unadjusted, as BEA does'
    return 'mixed (some inputs BLS-adjusted, some unadjusted)'

df_oct['seasonal handling'] = df_oct.apply(handling, axis=1)

rows_order = ['CPI direct', 'PPI direct', 'Composite', 'Proxied', 'Carried forward (no October data)']
cols_order = ['BLS-adjusted', 'unadjusted, as BEA does', 'our own adjustment', 'mixed (some inputs BLS-adjusted, some unadjusted)', 'n/a']

def grid(weight_col):
    g = pd.pivot_table(df_oct, index='source', columns='seasonal handling', values=weight_col, aggfunc='sum', fill_value=0) * 100
    g = g.reindex(index=rows_order, columns=cols_order, fill_value=0)
    g['total'] = g.sum(axis=1)
    g.loc['total'] = g.sum()
    return g

counts = pd.pivot_table(df_oct, index='source', columns='seasonal handling', values='line', aggfunc='count', fill_value=0)
counts = counts.reindex(index=rows_order, columns=cols_order, fill_value=0)
counts['total'] = counts.sum(axis=1); counts.loc['total'] = counts.sum()

fmt = lambda v: '' if abs(v) < 0.05 else f'{v:.1f}%'
print('Share of CORE spending (%)')
display(grid('w_c').style.format(fmt))
print('Share of HEADLINE spending (%)')
display(grid('w_h').style.format(fmt))
print('Number of lines')
display(counts.style.format(lambda v: '' if v == 0 else f'{v:.0f}'))

own = df_oct['seasonal handling'] == 'our own adjustment'
print(f"Rests on our own seasonal adjustment: {100 * df_oct.loc[own, 'w_c'].sum():.1f}% of core, "
      f"{100 * df_oct.loc[own, 'w_h'].sum():.1f}% of headline ({int(own.sum())} lines).")
""")

md(r"""
Notes on the map:

- The 224 lines in the mapping become about 212 here: the nonprofit-institutions leaf (NPISH) is priced as one carried-forward item rather than through its gross-output and receipts sub-lines.
- Shares are of the 99.7% of PCE we cover. The two uncovered lines (net foreign travel, net expenditures abroad, 0.30%) have no price index and are left out.
- A line whose source has no October value is carried forward for this month only. That's why the services-by-other-medical-professionals CPI, published every other month, can move between tiers.
""")

# ------------------------------------------------------------------------------------------------ 3. one line of each type
md(r"""
## 3. Pricing one component of each type, October 2026

### 3a. CPI direct: owners' equivalent rent (BEA line 162, about 13% of core)

BEA's table: "CPI Owners' equivalent rent of primary residence", seasonally adjusted. We use the BLS SA series `CUSR0000SEHC01` as published.
""")

code(r"""
def row(ln):
    return df_oct[df_oct.line == ln].iloc[0]

sid = 'CUSR0000SEHC01'
lv = eng_oct.src_lv[sid]
sep, octv = lv[dc.P('2026-09')], lv[dc.P('2026-10')]
print(f'{sid}: September {sep:.3f} -> October {octv:.3f}')
print(f'Monthly change = {octv:.3f} / {sep:.3f} - 1 = {100 * (octv / sep - 1):.4f}%')
print(f"Engine's value for line 162: {row(162).pi:.4f}%   weight in core {row(162).w_c:.4f}   contribution to core {row(162).contrib_c:.4f} pp")
""")

md(r"""
### 3b. PPI that needs our seasonal adjustment: hospitals (BEA lines 184–186, about 8.9% of core)

BEA's table: "PPI Hospitals", **SA by BEA**. BLS publishes this PPI only unadjusted, and BEA doesn't publish its seasonal factors.

**Our estimate of BEA's adjustment ("method B")**: for each past October, take BEA's seasonally adjusted change for the line minus the unadjusted PPI change. The average of those gaps is our October adjustment. Only years before the target month are used.
""")

code(r"""
spec_h = eng_oct.specs(version)[184]
t = dc.P(T)
src_hist = eng_oct.nsa_source_hist(spec_h, t)          # unadjusted PPI m/m
gap = eng_oct.bea_mm[184] - src_hist                    # BEA SA m/m minus PPI NSA m/m
octs = [p for p in gap.index if p.month == 10 and dc.P('2017-02') <= p < t and pd.notna(gap.get(p))]
tb = pd.DataFrame({'BEA SA change, line 184': eng_oct.bea_mm[184][octs], 'PPI hospitals, unadjusted': src_hist[octs], 'gap': gap[octs]})
tb.index = [str(p) for p in octs]
display(tb)
adj, yrs = eng_oct.method_b(spec_h, t)
raw, _ = eng_oct.series_mm('PCU622---622---', t)
print(f'Average October gap (our seasonal adjustment): {adj:+.4f} pp   (years {yrs})')
print(f'October 2026 PPI hospitals, unadjusted: {raw:+.4f}%')
print(f'Adjusted: {raw:+.4f} {adj:+.4f} = {raw + adj:+.4f}%   engine: {row(184).pi:+.4f}%')
print('\nThe function, as audited:')
show_source(dc.Engine.method_b)
""")

md(r"""
### 3c. Composite with fitted weights: computer software (BEA line 50, about 1.3% of core)

BEA's table: a fixed-weighted composite of the CPI for computer software and accessories, the PPI for game software publishing, and the PPI for hosting and IT infrastructure. BEA doesn't publish the weights.

**Weight fit**: regress BEA's own 12-month change for line 50 on the three inputs' 12-month changes, with weights constrained to be non-negative and sum to one (non-negative least squares). Only months before the target month are used, and only months after BEA switched to this composite. If fewer than 24 months exist, equal weights are used: that's the case for legal services.
""")

code(r"""
spec_s = eng_oct.specs(version)[50]
w, how = eng_oct.blend_weights(spec_s, t)
parts = []
for (s_id, _), wi in zip(spec_s['inputs'], w):
    v, prov = eng_oct.series_mm(s_id, t)
    parts.append((s_id, wi, v, wi * v))
pt = pd.DataFrame(parts, columns=['input series', 'fitted weight', 'Oct m/m %', 'weight x m/m'])
display(pt)
adj_s, yrs_s = eng_oct.method_b(spec_s, t)
print(f'Weights: {how}')
print(f'Weighted change {pt["weight x m/m"].sum():+.4f}%  + our seasonal adjustment {adj_s:+.4f} = {pt["weight x m/m"].sum() + adj_s:+.4f}%   engine: {row(50).pi:+.4f}%')
print('\nLegal services (line 299) weights:', row(299).weight_source)
print('\nThe weight-fitting function, as audited:')
show_source(dc.Engine.blend_weights)
""")

md(r"""
### 3d. Carried forward: portfolio management and investment advice (BEA line 268, about 1.9% of core)

Since Sep 30, 2026 BEA derives this price implicitly from payroll employment and hours, with out months "informed by market indicators and judgmental trend". No October input can replicate that, so we carry forward the average monthly change of BEA's own index over the last 12 months. The window length was chosen by the backtest (section 7).
""")

code(r"""
hist268 = eng_oct.bea_mm[268].loc[t - K:t - 1]
display(hist268.rename('BEA m/m %, line 268').to_frame().T)
print(f'{K}-month average: {hist268.mean():+.4f}%   engine: {row(268).pi:+.4f}%')
""")

# ------------------------------------------------------------------------------------------------ 4. aggregate
md(r"""
## 4. Adding up: October 2026

Each line's contribution is its September spending share times its October change. The table shows the 15 largest contributions to core, by absolute size.
""")

code(r"""
top = (df_oct.assign(abs_c=df_oct.contrib_c.abs()).sort_values('abs_c', ascending=False)
       [['line', 'name', 'type', 'pi', 'w_c', 'contrib_c']].head(15)
       .rename(columns={'pi': 'Oct m/m %', 'w_c': 'core weight', 'contrib_c': 'contribution to core (pp)'}))
display(top)

by_type = df_oct.groupby('type').agg(core_contrib_pp=('contrib_c', 'sum'), headline_contrib_pp=('contrib_h', 'sum'))
by_type.loc['Total'] = by_type.sum()
display(by_type)

saved = pd.read_csv(os.path.join(OUT, 'D_build_2026-10_summary.csv')).set_index('measure')
print(f"October 2026 core PCE, m/m:     {summ_oct['core']:.4f}%")
print(f"October 2026 headline PCE, m/m: {summ_oct['headline']:.4f}%")
check('core m/m vs the saved build', summ_oct['core'], saved.loc['core', 'estimate_mm'])
check('headline m/m vs the saved build', summ_oct['headline'], saved.loc['headline', 'estimate_mm'])
""")

# ------------------------------------------------------------------------------------------------ 5. regressions
md(r"""
## 5. The regressions

### 5a. Is there a seasonal pattern? (F-test on month dummies)

For each unadjusted input, regress its monthly change on 11 month dummies. A significant F-statistic means the series has a seasonal pattern that must be removed. Shown for the hospital PPI, on the audited (Nov 11) data through September 2026.
""")

code(r"""
y = eng_bt.hist_mm('PCU622---622---').loc[dc.P('2015-02'):dc.P('2026-09')].dropna()
d = pd.DataFrame({'y': y.values, 'month': [p.month for p in y.index]})
fit = smf.ols('y ~ C(month)', data=d).fit()
print(f'PPI hospitals, unadjusted m/m, {y.index[0]} to {y.index[-1]}, n = {len(y)}')
print(f'F = {fit.fvalue:.3f}, p = {fit.f_pvalue:.2e}  ->  seasonal at 5%: {fit.f_pvalue < 0.05}')
st = pd.read_csv(os.path.join(OUT, 'seasonal_tests.csv'))
saved_F = st[(st.series_id == 'PCU622---622---') & (st.kind == 'input series F-test')].F_stat.iloc[0]
check('F-statistic vs seasonal_tests.csv', fit.fvalue, saved_F, tol=1e-3)
print(f"\nAll inputs: {int((st[st.kind == 'input series F-test'].seasonal_at_5pct == 'yes').sum())} of "
      f"{int((st.kind == 'input series F-test').sum())} show seasonality at 5%.")
print('\nMonth effects (pp, relative to January):')
display(fit.params.rename('coefficient').to_frame().T)
""")

md(r"""
### 5b. The benchmark our build must beat: core PCE from core CPI alone

The decision rule's benchmark: regress monthly core PCE on monthly core CPI, using only months before the one being predicted. The full-sample fit through September 2026 is shown here; the backtest re-estimates it each month.
""")

code(r"""
from D_backtest import core_cpi_current, bench_core_cpi_ols, cleveland
cpi_mm, cpi_mm_f = core_cpi_current()
dd = pd.concat([eng_bt.bea_mm[dc.CORE_LINE].rename('core_pce'), cpi_mm.rename('core_cpi')], axis=1).loc[dc.P('2017-02'):dc.P('2026-09')].dropna()
ols = smf.ols('core_pce ~ core_cpi', data=dd.reset_index(drop=True)).fit()
print(ols.summary().tables[1])
print(f'n = {int(ols.nobs)}, R^2 = {ols.rsquared:.3f}, residual SD = {np.sqrt(ols.scale):.3f} pp/month')
""")

# ------------------------------------------------------------------------------------------------ 6. identity
md(r"""
## 6. Identity test: is the adding-up formula itself accurate?

Feed **BEA's own** component price changes through our weights and formula, and compare with BEA's published core. Any gap here is error from the formula, not from our pricing.
""")

code(r"""
rows = []
for m in dc.RULE_MONTHS:
    s_, d_ = eng_bt.estimate(m, k=K, version=dc.table_version(m))
    rows.append((m, d_.contrib_c_bea.sum(), eng_bt.bea_mm.at[dc.P(m), dc.CORE_LINE]))
idt = pd.DataFrame(rows, columns=['month', 'our formula on BEA components', 'BEA published core']).set_index('month')
idt['gap'] = idt.iloc[:, 0] - idt.iloc[:, 1]
display(idt)
print(f'Mean absolute gap {idt.gap.abs().mean():.4f} pp; largest {idt.gap.abs().max():.4f} pp.')
print('Cause (found in the audit): two small net lines (net foreign travel, net spending abroad, 0.3% of PCE) are left out,')
print('but they are nets of large gross flows whose prices diverge. Adding them back cuts the largest gap to about 0.005 pp.')
""")

# ------------------------------------------------------------------------------------------------ 7. backtest
md(r"""
## 7. The backtest, rerun live

For each month from December 2025 to September 2026, estimate core PCE using only what was published by the day after that month's PPI release, and compare with what BEA **first** published. Rules locked before any results:

- PPI at first release where available. CPI current vintage.
- BEA's source table as in force for that month: before Sep 30, 2026 portfolio management, legal services and software used their old sources.
- Seasonal factors, composite weights and carry-forward averages use only months before the target.
- Carry-forward window (3, 6 or 12 months) chosen by the smallest error in the carried-forward items' contribution.

The **first-release variant** is the basis for the decision rule (Eli, Nov 13). It differs from the main run in one input: portfolio management in Dec 2025 – Jul 2026 is priced from the PPIs as BLS first published them (recovered from BLS's archived reports), not today's revised values.
""")

code(r"""
fps = dc.first_prints()
MONTHS = dc.RULE_MONTHS + dc.EXTRA_MONTHS

# 1. every month, every window
runs = {(k, m): eng_bt.estimate(m, k=k, version=dc.table_version(m)) for k in (3, 6, 12) for m in MONTHS}

# 2. window choice: error of the carried-forward items' total contribution to core
wsel = []
for k in (3, 6, 12):
    errs = [runs[(k, m)][1].query("cat == 'assumed'").contrib_c.sum() - runs[(k, m)][1].query("cat == 'assumed'").contrib_c_bea.sum()
            for m in dc.RULE_MONTHS]
    wsel.append((k, np.abs(errs).mean()))
wsel = pd.DataFrame(wsel, columns=['window (months)', 'MAE of carried-forward contribution (pp)']).set_index('window (months)')
display(wsel)
K_live = int(wsel.iloc[:, 0].idxmin())
print(f'Chosen window: {K_live} months (the audited choice was {K}).')
""")

code(r"""
from D2_variant_first_release_pm import PMSwapEngine
dc.HISTORY = HIST_NOV11
eng_var = PMSwapEngine(swap=True)

rows = []
for m in dc.RULE_MONTHS:
    fp = fps[('core', m)]
    main_est = runs[(K_live, m)][0]['core']
    var_est = eng_var.estimate(m, k=K_live, version=dc.table_version(m))[0]['core']
    no_change = fps[('core', str(dc.P(m) - 1))]['mm']
    ols_est = bench_core_cpi_ols(eng_bt, m, cpi_mm, cpi_mm_f)[0]
    clev = cleveland(m, fp['vintage'])[0]
    rows.append((m, fp['mm'], var_est, main_est, ols_est, clev, no_change))
bt = pd.DataFrame(rows, columns=['month', 'BEA first print', 'build: first-release variant', 'build: main run',
                                 'core CPI alone (OLS)', 'Cleveland nowcast', 'no change']).set_index('month')
display(bt)
""")

code(r"""
def score(est, target):
    miss = est - target
    a = miss.abs()
    n = len(a)
    se = a.std(ddof=1) / np.sqrt(n)
    return pd.Series({'n': n, 'bias': miss.mean(), 'MAE': a.mean(), 'SE of MAE': se, 'MAE - 1 SE': a.mean() - se,
                      'MAE + 1 SE': a.mean() + se, 'RMSE': np.sqrt((miss ** 2).mean()), 'largest miss': miss[a.idxmax()]})

scores = pd.DataFrame({c: score(bt[c], bt['BEA first print']) for c in bt.columns[1:]}).T
display(scores)

bt_saved = pd.read_csv(os.path.join(OUT, 'backtest_results.csv'))
mae_main_saved = bt_saved.query("row_type == 'summary' and group == 'rule (Dec 2025-Sep 2026)' and measure == 'core' and method == 'build' and target == 'first print'").mae.iloc[0]
var_saved = pd.read_csv(os.path.join(OUT, 'D2_backtest_variant_first_release_pm.csv'))
mae_var_saved = var_saved.query("row_type == 'summary' and run == 'variant' and measure == 'core' and group == 'rule (Dec 2025-Sep 2026)'").mae.iloc[0]
check('main run core MAE vs the audited backtest', scores.loc['build: main run', 'MAE'], mae_main_saved, tol=5e-5)
check('variant core MAE vs the audited variant', scores.loc['build: first-release variant', 'MAE'], mae_var_saved, tol=5e-5)
""")

md(r"""
### The decision rule (set before any results)

- **Threshold leg**: is our typical miss below 0.05 pp? Judged with its uncertainty: if MAE ± 1 SE is entirely below 0.05, *pass*; if it includes 0.05, *inconclusive at this sample size*; if entirely above, *fail*.
- **Benchmark leg**: lower MAE than core CPI alone.
- **Outcome**: both pass → our estimate goes on the slide as our number, with a band. Otherwise → it's shown as a cross-check next to the Cleveland Fed nowcast.
""")

code(r"""
def threshold_leg(lo, hi, thr=0.05):
    return 'pass' if hi < thr else ('fail' if lo > thr else 'inconclusive at this sample size')

for run in ('build: first-release variant', 'build: main run'):
    s = scores.loc[run]
    leg1 = threshold_leg(s['MAE - 1 SE'], s['MAE + 1 SE'])
    leg2 = 'beats' if s['MAE'] < scores.loc['core CPI alone (OLS)', 'MAE'] else 'does not beat'
    basis = '  <- basis for the decision (Eli, Nov 13)' if 'variant' in run else ''
    print(f"{run}{basis}")
    print(f"   threshold leg: MAE {s['MAE']:.4f} +/- {s['SE of MAE']:.4f} = [{s['MAE - 1 SE']:.4f}, {s['MAE + 1 SE']:.4f}] -> {leg1}")
    print(f"   benchmark leg: {s['MAE']:.4f} vs core CPI alone {scores.loc['core CPI alone (OLS)', 'MAE']:.4f} -> {leg2}\n")
""")

code(r"""
print('Months outside the rule (reported, not scored): core miss of the main run vs first print')
for m in dc.EXTRA_MONTHS:
    print(f"   {m}: {runs[(K_live, m)][0]['core'] - fps[('core', m)]['mm']:+.4f} pp")
print('\nBy BEA method regime (main run):')
old = [m for m in dc.RULE_MONTHS if m in dc.OLD_GROUP]
print(f"   old-method months Dec 2025 - Jul 2026: MAE {(bt.loc[old, 'build: main run'] - bt.loc[old, 'BEA first print']).abs().mean():.4f} (n = {len(old)})")
for m in dc.NEW_GROUP:
    print(f"   {m} (current methods, as October will be): miss {bt.loc[m, 'build: main run'] - bt.loc[m, 'BEA first print']:+.4f}")
""")

# ------------------------------------------------------------------------------------------------ 8. October
md(r"""
## 8. October 2026: the result

The October change extends BEA's published, seasonally adjusted September index (vintage of Oct 29). The 3-month, 6-month and 12-month rates come from index ratios:

- 3-month annualized $=(I_{Oct}/I_{Jul})^4-1$
- 6-month annualized $=(I_{Oct}/I_{Apr})^2-1$
- 12-month $=I_{Oct}/I_{Oct\,2025}-1$

**Band**: the wider of a bottom-up band (spread of the carried-forward items) and the backtest's RMSE. An error in October's monthly change is magnified about 12× in the annualized 1-month rate, 4× in the 3-month rate, 2× in the 6-month rate, and 1× in the 12-month rate.
""")

code(r"""
band_a, items = dc.bottom_up_band(eng_oct, df_oct, T)
rmse = {'main run': (scores.loc['build: main run', 'RMSE'], None), 'first-release variant': (scores.loc['build: first-release variant', 'RMSE'], None)}
var_h = var_saved.query("row_type == 'summary' and run == 'variant' and measure == 'headline' and group == 'rule (Dec 2025-Sep 2026)'").rmse.iloc[0]
main_h = bt_saved.query("row_type == 'summary' and group == 'rule (Dec 2025-Sep 2026)' and measure == 'headline' and method == 'build' and target == 'first print'").rmse.iloc[0]
rmse_by = {'core': {'main': scores.loc['build: main run', 'RMSE'], 'variant': scores.loc['build: first-release variant', 'RMSE']},
           'headline': {'main': main_h, 'variant': var_h}}

res = []
for meas, sid, ba in (('core', 'PCEPILFE', band_a['band_a_c']), ('headline', 'PCEPI', band_a['band_a_h'])):
    vint, lvls = dc.base_vintage_levels(sid, dc.P(T))
    r = dc.rates(lvls, dc.P(T), summ_oct[meas])
    b = max(ba, rmse_by[meas]['variant'])
    res.append({'measure': meas, 'm/m %': r['r1m'], 'band (m/m)': b, '1m annualized': r['r1m_ann'], '3m annualized': r['r3m_ann'],
                '3m band': 4 * b, '6m annualized': r['r6m_ann'], '6m band': 2 * b, '12m': r['r12m'], '12m band': b,
                'Sep index (vintage ' + vint + ')': r['I_tm1'], 'Oct index (ours)': r['I_t']})
octres = pd.DataFrame(res).set_index('measure').T
display(octres)

clev = pd.read_csv(os.path.join(OUT, 'cleveland_nowcast_history.csv')).query("target_month == '2026-10'").iloc[0]
print(f"Cleveland Fed nowcast for October (Nov 10): core {clev.core_pce_nowcast_on_cpi_day:.4f} m/m, headline {clev.pce_nowcast_on_cpi_day:.4f} m/m")
print(f"Bands use the first-release variant's RMSE (Eli, Nov 13): core {rmse_by['core']['variant']:.4f}, headline {rmse_by['headline']['variant']:.4f}. "
      f"(Main run would give core {rmse_by['core']['main']:.4f}.) Bottom-up band: core {band_a['band_a_c']:.4f}.")
check('core band vs the saved build', octres.loc['band (m/m)', 'core'], saved.loc['core', 'band_reported'])
print(f"Plus a separate allowance for portfolio management (new BEA method, almost no history): core {band_a['pm_allow_c']:.4f} pp.")
""")

md(r"""
### Two readings worth a look

Both sit in "needs our seasonal adjustment" or "composite", the parts of the build that rest most on our own estimates.
""")

code(r"""
for ln in (207, 50):
    r = row(ln)
    octs_bea = eng_oct.bea_mm[ln][[p for p in eng_oct.bea_mm.index if p.month == 10 and p.year >= 2017]]
    print(f"Line {ln} {r['name']}: our October change {r.pi:+.2f}% (seasonal adjustment {r.adj_b:+.2f} pp), contribution to core {r.contrib_c:+.4f} pp")
    print(f"   BEA's own October changes 2017-2025: min {octs_bea.min():+.2f}%, max {octs_bea.max():+.2f}%")
""")

md(r"""
## 9. What this shows and what it doesn't

- **Shows**: the estimate follows BEA's own source table line by line. 66% of core is read straight off published BLS data. In the backtest, its typical miss (about 0.04 pp) is about half that of core CPI alone and smaller than the Cleveland nowcast's.
- **Doesn't settle**: whether the typical miss is below 0.05 pp. With 10 months the answer is "inconclusive" under the first-release variant.
- **Leans high**: misses were positive in 7 of 10 months, and in both months built under BEA's current methods (+0.056, +0.081) and both past Octobers (+0.086, +0.060).
- **Not fully real time**: the weights, CPI and BEA history are today's vintage, and five small brokerage PPIs (about 0.2% of core) are priced from revised data.
- **Revisions**: BEA revises July–September with the October release, so our 3-month and 6-month rates can move for reasons that have nothing to do with our estimate.
""")

nb = nbf.v4.new_notebook()
nb['cells'] = cells
nb['metadata'] = {'kernelspec': {'name': 'python3', 'display_name': 'Python 3 (ipykernel)', 'language': 'python'},
                  'language_info': {'name': 'python'}}
nbf.write(nb, NB)
print('Wrote', NB)
