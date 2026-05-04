# Kogod Admissions Funnel Dashboard

An executive-level admissions analytics dashboard tracking the full application funnel for Kogod School of Business programs — with year-over-year comparison and program-level drill-down.

## What this project does

This Streamlit dashboard gives admissions leadership a real-time view of where the Fall 2026 pipeline stands relative to the same point in Fall 2025. It tracks every stage of the funnel — inquiry, application, decision, and enrollment — broken out by program, application date, and decision type.

The comparison logic is anchored to strict file-date matching so that Fall 2026 vs. Fall 2025 comparisons reflect the same point in the recruiting cycle, not raw end-of-cycle totals. The UI switches automatically between an aggregate view (all programs) and a program-level drill-down based on the active filter state, keeping the dashboard readable at any analysis level.

## Key features

- Year-over-year funnel comparison anchored to matching file dates across cycles
- Automatic Tab view (all programs) / Single Program view switching based on filter selection
- KPI cards with absolute and percentage deltas for each funnel stage
- Plotly-powered bar and trend charts with AU brand color scheme
- DuckDB in-memory SQL for fast aggregation across large export files
- High-density custom CSS layout — full funnel visible without scrolling on 1440px
- Streamlit Cloud compatible — deploys from GitHub with no infrastructure setup

## Tech stack

| Layer | Technology |
|---|---|
| App framework | Streamlit |
| Data layer | DuckDB + Pandas |
| Charts | Plotly Express / Plotly Graph Objects |
| Fonts | Inter (Google Fonts) |
| Styling | Custom CSS with AU brand colors |
| Deployment | Streamlit Cloud |

## How to run

```bash
# Clone the repository
git clone https://github.com/akbknight/admissions_funnel_dashboard.git
cd admissions_funnel_dashboard

# Install dependencies
pip install -r requirements.txt

# Start the dashboard
streamlit run app.py
# Opens at http://localhost:8501
```

**Requirements:** Python 3.9+. Place the export files in the expected directory structure before running — see the `Foundation_Data/` folder for format reference.

## Data and methodology

- Source: Admissions export files from the Kogod School of Business application system
- Comparison logic: File dates matched between Fall 2026 and Fall 2025 export timestamps
- No personally identifiable information is included or displayed — all data is aggregate-level

## Skills demonstrated

- **Business analytics:** funnel analysis, year-over-year cohort comparison, enrollment pipeline reporting
- **Data engineering:** DuckDB in-process SQL for multi-file aggregation, Pandas-based cleaning and transformation
- **Executive dashboarding:** high-density UI design for stakeholder-facing reporting, Plotly chart composition
- **Streamlit:** production-ready app structure, custom CSS theming, cloud deployment

## Author

**Akshay Kumar**
[linkedin.com/in/akshaykumardl](https://www.linkedin.com/in/akshaykumardl/)
