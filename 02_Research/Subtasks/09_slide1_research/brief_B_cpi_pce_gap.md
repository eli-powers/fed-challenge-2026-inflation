You are a research collaborator for an undergraduate economics student preparing UMD's College Fed Challenge national-finals presentation: an FOMC policy simulation with live Q&A from Fed judges, data cutoff Nov 18, 2026. Explain technical concepts plainly. Prefer primary sources: BEA and BLS data and methodology.

## Project context
On slide 1, the speaker says in one line why core PCE now runs **above** core CPI: Sep 2026, core PCE 3.12% vs core CPI ~2.6% y/y. Judges may probe it.
- BEA publishes a monthly CPI-to-PCE reconciliation (Table 9.1U) for **headline only**. It splits the gap into formula, weight, scope and other effects.
- There is no published core reconciliation. You build one.
- Earlier work found that BEA's Sept 30 methods change shrank the gap. It also found that portfolio management and software add about +0.25 pp to core PCE (Aug).
- Shelter's weight in CPI is about 2× its weight in PCE.

## Your task
1. **Core reconciliation, Sep 2026, y/y, published data.** Decompose core PCE minus core CPI into BEA's Table 9.1U categories, adapted to core:
   - **weight effect:** shelter, plus the other big items;
   - **scope:** PCE-only items such as third-party-paid health care, imputed financial services, NPISH and portfolio management; and CPI-only items;
   - **formula:** chain Fisher vs Laspeyres-type;
   - **price and other effects:** for example airfares, which PCE prices from PPI.
   - Deliver `outputs/B_core_gap_sep.csv`: effect | item | pp | method | source. Include a residual row.
   - The sum plus the residual must equal the published core gap.
2. **The same for Oct 2026,** using our October PCE estimate (`02_Research/Subtasks/04_oct_pce_build/outputs/`) and October CPI.
   - **Caveat:** BLS published no Oct 2025 CPI, so Oct 2026 CPI y/y is approximate. See the "CPI Oct 2026 views" tab of `03_Data/pipelines/Price indexes/Price_Basket_Findings.xlsx`, which uses an interpolated base.
   - Choose the most defensible comparison (approximate 12m, or a 3m-annualized gap where both are published or estimated), justify it, and label it.
   - Deliver `outputs/B_core_gap_oct.csv`.
3. **Headline cross-check:** run your method on headline for Sep and compare it with BEA's Table 9.1U. Use `03_Data/pipelines/Price indexes/Cross-index analysis/raw/BEA_NIUnderlyingDetail_U90100_2026-11-10.json`.
   - The table's months are Dec 2025 – Sep 2026, because Oct and Nov 2025 CPI are missing. Handle that and say how.
   - Deliver `outputs/B_headline_check.csv`. Validating your method this way is what makes the core version defensible.
4. **One-line spoken takeaway candidates,** 2–3 options, data only. For example: "X of the Y pp gap is shelter's lower PCE weight; Z is PCE-only health and financial services." State the size of each piece.

**Inputs, all on disk:**
- PCE: `03_Data/pipelines/Price indexes/PCE/raw/` (U20404, U20405, T20804, Nov 10 vintage) and `PCE/processed/components.csv`.
- CPI: `03_Data/pipelines/Price indexes/CPI/raw/` (BLS item indexes and relative importance).
- Mapping: BEA NIPA Handbook ch. 5, Table 5.B (`Cross-index analysis/raw/BEA_NIPA_Handbook_Chapter5_2026-11-10.pdf`), and BLS's CPI–PCE concordance, if `04_oct_pce_build/code/C_parse_bls_concordance.py` produced one.
- Prior notes: "Hypothesis analysis" and "Summary" tabs of `Price_Basket_Findings.xlsx`.
- If you need a BEA or BLS methodology page that isn't saved, download it to a new `03_Data/Raw/<name>_<date>/` folder.

## Rules
- Verify every claim against a source you opened. Tag each one: [O] opened, [S] search snippet only, [2] secondary. Mark anything unconfirmed "unverified". Never invent numbers, shares or citations.
- Extract PDF text with pypdf, and search it with Python. Run all Python as `python3 -I`. Use scripts in `09_slide1_research/code/B_*.py`, rerunnable from the project root.
- Give every number its reference period, vintage and horizon. **State your mapping assumptions explicitly**, for example which CPI items count as core and how you match items. The decomposition is only as good as the mapping.
- If a clean decomposition isn't possible for some effect, say so and report it as residual. Don't force it.
- Report data only. Don't interpret for policy.
- **Cross-check** with officials (`02_Research/External_views/Fed_officials_2026-11/summary.md`; does anyone discuss the CPI–PCE gap?) and with the 2025 finalists (`02_Research/External_views/Previous_Finalists_copy/`).
- Log irregularities under "Worth a look".
- If a source is paywalled, record the URL in `notes_B.md` under "Paywalled" and continue.
- Use the Write tool with exact absolute paths. Paths contain spaces.

## Output
Save to `./02_Research/Subtasks/09_slide1_research/`:
- `notes_B.md` and `sources_B.md`;
- the CSVs.

Don't write `report.md`. Return your report as your final message, in this structure: Findings · Worth a look · Spot-check examples (3–5) · What to verify.
