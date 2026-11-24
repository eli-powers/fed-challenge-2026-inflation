"""Shared engine for brief D (methods and backtest) of the October 2026 PCE build.

Run every D_ script from the project root with python3, e.g.
    python3 "02_Research/Subtasks/04_oct_pce_build/code/D_backtest.py"
All inputs are saved local files; nothing is downloaded and nothing under 03_Data is modified.

Locked method (brief_D_methods_backtest.md):
  monthly change ~= sum_i w_i * pi_i, w_i = previous-month nominal spending shares (U20405, current vintage;
  NOT real time). Leaves = the 177 BEA leaf lines in component_mapping.csv (lines 145 and 333 left out,
  weights rescaled). Parent leaves are priced on their sub-lines and rolled up with previous-month
  within-leaf shares. Tenant rent leaf 156: 100% sub-line 157 (CPI rent). NPISH leaf 342: one assumed item.
  Tiers: observed / proxied (line 163 only) / assumed (carry-forward of BEA's own component m/m).
  Seasonal status by BEA's column: SA -> BLS SA series; NSA -> unadjusted; SA by BEA -> method B.
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize, nnls

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build')
OUT = os.path.join(SUB, 'outputs')
RAW = os.path.join(ROOT, '03_Data', 'Raw')
PCE_RAW = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'PCE', 'raw')
U20404 = os.path.join(PCE_RAW, 'BEA_NIUnderlyingDetail_U20404_2026-11-10.json')
U20405 = os.path.join(PCE_RAW, 'BEA_NIUnderlyingDetail_U20405_2026-11-10.json')
MAPPING = os.path.join(OUT, 'component_mapping.csv')
HISTORY = os.path.join(OUT, 'component_series_history.csv')
PPI_FR = os.path.join(OUT, 'ppi_first_release.csv')
PCE_FP = os.path.join(OUT, 'pce_first_prints.csv')
CLEV_LONG = os.path.join(OUT, 'C_cleveland_nowcast_long_mm.csv')
CLEV_HIST = os.path.join(OUT, 'cleveland_nowcast_history.csv')
ALFRED = {s: os.path.join(RAW, f'ALFRED_{s}_all_vintages_2026-11-11.json') for s in ('PCEPILFE', 'PCEPI', 'CPILFESL')}

HEADLINE_LINE, CORE_LINE = 1, 374
NPISH_LEAF, TENANT_LEAF = 342, 156
PROXIED_LINES = {163}
PM_LINE = 268
# Lines whose BEA source changed at the Sep 30, 2026 annual update. NEW_METHOD_START is the first month BEA's
# current-vintage history for the line is built on the NEW source.
#   299, 305 (legal services, professional association dues): 2024-01. BEA, SCB preview of the 2026 annual update
#     (Jun 24, 2026): the PPI composite "will replace the consumer price index (CPI) for legal services beginning
#     in 2024". Corrected from 2021-01 after Codex audit R1-F01 (2026-11-12), i.e. AFTER backtest results were seen.
#   50 (computer software): 2021-01. BEA states no start date for this composite; 2021-01 is the start of the
#     annual-update revision window (judgment call, unverified).
# Two sample boundaries follow from it (R1-F01: keep them separate):
#   m/m samples (method B, method A) start one month later, so no m/m change straddles the method change;
#   12-month-change samples (blend-weight fits) start twelve months later, for the same reason.
NEW_METHOD_START = {50: pd.Period('2021-01', 'M'), 299: pd.Period('2024-01', 'M'), 305: pd.Period('2024-01', 'M')}


def mm_sample_start(ln, default):
    return NEW_METHOD_START[ln] + 1 if ln in NEW_METHOD_START else default


def fit_sample_start(ln, default):
    return NEW_METHOD_START[ln] + 12 if ln in NEW_METHOD_START else default


# Old PPI-based portfolio management: BEA's current-vintage line 268 is implicit (new method) from 2021, so
# weights for the old two-PPI blend are fitted on pre-2021 data only (judgment call).
OLD_PM_FIT_END = pd.Period('2020-12', 'M')

RULE_MONTHS = [str(p) for p in pd.period_range('2025-12', '2026-09', freq='M')]
OLD_GROUP = [str(p) for p in pd.period_range('2025-12', '2026-07', freq='M')]
NEW_GROUP = ['2026-08', '2026-09']
EXTRA_MONTHS = ['2025-11', '2023-10', '2024-10']
CPI_SA_REVISED_FEB2026 = lambda t: pd.Period(t, 'M') <= pd.Period('2025-12', 'M')  # ref months through Dec 2025


def P(x):
    return pd.Period(x, 'M')


# --------------------------------------------------------------------------- loaders
def load_bea_frame(path):
    d = json.load(open(path))['BEAAPI']['Results']['Data']
    rows = [(int(r['LineNumber']), r['TimePeriod'], float(r['DataValue'].replace(',', ''))) for r in d]
    df = pd.DataFrame(rows, columns=['line', 'tp', 'v'])
    df['month'] = pd.PeriodIndex(df.tp.str.replace('M', '-'), freq='M')
    names = {int(r['LineNumber']): r['LineDescription'] for r in d}
    return df.pivot_table(index='month', columns='line', values='v', aggfunc='first').sort_index(), names


def load_history():
    h = pd.read_csv(HISTORY)
    h['month'] = pd.PeriodIndex(h.year.astype(str) + '-' + h.period.str[1:], freq='M')
    lv = h.pivot_table(index='month', columns='series_id', values='value', aggfunc='first').sort_index()
    full = pd.period_range(lv.index.min(), lv.index.max(), freq='M')
    return lv.reindex(full)


def fill_oct2025(lv):
    """Fill for the missing Oct 2025 CPI: geometric mean of Sep and Nov, applied to SA and NSA CPI series alike.
    This matches BEA's stated procedure for SEASONALLY ADJUSTED prices (PIO Oct+Nov 2025 release). For NSA prices
    BEA instead rebuilt October from the SA value and October 2024 seasonal factors; we do not have those factors
    for every series, so for NSA series this is OUR APPROXIMATION, not BEA's method (Codex audit R1-F02).
    Filled October values are kept out of every October seasonal factor. PPIs all have an Oct 2025 value.
    Returns filled levels and the list filled."""
    lv = lv.copy()
    o, s, n = P('2025-10'), P('2025-09'), P('2025-11')
    filled = []
    for c in lv.columns:
        if c.startswith('CU') and pd.isna(lv.at[o, c]) and pd.notna(lv.at[s, c]) and pd.notna(lv.at[n, c]):
            lv.at[o, c] = np.sqrt(lv.at[s, c] * lv.at[n, c])
            filled.append(c)
    return lv, filled


def pct(lv):
    return 100.0 * (lv / lv.shift(1) - 1.0)


def load_ppi_first_release():
    p = pd.read_csv(PPI_FR)
    return {(r.bls_series_id, r.reference_month): float(r.first_print_mm_pct) for r in p.itertuples()}


def alfred_obs(series):
    d = json.load(open(ALFRED[series]))['observations']
    df = pd.DataFrame(d)
    df = df[df.value != '.']
    df['value'] = df.value.astype(float)
    df['month'] = pd.PeriodIndex(df.date.str[:7], freq='M')
    return df


def alfred_asof(df, vintage):
    """Levels by month as of a vintage date string (YYYY-MM-DD)."""
    x = df[(df.realtime_start <= vintage) & (df.realtime_end >= vintage)]
    return x.set_index('month').value.sort_index()


def alfred_first_print(df, month):
    """First vintage carrying `month`; return (vintage, levels-as-of-that-vintage)."""
    m = P(month)
    v = df[df.month == m].realtime_start.min()
    if pd.isna(v):
        return None, None
    return v, alfred_asof(df, v)


def load_mapping():
    m = pd.read_csv(MAPPING)
    m['pricing_bea_line'] = m.pricing_bea_line.astype(int)
    m['leaf_bea_line'] = m.leaf_bea_line.astype(int)
    return m


def parse_blend(s):
    out = []
    for part in str(s).split(';'):
        sid, w = part.rsplit(':', 1)
        out.append((sid.strip(), None if w.strip() == 'NA' else float(w)))
    return out


# --------------------------------------------------------------------------- method versions
def table_version(t):
    """BEA source table in force for the first print of month t (locked spec + judgment for months outside it).
    Dec 2025 - Jul 2026 prints: 2026-02-20 table. Aug 2026 on: 2026-09-30 (current).
    Nov 2025, Oct 2024, Oct 2023 prints predate the Feb 2026 file: 2025-02-28 table (judgment)."""
    t = P(t)
    if t >= P('2026-08'):
        return '2026-09-30'
    if t >= P('2025-12'):
        return '2026-02-20'
    return '2025-02-28'


def build_specs(mapping, version):
    """Pricing specification per pricing line for a table version. Returns dict line -> spec."""
    specs = {}
    for r in mapping.itertuples():
        ln = r.pricing_bea_line
        stat = str(r.bea_seasonal_status)
        spec = dict(line=ln, leaf=r.leaf_bea_line, is_sub=(r.is_subline == 'Y'), in_core=(r.in_core == 'Y'),
                    name=r.pricing_line_name, tier=r.tier, source_tag=r.source_tag, seasonal=None, inputs=[],
                    weight_rule=None, note='')
        if r.tier == 'assumed' or r.source_tag == 'imputed' and ln not in PROXIED_LINES:
            spec['tier'] = 'assumed'
        elif ln in PROXIED_LINES:
            spec['tier'] = 'proxied'
            spec['seasonal'] = 'SA'
            spec['inputs'] = [(r.series_to_use, 1.0)]
        elif r.source_tag == 'blend':
            ins = parse_blend(r.blend_inputs)
            spec['inputs'] = ins
            spec['seasonal'] = 'SAbyBEA' if stat == 'SA by BEA' else 'mixed_by_series'
            spec['weight_rule'] = 'RI' if all(w is not None for _, w in ins) else 'fit'
        else:
            spec['inputs'] = [(r.series_to_use, 1.0)]
            spec['seasonal'] = {'SA': 'SA', 'NSA': 'NSA', 'SA by BEA': 'SAbyBEA'}.get(stat, stat)
        specs[ln] = spec
    # NPISH leaf 342: one assumed item at leaf level (replaces its sub-lines)
    for ln in [k for k, s in specs.items() if s['leaf'] == NPISH_LEAF]:
        del specs[ln]
    specs[NPISH_LEAF] = dict(line=NPISH_LEAF, leaf=NPISH_LEAF, is_sub=False, in_core=True, name='NPISH final consumption (leaf)',
                             tier='assumed', source_tag='imputed', seasonal=None, inputs=[], weight_rule=None,
                             note='NPISH treated as one assumed item at leaf level (locked)')
    # Tenant rent: 157 = 100% CPI rent; 158 dropped (weight 0)
    specs.pop(158, None)

    if version in ('2026-02-20', '2025-02-28'):
        s = specs[50]; s.update(seasonal='NSA', inputs=[('CUUR0000SEEE02', 1.0)], weight_rule=None, source_tag='CPI',
                                note='old table: CPI computer software and accessories alone, NSA')
        s = specs[211]; s.update(seasonal='NSA', inputs=[('CUUR0000SERF01', 1.0)],
                                 note="old table: former CPI item (club dues and fees); CUUR0000SERF01 is C2's closest match (judgment)")
        s = specs[PM_LINE]; s.update(tier='observed', source_tag='blend', seasonal='NSA',
                                     inputs=[('PCU5239405239401', None), ('PCU5239405239402', None)], weight_rule='fit_old_pm',
                                     note='old table: PPI portfolio management, NSA; two PPIs, weights fitted pre-2021')
        for ln in (299, 305):
            s = specs[ln]; s.update(tier='observed', source_tag='CPI', seasonal='NSA', inputs=[('CUUR0000SEGD01', 1.0)],
                                    weight_rule=None, note='old table: CPI legal services (unpublished since Sep 2024 -> assumed when missing)')
    if version == '2025-02-28':
        specs[84].update(seasonal='SA', inputs=[('CUSR0000SEFG', 1.0)], note='2025-02-28 table: SA')
        specs[175].update(seasonal='SA', inputs=[('CUSR0000SEMC02', 1.0)], note='2025-02-28 table: SA')
        for ln in (296, 316):
            specs[ln].update(seasonal='NSA', inputs=[('CUUR0000SEEB03', 1.0)], note='2025-02-28 table: NSA')
    # attribution category
    for s in specs.values():
        if s['tier'] == 'assumed':
            cat = 'assumed'
        elif s['tier'] == 'proxied':
            cat = 'proxied'
        elif s['source_tag'] == 'blend' and len(s['inputs']) > 1:
            cat = 'blend'
        elif s['seasonal'] == 'SAbyBEA':
            cat = 'observed_needs_seasonal'
        else:
            cat = 'observed_published'
        s['cat'] = cat
    return specs


# --------------------------------------------------------------------------- engine
class Engine:
    def __init__(self):
        self.mapping = load_mapping()
        self.bea_p, self.names = load_bea_frame(U20404)
        self.bea_n, _ = load_bea_frame(U20405)
        self.bea_mm = pct(self.bea_p)
        raw_lv = load_history()
        self.src_raw = raw_lv
        self.src_lv, self.oct25_filled = fill_oct2025(raw_lv)
        self.src_mm = pct(self.src_lv)
        self.ppi_fr = load_ppi_first_release()
        self.leaves = sorted(self.mapping.leaf_bea_line.unique())
        self.leaf_core = self.mapping.groupby('leaf_bea_line').in_core.first().eq('Y').to_dict()
        self.ri_cache = {}
        self.fit_cache = {}
        self.specs_cache = {}

    def specs(self, version):
        if version not in self.specs_cache:
            self.specs_cache[version] = build_specs(self.mapping, version)
        return self.specs_cache[version]

    # ---- weights
    def leaf_weights(self, t):
        """Previous-month nominal shares of covered leaves (headline) and core leaves (core), rescaled."""
        prev = P(t) - 1
        nom = self.bea_n.loc[prev, self.leaves]
        wh = nom / nom.sum()
        core = [l for l in self.leaves if self.leaf_core[l]]
        wc = nom[core] / nom[core].sum()
        return wh, wc.reindex(self.leaves).fillna(0.0)

    def sub_shares(self, t, specs):
        """Within-leaf previous-month nominal shares for priced sub-lines (normalised to sum to one)."""
        prev = P(t) - 1
        out, dev = {}, {}
        byleaf = {}
        for ln, s in specs.items():
            byleaf.setdefault(s['leaf'], []).append(ln)
        for leaf, lines in byleaf.items():
            if lines == [leaf]:
                out[leaf] = 1.0
                continue
            if leaf == TENANT_LEAF:
                out[157] = 1.0
                continue
            v = {ln: self.bea_n.at[prev, ln] / self.bea_n.at[prev, leaf] for ln in lines}
            tot = sum(v.values())
            dev[leaf] = tot - 1.0
            for ln in lines:
                out[ln] = v[ln] / tot
        return out, dev

    # ---- source m/m
    def series_mm(self, sid, t, first_release=True):
        """m/m (%) of a source series in month t, with provenance. PPI: first release if available.
        CPI: current vintage (Oct 2025 filled as BEA did). If the target value exists but t-1 is missing, use the
        geometric average over a gap of <= 2 months (bimonthly series such as SEMC04); otherwise missing."""
        t = P(t)
        if sid in getattr(self, 'force_missing', set()):
            return np.nan, 'treated as missing (sensitivity run)'
        if first_release and (sid.startswith('PCU') or sid.startswith('WPU')):
            k = (sid, str(t))
            if k in self.ppi_fr:
                return self.ppi_fr[k], 'PPI first release'
        if sid not in self.src_lv.columns or t not in self.src_lv.index:
            return np.nan, 'missing'
        x = self.src_lv.at[t, sid]
        if pd.isna(x):
            return np.nan, 'missing'
        prov = 'PPI revised (no first release)' if sid.startswith(('PCU', 'WPU')) else 'CPI current vintage'
        if str(t) in ('2025-10', '2025-11') and sid in self.oct25_filled:
            prov += '; Oct 2025 geometric fill'
        y = self.src_lv.at[t - 1, sid] if (t - 1) in self.src_lv.index else np.nan
        if pd.notna(y):
            return 100 * (x / y - 1), prov
        y2 = self.src_lv.at[t - 2, sid] if (t - 2) in self.src_lv.index else np.nan
        if pd.notna(y2):
            return 100 * ((x / y2) ** 0.5 - 1), prov + '; 2-month geometric (t-1 missing)'
        return np.nan, 'missing (t-1 and t-2 absent)'

    def hist_mm(self, sid):
        if sid not in self.src_mm.columns:
            return pd.Series(np.nan, index=self.src_mm.index)
        return self.src_mm[sid]

    # ---- blend weights
    def blend_weights(self, spec, t):
        ins = spec['inputs']
        if spec['weight_rule'] in (None, 'RI'):
            ws = np.array([w for _, w in ins], dtype=float)
            return ws / ws.sum(), 'CPI relative importance Dec 2025' if spec['weight_rule'] == 'RI' else 'single'
        key = (spec['line'], spec['weight_rule'], str(t))
        if key in self.fit_cache:
            return self.fit_cache[key]
        ln = spec['line']
        end = P(t) - 1
        start = fit_sample_start(ln, P('2017-01'))
        if spec['weight_rule'] == 'fit_old_pm':
            end, start = OLD_PM_FIT_END, P('2017-01')
        # fit on 12-month log changes (robust to seasonal mismatch between NSA inputs and BEA's SA line)
        y = np.log(self.bea_p[ln]).diff(12)
        X = pd.concat([np.log(self.src_lv[s]).diff(12) if s in self.src_lv.columns else pd.Series(np.nan, index=self.src_lv.index)
                       for s, _ in ins], axis=1)
        X.columns = [s for s, _ in ins]
        d = pd.concat([y.rename('y'), X], axis=1).loc[start:end].dropna()
        k = len(ins)
        if len(d) < 24:
            res = (np.ones(k) / k, f'equal (fallback: only {len(d)} obs)')
        else:
            # Exact non-negative least squares with the sum-to-one constraint imposed by a heavily weighted extra
            # row (scipy nnls). Replaces an SLSQP fit that stalled at the starting point or failed (bug found during
            # the run and fixed; see notes_D.md). Data in percent.
            A, b = 100 * d[X.columns].values, 100 * d['y'].values
            M = 1e4
            Aa = np.vstack([A, M * np.ones((1, k))])
            ba = np.concatenate([b, [M]])
            w, _ = nnls(Aa, ba, maxiter=5000)
            if w.sum() > 0:
                res = (w / w.sum(), f'fitted NNLS sum-to-one on 12m log changes {d.index[0]}..{d.index[-1]} (n={len(d)})')
            else:
                res = (np.ones(k) / k, 'equal (fallback: fit failed)')
        self.fit_cache[key] = res
        return res

    def nsa_source_hist(self, spec, t):
        """History of the line's (NSA) source m/m built with the weights in force at t (for method B)."""
        ins = spec['inputs']
        w, _ = self.blend_weights(spec, t)
        cols = [self.hist_mm(s) * wi for (s, _), wi in zip(ins, w)]
        return pd.concat(cols, axis=1).sum(axis=1, min_count=len(cols))

    # ---- method B
    def method_b(self, spec, t):
        """BEA's implied adjustment for calendar month of t: mean over prior years of (BEA SA m/m - source NSA m/m).
        Oct 2025 is kept out where a CPI input was missing (filled)."""
        t = P(t)
        ln = spec['line']
        src = self.nsa_source_hist(spec, t)
        gap = self.bea_mm[ln] - src
        start = mm_sample_start(ln, P('2017-02'))
        idx = [p for p in gap.index if p.month == t.month and start <= p < t and pd.notna(gap.get(p, np.nan))]
        if any(s in self.oct25_filled for s, _ in spec['inputs']):
            idx = [p for p in idx if p != P('2025-10')]
        if not idx:
            return 0.0, ''
        return float(gap.loc[idx].mean()), ','.join(str(p.year) for p in idx)

    def method_a(self, spec, t):
        """Own month-dummy adjustment of the NSA source (cross-check): mean NSA m/m in calendar month minus the
        mean over all months, years before t."""
        t = P(t)
        src = self.nsa_source_hist(spec, t)
        start = mm_sample_start(spec['line'], P('2015-02'))
        h = src.loc[start:t - 1].dropna()
        if any(s in self.oct25_filled for s, _ in spec['inputs']):
            h = h.drop([P('2025-10'), P('2025-11')], errors='ignore')
        if len(h) < 24:
            return np.nan
        return float(-(h[h.index.month == t.month].mean() - h.mean()))

    # ---- carry-forward
    def carry_forward(self, ln, t, k):
        t = P(t)
        h = self.bea_mm[ln].loc[t - k:t - 1]
        return float(h.mean())

    # ---- one pricing line
    def price_line(self, spec, t, k, first_release=True):
        t = P(t)
        ln = spec['line']
        bea_line = 156 if ln == 157 else ln
        info = dict(line=ln, leaf=spec['leaf'], name=spec['name'], cat=spec['cat'], tier_used=spec['tier'],
                    seasonal=spec['seasonal'], inputs='', weights='', weight_source='', provenance='', adj_b=np.nan,
                    adj_b_years='', note=spec.get('note', ''))
        if spec['tier'] == 'assumed':
            info.update(pi=self.carry_forward(bea_line, t, k), provenance=f'carry-forward {k}m BEA m/m line {bea_line}')
            return info
        src = self.source_treated(spec, t, first_release)
        info.update(inputs=src['inputs'], weights=src['weights'], weight_source=src['weight_source'],
                    provenance=src['provenance'], adj_b=src['adj_b'], adj_b_years=src['adj_b_years'])
        if pd.isna(src['value']):
            info.update(pi=self.carry_forward(bea_line, t, k), tier_used='assumed', cat='assumed',
                        note=(info['note'] + '; source missing for target month -> assumed this month').strip('; '))
            return info
        info['pi'] = src['value']
        return info

    def source_treated(self, spec, t, first_release=True):
        """Source m/m for month t treated per BEA's seasonal status (no carry-forward fallback)."""
        t = P(t)
        ins = spec['inputs']
        w, wsrc = self.blend_weights(spec, t)
        vals, provs = [], []
        for (sid, _), wi in zip(ins, w):
            v, pv = self.series_mm(sid, t, first_release)
            vals.append(v); provs.append(f'{sid}:{pv}')
        out = dict(inputs=';'.join(s for s, _ in ins), weights=';'.join(f'{x:.4f}' for x in w), weight_source=wsrc,
                   provenance=' | '.join(provs), adj_b=np.nan, adj_b_years='', value=np.nan, raw=np.nan)
        if any(pd.isna(v) for v in vals):
            return out
        val = float(np.dot(w, vals))
        out['raw'] = val
        if spec['seasonal'] == 'SAbyBEA':
            adj, yrs = self.method_b(spec, t)
            out.update(adj_b=adj, adj_b_years=yrs)
            val += adj
        out['value'] = val
        return out

    # ---- full estimate
    def estimate(self, t, k=6, version=None, first_release=True):
        t = P(t)
        version = version or table_version(t)
        specs = self.specs(version)
        wh, wc = self.leaf_weights(t)
        sub, dev = self.sub_shares(t, specs)
        rows = []
        for ln, s in specs.items():
            info = self.price_line(s, t, k, first_release)
            leaf = s['leaf']
            info['w_leaf_h'] = wh[leaf]
            info['w_leaf_c'] = wc[leaf]
            info['sub_share'] = sub[ln]
            info['w_h'] = wh[leaf] * sub[ln]
            info['w_c'] = wc[leaf] * sub[ln]
            info['in_core'] = self.leaf_core[leaf]
            bl = 156 if ln == 157 else ln
            info['pi_bea'] = self.bea_mm.at[t, bl] if t in self.bea_mm.index else np.nan
            rows.append(info)
        df = pd.DataFrame(rows)
        df['contrib_h'] = df.w_h * df.pi
        df['contrib_c'] = df.w_c * df.pi
        df['contrib_h_bea'] = df.w_h * df.pi_bea
        df['contrib_c_bea'] = df.w_c * df.pi_bea
        df['month'] = str(t); df['version'] = version; df['window'] = k
        summ = dict(month=str(t), version=version, window=k, headline=df.contrib_h.sum(), core=df.contrib_c.sum(),
                    max_subshare_dev=max([abs(v) for v in dev.values()] or [0]))
        return summ, df


def bea_published_mm(eng, t):
    t = P(t)
    return eng.bea_mm.at[t, HEADLINE_LINE], eng.bea_mm.at[t, CORE_LINE]


def first_prints():
    """First-print m/m and 12m (same vintage) for core and headline, Jan 2024 - Sep 2026 from pce_first_prints.csv,
    plus Oct 2023 computed from the raw ALFRED files with the same method."""
    fp = pd.read_csv(PCE_FP)
    out = {}
    for r in fp.itertuples():
        out[(r.measure, r.ref_month)] = dict(mm=r.mm_first_print_pct, mm1=r.mm_first_print_1dp, yy=r.yy_first_print_pct,
                                             vintage=r.first_release_vintage, L_prev=r.level_prior_month_same_vintage,
                                             L_yago=r.level_year_ago_same_vintage, flag=r.flag)
    for measure, sid in (('core', 'PCEPILFE'), ('headline', 'PCEPI')):
        df = alfred_obs(sid)
        for m in ('2023-10',):
            if (measure, m) in out:
                continue
            v, lv = alfred_first_print(df, m)
            t = P(m)
            mm = 100 * (lv[t] / lv[t - 1] - 1)
            yago = lv.get(t - 12, np.nan)
            out[(measure, m)] = dict(mm=mm, mm1=round(mm, 1), yy=(100 * (lv[t] / yago - 1)) if pd.notna(yago) else np.nan,
                                     vintage=v, L_prev=lv[t - 1], L_yago=yago, flag='computed from raw ALFRED (D_common)')
    return out


# --------------------------------------------------------------------------- bands
BAND_SD_MONTHS = 36  # judgment: historical SD of m/m over the 36 months before the target month


def bottom_up_band(eng, df, t):
    """Band (a): per assumed or proxied item, weight x historical SD of its m/m (BEA current vintage, 36 months
    before t), combined in quadrature; plus proxy error for line 163 (SD of BEA 163 m/m minus CUSR0000SEHC01 m/m).
    Portfolio management (268), when assumed, is kept out and returned as a separate allowance."""
    t = P(t)
    win = slice(t - BAND_SD_MONTHS, t - 1)
    var_h = var_c = 0.0
    pm_h = pm_c = 0.0
    items = []
    for r in df.itertuples():
        if r.tier_used not in ('assumed', 'proxied'):
            continue
        bl = 156 if r.line == 157 else r.line
        sd = eng.bea_mm[bl].loc[win].std()
        if r.tier_used == 'proxied':
            sid = r.inputs.split(';')[0]
            sd_proxy = (eng.bea_mm[bl] - eng.hist_mm(sid)).loc[win].std()
            sd = sd_proxy  # proxy error replaces the item SD for the proxied line
        if r.line == PM_LINE:
            pm_h, pm_c = r.w_h * sd, r.w_c * sd
            items.append((r.line, r.tier_used, sd, r.w_h * sd, r.w_c * sd, 'separate PM allowance'))
            continue
        var_h += (r.w_h * sd) ** 2
        var_c += (r.w_c * sd) ** 2
        items.append((r.line, r.tier_used, sd, r.w_h * sd, r.w_c * sd, ''))
    it = pd.DataFrame(items, columns=['line', 'tier', 'sd_mm_pp', 'contrib_sd_h', 'contrib_sd_c', 'note'])
    return dict(band_a_h=np.sqrt(var_h), band_a_c=np.sqrt(var_c), pm_allow_h=pm_h, pm_allow_c=pm_c), it


def rates(levels, t, est_mm):
    """Extend a published SA index (levels as of the vintage before t's release) by the estimate for t."""
    t = P(t)
    it = levels[t - 1] * (1 + est_mm / 100)
    return dict(I_t=it, I_tm1=levels[t - 1], r1m=est_mm, r1m_ann=100 * ((it / levels[t - 1]) ** 12 - 1),
                r3m_ann=100 * ((it / levels[t - 3]) ** 4 - 1), r6m_ann=100 * ((it / levels[t - 6]) ** 2 - 1),
                r12m=100 * (it / levels[t - 12] - 1))


def base_vintage_levels(series, t):
    """ALFRED levels from the latest vintage that carries t-1 but not t (i.e., the vintage before t's PCE release)."""
    t = P(t)
    df = alfred_obs(series)
    vint = sorted(df.realtime_start.unique())
    best = None
    for v in vint:
        lv = alfred_asof(df, v)
        if (t - 1) in lv.index and t not in lv.index:
            best = (v, lv)
    return best


def round1(x):
    return np.floor(np.asarray(x, dtype=float) * 10 + 0.5) / 10
