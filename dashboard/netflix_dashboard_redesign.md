# Netflix Dashboard Visual Redesign

## Current Report Inventory

- Canvas: 1280 x 720, one page.
- Header: centered title and subtitle.
- KPI cards: Total Titles, Total Movies, Total TV Shows.
- Charts: Movies vs TV Shows donut, rating distribution bar, catalog growth line, top release years bar.
- Notes: key insights text block and rating glossary text block.

## Main Visual Direction

Make the report feel like a polished streaming analytics dashboard instead of a default chart canvas.

- Use a near-black canvas: `#0B0B0F`.
- Use dark visual panels: `#151519`.
- Use Netflix red only for primary emphasis: `#E50914`.
- Use white/off-white text: `#F5F5F1`.
- Use gray for supporting labels and axes: `#8C8C8C`.
- Keep borders subtle: `#2A2A30`, 6 px radius.

## Large-Screen Layout

Recommended 1280 x 720 structure:

- Top band, y 24-92:
  - Left-aligned title: `Netflix Content Analytics`
  - Subtitle below: `Azure Data Engineering Project | ADF + ADLS Gen2 + Databricks + Unity Catalog + Power BI`
  - Remove centered title positioning; left alignment reads more like an executive product dashboard.

- KPI row, y 112-220:
  - `Total Titles`
  - `Movies`
  - `TV Shows`
  - Optional derived card: `Movie Share %`
  - Cards should have equal width, aligned baselines, and large numeric values.

- Middle row, y 248-470:
  - Left 65%: `Netflix Catalog Growth by Release Year`
  - Right 35%: `Content Mix`
  - The time trend deserves more space than the donut because it carries the strongest story.

- Bottom row, y 500-690:
  - Left 50%: `Top Release Years`
  - Right 50%: `Distribution by Content Rating`
  - Use horizontal bars for both, sorted descending, with direct labels.

## Chart-Specific Fixes

- `Content Mix: Movies vs TV Shows`
  - Keep donut only because it has two categories. Use two high-contrast colors: red for Movies, gray for TV Shows.
  - Show percent labels directly. Remove legend if labels are clear.

- `Distribution by Content Rating`
  - Keep as horizontal bar chart.
  - Sort by total titles descending.
  - Use neutral gray bars and highlight the largest rating in red.
  - Add data labels at the end of bars.

- `Netflix Catalog Growth by Release Year`
  - Increase height to at least 220 px.
  - Use a red 3 px line.
  - Add an annotation around the peak year instead of explaining everything in a paragraph.
  - Light gridlines only; no heavy axis titles.

- `Highest-Volume Release Years`
  - Change title to `Top Release Years by Title Count`.
  - If years are categorical top-N, use vertical columns. If comparing exact rankings, use horizontal bars.
  - Limit to top 10 for readability unless the report is exploratory.

- `Key Insights`
  - Replace the long paragraph with 3 short bullets or 3 callout chips.
  - Example:
    - Movies dominate the catalog.
    - Catalog volume accelerated after 2015.
    - Mature and parental-guidance ratings represent a large share.

## Mobile Layout

Power BI mobile view should be manually arranged in this order:

1. Title and subtitle.
2. Total Titles KPI.
3. Movies and TV Shows KPI cards.
4. Catalog Growth line chart.
5. Content Mix donut.
6. Top Release Years.
7. Rating Distribution.
8. Three short insight bullets.
9. Rating note.

Avoid placing the full desktop canvas in mobile view. Use single-column cards and charts with at least 44 px tap targets.

## Import Steps

1. Open the PBIX in Power BI Desktop.
2. Go to `View` > `Themes` > `Browse for themes`.
3. Select `dashboard/netflix_powerbi_theme.json`.
4. Reposition visuals using the large-screen layout above.
5. Open Mobile layout and arrange visuals using the mobile order above.

## QA Checklist

- No chart title wraps awkwardly.
- No text overlaps at 1280 x 720.
- All charts show values without requiring hover.
- Red is used for emphasis, not every mark.
- Mobile view is manually designed, not auto-generated.
- Rating note stays visible but does not compete with the main charts.
