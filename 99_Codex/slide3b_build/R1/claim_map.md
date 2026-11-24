# Claim map — slide3b_build R1
All paths below refer to fresh copies under this R1 directory unless stated otherwise.

| Load-bearing claim / location | Evidence | Independent check |
|---|---|---|
| report.md, Slide content: four actual quarters 2.49, 3.94, 3.31, 2.47 | raw/2026-11-16/PCEPILFE_observations.json; workbook Raw_PCE B2:B16 | Quarterly-average index ratios, fourth power; audit_check.py and audit_results.json |
| Five SPF quarterly medians 3.00, 2.7106, 2.60, 2.4141, 2.361 | medianLevel.xlsx COREPCE, YEAR=2026 QUARTER=4, COREPCE2:6 | Direct openpyxl extraction; current official SPF release agrees at its displayed precision |
| Post-pandemic scenario values | nov26_base.xlsx and feb26_base.xlsx, 2tab BREPUUS; EIA_RBRTEd.xls Data 1; config/regime_response.csv | Both paths independently recomputed from monthly/daily raw data, log gaps and response convolution; no pipeline imports |
| Annual values 2.8%, 2.5%, 2.3% | Forecast C7:E10; Q4Q4_2027 B2:B4 | Product of four annualized quarterly gross rates to power 1/4 |
| SPF annual 2.5213 versus published 2.50 | COREPCEB; Q4Q4_2027 B6 and A7 explanation | Both round to 2.5%; compounded median quarterly path distinguished from annual-question median |
| November STEO proxy precedes survey deadline | saved spf-release-dates.txt and page_steo_outlook.html; live official pages | Nov 10 release < Nov 11 deadline; survey released Nov 16 |
| Native chart faithfully copies workbook | ppt/charts/chart21.xml; embedded Microsoft_Excel_Sheet7.xlsx | All 22 nonblank points and missing-value positions checked independently |
| Source line and economic interpretation | slide400.xml; official FRED, SPF, EIA, FEDS accessible table | Correct publishers, units, dates; no probabilities or changed-price-setting assertion |
| Shading, labels and source/takeaway clearance | deck_3b.pdf page 12; independent_pdf_slide12.png | Independent PDFKit render; shade x=488..1032 pixels agrees with RENDER_X and Q3 fork |
| Slides 1–11 unchanged | prior slide3a R3 final-state deck copied to comparison/slide3a_final.pptx | XML and relationships byte-identical under 300→9, 301→10, 302→11 renaming; other old content parts unchanged |

External checks are preserved in external/web_evidence.json. Direct shell downloads were unavailable (DNS); web-tool access succeeded. No raw research note claim was added solely on plausibility.
