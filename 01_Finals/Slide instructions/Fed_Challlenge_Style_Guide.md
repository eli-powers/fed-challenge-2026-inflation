# Fed Challenge deck house style: chart slides. Follow exactly.

Build the chart slide(s) I ask for at the bottom in PowerPoint, using the Excel data I name. Don't change any color, font, size or position listed here. All positions are inches from the slide's top-left corner.

The title slide and the three section slides (Inflation, Employment, Growth & Markets) are already built. Don't edit, move or restyle them.

## 1. Applies to every slide

- **Slide size:** 13.33 × 7.5 in (16:9). If the deck is a different size, stop and tell me before building.
- **Fonts:** Georgia for titles, headings and takeaways. Arial for everything inside charts, note lines and source lines.
- **Nothing extra:** no logo, image, slide number, footer, school name or emblem.

| Color | Hex | Used for |
| --- | --- | --- |
| Navy | #1B2A4A | Title band, headings, note lines, panel titles, takeaways |
| White | #FFFFFF | Title text on the navy band |
| Gold | #F2CC6B | Title text after the colon |
| Light gray | #F2F2F2 | Background of chart slides |
| Red | #C0282D | First data series and its end label |
| Dark navy | #1B2A61 | Second data series and its end label |
| Black | #000000 | Dashed reference line |
| Axis gray | #7F7F7F | X-axis baseline |
| Label gray | #595959 | Axis numbers and dates |
| Source gray | #6B6B6B | Source line |

## 2. Chart slides: shared layout (one-chart and two-chart)

- Background #F2F2F2.
- Title band: rectangle at the very top, full width, 1.01 in tall, fill #1B2A4A, no outline.
- Title: Georgia 32, white, centered in the band. If the title has a colon, make the text after it gold; the colon itself stays white.
- Chart heading: Georgia 21 bold, navy, centered. Box: left 0.67, top 1.09, width 12.00, height 0.61.
- Note line (optional, only if I give one): Arial 13, navy, centered, top 1.63 in. Separate items with " · ".
- Source line: Arial 13, source gray, left-aligned. Box: left 0.73, top 6.00, width 12.00, height 0.47. Format: `Source: <publisher> (<series>). <Units>, <frequency>, through <last month>. Dashed line: <reference label>.` Every month, series ID and unit must match the data.
- Takeaway: Georgia 24 bold italic, navy, centered. Box: left 0.67, top 6.53, width 12.00, height 0.73. Use exactly `[Takeaway: one sentence the team writes]` unless I give the sentence. **Never write, suggest or edit the takeaway yourself.**

## 3. Chart rules (every chart)

- Native PowerPoint chart, built from the Excel tab I name.
- No chart title inside the chart, no legend, no gridlines, no chart fill or border, so the gray page shows through.
- Lines: first series red #C0282D, second series dark navy #1B2A61, 3 pt. No markers, no smoothing. At most two data lines per chart.
- Reference line (if any): black, 2.25 pt, dashed, drawn from the tab's Reference column. It gets no label on the chart; its label goes in the source line ("Dashed line: ...").
- End labels instead of a legend: label each data line's last point with the line's name, to the right of the point, in bold Arial in the line's own color. If two labels overlap, nudge them apart.
- Y-axis: from 0, or the next whole number below the lowest value if the data goes negative, up to the next whole number at or above the highest value (counting the reference value too). Steps of 1; use 2 or 5 if there would be more than 10 steps. Number format 0.00, Arial 12, label gray, no axis line.
- X-axis: dates in YYYY-MM format, labeled every January and July. Gray baseline #7F7F7F, 1 pt. Keep the baseline and dates at the bottom even when values go negative. The first and last points sit on the plot's edges.
- Missing months: bridge the gap with the line, and never plot a missing month as 0.
- Bar charts (if asked): same colors, no gridlines, value labels in Arial 11 above each bar.

## 4. One-chart slide

- Plot area: x 1.53–9.27 in, y 1.80–5.60 in (start at y 2.07 in if there's a note line).
- End labels: Arial 16 bold, starting just right of the plot (about x 9.33 in).
- Date labels: Arial 12.

## 5. Two-chart slide

- Left plot area: x 1.27–5.13 in. Right plot area: x 7.40–11.27 in.
- Both plots end at y 5.60 in. They start at y 2.16 in, or 2.40 in if there's a note line. The two plots are the same size and line up.
- Panel titles: one above each chart, Arial 13 bold, navy, centered over its plot. Top 1.80 in, or 2.07 in if there's a note line.
- End labels: Arial 13 bold, starting about 0.16 in right of each plot. A second line under the name can show the last value, such as "12-month" then "3.4%". Left-chart labels must end before x 6.53 in, so they don't touch the right chart.
- Y-axis: each chart has its own, right-aligned just left of its plot. If both charts use the same units, give them the same range.
- Date labels: Arial 11. Use quarterly labels if a chart covers 2 years or less.
- One source line and one takeaway cover both charts.

## 6. Excel data format (what the prompts expect)

- One data source per tab, starting in A1 with one header row. Use short tab names.
- Column A: real dates (not text), oldest first, one row per month or quarter.
- One column per line. The header is exactly the name shown beside the line.
- Values already in plotting units, such as percent change rather than index levels.
- Missing values are blank cells, never 0, "NA" or ".".
- Optional "Reference" column with the same value in every row, such as 0 or 2.
- No merged cells, notes, totals or blank rows inside the data. Put notes on a separate tab.

## 7. Updating a chart

Charts hold a copy of the data and don't update on their own. When I ask you to refresh a slide, reread its tab and replace the chart data. Recheck the axis range with the rules above, move the end labels to the new last points, and update "through <month>" in the source line. Leave the takeaway alone.

## 8. Check before finishing

- Dashed reference lines sit exactly on their axis values.
- The highest point and last point land on their values against the y-axis.
- End labels sit beside their own lines, don't touch each other, and don't cross into another chart.
- No gridlines, legend, white chart box, logo or slide number.
- Title text sits inside the band, the date labels clear the source line, and the source line clears the takeaway.
- The source line matches the data; the takeaway is the placeholder or my exact sentence.
- The title and section slides are unchanged.

Tell me the axis range used, the last date plotted, and anything that didn't pass.

---
## My request (fill in the parts you need, delete the rest)

**Slide type:** [one-chart / two-chart]

**Place after:** [section name, e.g. "Inflation" section slide]

- **Data:** [tab name] (two-chart: [left tab or columns] / [right tab or columns])
- **Title:** [Label: Story]
- **Chart heading:** [heading]
- **Note line:** [items, or "none"]
- **Panel titles (two-chart only):** [left] / [right]
- **Reference line:** [value and label, or "none"] (two-chart: [left] / [right])
- **Source:** [publisher, series, units, last month]
- **Takeaway:** [our exact sentence, or "placeholder"]