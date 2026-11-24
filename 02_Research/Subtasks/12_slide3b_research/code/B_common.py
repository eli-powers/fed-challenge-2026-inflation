"""Shared helpers for Agent B scripts (slide 3B research: oil paths and pass-through mapping).

Run any B_*.py from the project root with:  python3 -I 02_Research/Subtasks/12_slide3b_research/code/B_xxx.py
The forecast script can import `map_gap_to_core` from here:
    sys.path.insert(0, ".../12_slide3b_research/code"); from B_common import map_gap_to_core
"""
import json, math, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(".")
TASK = ROOT / "02_Research/Subtasks/12_slide3b_research"
OUT = TASK / "outputs"
RAW = ROOT / "03_Data/Raw"
TODAY = "2026-11-15"
OUT.mkdir(parents=True, exist_ok=True)


def load_keys():
    env = {}
    p = Path(".env")
    for line in p.read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


KEYS = load_keys()


def redact(text):
    for v in KEYS.values():
        if v:
            text = text.replace(v, "REDACTED")
    return text


def http_get(url, params=None, timeout=120):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (university research)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def quarter_of(date_str):
    y, m = int(date_str[:4]), int(date_str[5:7])
    return f"{y}Q{(m - 1) // 3 + 1}"


def quarters(start, end):
    """List of 'YYYYQn' from start to end inclusive."""
    y, q = int(start[:4]), int(start[-1])
    out = []
    while True:
        s = f"{y}Q{q}"
        out.append(s)
        if s == end:
            return out
        q += 1
        if q == 5:
            y, q = y + 1, 1


def map_gap_to_core(gap_path, response, log_points=True, exact=True):
    """Map a quarterly oil-price gap path into a core PCE price-level and inflation adjustment.

    Parameters
    ----------
    gap_path : list of float
        Oil gap g_s for consecutive quarters s = 0..T-1, in percent of the baseline-assumption
        oil price. Use log points x100 (100*ln(P_scenario/P_assumed)) when log_points=True
        (recommended: the oil note's model is in log differences, so a log gap is additive).
        The first element is the first quarter in which the gap can be nonzero (2026Q3 for the
        Q3-SPF baseline); the gap before that quarter is taken as 0.
    response : list of float
        R_k, k = 0..K: cumulative core PRICE-LEVEL response (in %, i.e. log points x100) k quarters
        after a PERMANENT 10% (10 log points) rise in the oil price, k=0 being the impact quarter.
        For k > K the response is held at R_K (the note's Fig. 2 shows the level has largely
        converged by ~12 quarters; holding flat is an assumption).
    log_points : bool
        Documentation flag only; the arithmetic is the same. The response is per 10 units of gap.
    exact : bool
        If True, the annualized inflation adjustment uses exact compounding of the level gap;
        otherwise the approximation a_t = 4*(L_t - L_{t-1}).

    Returns
    -------
    dict with lists (length T):
      'L'   : core price-level adjustment L_t in % (log points x100), L_t = sum_{s<=t} R_{t-s} * dg_s / 10,
              where dg_s = g_s - g_{s-1} (g_{-1} = 0). Linear superposition of step responses.
      'a_qa': adjustment to quarterly annualized core inflation, pp.
              approx: 4*(L_t - L_{t-1});  exact: 100*[exp(4*(L_t-L_{t-1})/100) - 1] applied as a
              difference vs. the baseline is second-order; we report the exact-compounding version
              of the level gap: 100*((exp((L_t-L_{t-1})/100))**4 - 1).
      'dL'  : L_t - L_{t-1}, pp of quarterly (non-annualized) log change.
    Q4/Q4 adjustment for year Y (in pp, log approx): L[Q4 of Y] - L[Q4 of Y-1].

    Notes
    -----
    * The oil note's regressor is oil inflation RELATIVE TO core inflation. A higher core path
      lowers relative oil inflation, a negative feedback. In the published impulse responses
      (Fig. 2) that feedback is already embedded, so using R_k from Fig. 2 (or from a simulation
      that includes the feedback, see B_q4_response.py) is internally consistent. The size of the
      feedback is tiny because pass-through coefficients sum to 0.001-0.014.
    * The response is for a five-economy panel average, not the US, and the authors call the
      post-pandemic projection an upper bound.
    """
    T = len(gap_path)
    K = len(response) - 1
    R = lambda k: response[k] if k <= K else response[K]
    dg = [gap_path[0]] + [gap_path[s] - gap_path[s - 1] for s in range(1, T)]
    L = []
    for t in range(T):
        L.append(sum(R(t - s) * dg[s] / 10.0 for s in range(t + 1)))
    dL = [L[0]] + [L[t] - L[t - 1] for t in range(1, T)]
    if exact:
        a = [100.0 * (math.exp(x / 100.0) ** 4 - 1.0) for x in dL]
    else:
        a = [4.0 * x for x in dL]
    return {"L": L, "dL": dL, "a_qa": a}
