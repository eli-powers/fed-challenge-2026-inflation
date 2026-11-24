# Slide build prompt (reusable, inflation section)

**Status: FIRST DRAFT (Nov 15, 2026).** Placeholders in `[brackets]` stay until Eli edits them on Nov 16. Don't treat any bracketed item as decided.

**How to use:** copy everything below the line into a new chat, fill in the brackets, and delete what doesn't apply. It generalizes Eli's Nov 15 slide 1 instructions and the decisions and fixes from that build.

**Before using it:** the slide's research has converged (audit-loop), and its interpretation calls (S[N]-E1, S[N]-E2…) are locked with Eli. Slide design starts only after that, per Eli's slide workflow.

---

## Task: build Inflation slide [N], "[Label: Story]"

**Step 0. Restate and ask, then stop.**
- Restate the task in 3–4 sentences.
- Ask every clarifying question now, including final design quirks, so we limit iteration later. Use the checklist at the end.
- Wait for my answers before building.

**Verbal cues to add to the tracker** (`01_Finals/speaker_notes/verbal_cues_and_script_notes.md`, slide [N] section): [cues, or "none"]

### 1. Workbook
- Create `01_Finals/Slide data/Inflation Slide [N].xlsx`.
- It holds all the raw data behind the slide's contents (every graph and every number), with its source.
- Confirm it is accurate:
  - recompute from the raw files;
  - cross-check against the audited research outputs in `[02_Research/Subtasks/NN_slide[N]_research/outputs/…]`.
- Format:
  - chart tabs follow the guide's s.6 format;
  - values are live formulas over a raw tab, wherever practical;
  - a `Notes` tab maps every slide element (title, heading, panel titles, end labels, axis range, window, source line, takeaway) to where it comes from.
- **Main concern: verifiability and reproducibility.** Every input that populates a visual traces directly to this workbook, and the workbook traces to a saved raw file and a script.

### 2. Formatting
- Read David's style guide: `01_Finals/Slide instructions/Fed_Challlenge_Style_Guide.md`.
- Apply the parts that fit this slide.
- My rules override it where they conflict. Flag every conflict, and anything in the guide that changes how you work (e.g. pulling data from a different workbook).

### 3. Build slide [N]
- **Where:** add it to our working deck, `01_Finals/slides/Inflation Slides (working).pptx`, after slide [N−1].
- **Don't touch:**
  - the team deck (`01_Finals/slides/Finals/Slides.pptx`);
  - the Inflation section slide;
  - earlier slides in the working deck.
- I'll copy and paste the slide into the team presentation by hand. Tell me if that creates any conflicts (template, linked vs embedded charts, theme).
- **Build approach:** scripted, in `02_Research/Subtasks/[NN]_slide[N]_build/code/`.
  - Reuse `10_slide1_build/code/build_inflation_slide1.py` as the template; don't start from scratch.
  - The script writes a `verify_report.txt`.
- **Slide spec** (the guide's "My request" block):
  - **Slide type:** [one-chart / two-chart]
  - **Data:** [tab(s)] (two-chart: [left] / [right])
  - **Title:** [Label: Story]
  - **Chart heading:** [heading, or "draft one for me to confirm"]
  - **Panel titles (two-chart):** [left] / [right]
  - **Series and colors:** [series → color]
  - **Window:** [start–end]. The same on both panels unless I say otherwise.
  - **Y-axis:** [range, or "default per guide"]. The same range on both panels if units match.
  - **Reference line:** [e.g. 2% target dashed, or "none"]
  - **End labels:** [name / value format, e.g. "Core / 3.24%*"]
  - **Note line:** [items, or "none"]
  - **Source:** [publisher, series, table, units, last month]
  - **Takeaway:** [my exact sentence, or "placeholder"]. Never write it yourself.
  - **Versions:** [guide layout only / guide + wide]

### 4. Audit
- Run `/audit-loop` on slide [N] (task `slide[N]_build`).
- No subagents are needed for this development.

### Done when
- The "Inflation Slide [N]" workbook holds every number on the slide with its source.
- Slide [N] is built in our working .pptx per David's formatting, with my rules overriding where they conflict.
- The build checks pass and the slide is rendered in Microsoft PowerPoint.
- The audit-loop has converged.
- The report lists: the axis range used, the last date plotted, the deviations from the guide, and anything that didn't pass.

---

## Standing rules from slide 1 (apply unless the spec above says otherwise)
- **Estimates:** mark any estimated value (e.g. our bottom-up October build) with an asterisk on the end label, e.g. "3.24%*".
  - Add a footnote in the source line: "*[Month] = UMD estimate built from [inputs]."
  - No "est." text on the chart.
- **Windows:** the same date window on every panel of a slide. Changing windows across panels reads as cherry-picking; flag it if the data argue for it.
- **Placeholders:** the takeaway stays the placeholder until I give the sentence. A drafted heading is labelled as a draft in report.md and in STATUS "Judgment calls for Eli".
- **Data cutoff:** Nov 18. Note in report.md which numbers need re-pulling after the last releases, and which script rebuilds them.
- **Re-audits:** a change that is layout-only (no numbers changed or added) needs only the build checks, not a new audit round, and only once I say so.
- **Script consistency:** after the build, list any spoken figure in `script_final.md` that differs from the slide (rounding, dates, wording).

## Build notes (known PowerPoint/Excel quirks from slide 1)
- **Charts:** native and embedded, not linked, so the copy-paste into the team deck keeps the data.
  - Line series: `smooth=False`. Bar series: `invertIfNegative=False`.
  - Use `crossBetween=midCat` so the first and last points sit on the plot edges.
  - Position the plot area with an inner manualLayout so the guide's plot coordinates hold.
- **Date labels:**
  - Use text category labels ("YYYY-MM" on the label months, a single space " " otherwise, never an empty string, which writes "None").
  - Set `bodyPr wrap="none"`, because PowerPoint wraps "2024-01" at the hyphen and shrinks the plot.
  - The workbook tabs keep real dates.
- **Deck edits:** renumber the kept slide's partname before adding slides, to avoid duplicate zip entries. Confirm the section slide's XML is unchanged.
- **Rendering:**
  - Check in Microsoft PowerPoint (AppleScript export to PDF, via the project folder because of the sandbox), not only LibreOffice.
  - Check against the guide's s.8 list.
- **Workbook:** set `fullCalcOnLoad=True`. Verify the recalculated formulas against the script's values.

## Clarifying-question checklist (Step 0)
1. Panel structure: which series go on which panel, and why that split?
2. Window and frequency: same on all panels? m/m, 3m, 6m or 12m?
3. Axis: default range, or fixed? Does the peak fit?
4. Labels: end-label format, estimate marking, and any callouts?
5. Title, heading and panel titles: Eli's wording, or a draft?
6. Source line: exact wording and footnotes.
7. Takeaway: placeholder or sentence?
8. Versions: guide layout, wide, or both?
9. Anything on the slide that should be verbal only, or backup?
10. Conflicts with the guide or with earlier slides (colors, series names, units)?
11. [Eli: add slide-specific questions]
