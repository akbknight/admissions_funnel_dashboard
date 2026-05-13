# Architecture — Kogod Admissions Funnel Dashboard

## System Overview

Single-file Streamlit application with DuckDB in-process analytics. No backend server, no persistent database — DuckDB loads the export CSVs into memory on startup and runs SQL aggregations directly. The application is deployed to Streamlit Cloud from GitHub.

```
Slate CRM Export Files (CSV)
        │
        ▼
data_pipeline.py
  └── DuckDB in-process
      └── funnel_logic.sql queries
        │
        ▼
app.py (Streamlit)
  ├── Filter controls (program, date range, decision type)
  ├── KPI cards (funnel stage counts + YoY deltas)
  ├── Plotly bar charts (stage comparison)
  └── Plotly trend charts (applications over time)
        │
        ▼
Streamlit Cloud (GitHub Pages equivalent for Python apps)
```

---

## File Structure

```
admissions_funnel_dashboard/
├── app.py                  ← Streamlit entry point, all UI logic
├── data_pipeline.py        ← DuckDB connection, data loading, query runner
├── requirements.txt        ← Pinned dependencies
├── sql/
│   └── funnel_logic.sql    ← Core YoY comparison query with date anchoring
├── data/
│   ├── raw/                ← Source export files (not committed — local only)
│   └── processed/          ← Processed outputs
└── docs/
    ├── methodology.md
    ├── architecture.md
    └── decision_log.md
```

---

## Data Flow

1. **Load** (`data_pipeline.py`): DuckDB reads CSV exports from `data/raw/` into in-memory tables
2. **Query** (`sql/funnel_logic.sql`): Funnel stage aggregation with YoY file-date anchoring
3. **Transform** (`data_pipeline.py`): Query results returned as Pandas DataFrames
4. **Render** (`app.py`): Streamlit renders KPI cards and Plotly charts from DataFrames

DuckDB operates entirely in-process — the Python process IS the database. There is no separate DuckDB server.

---

## Display Logic

```python
# In app.py — automatic view switching
if selected_program == "All Programs":
    render_tab_view(df)        # One tab per program
else:
    render_single_program_view(df, selected_program)  # Expanded single-program view
```

Session state preserves filter selections across Streamlit rerenders without full page reload.

---

## Deployment

- **Host**: Streamlit Cloud (automatic redeploy on push to main)
- **Live URL**: https://admissionsfunneldashboard-8pbzttpynneixaywcls7rx.streamlit.app/
- **Data**: Export files are loaded from the deployed environment; not stored in the repo (contains student records)
- **Environment**: Python 3.9+, dependencies from `requirements.txt`

---

## Design Decisions

- **DuckDB over SQLite**: DuckDB's columnar engine is faster for the analytical aggregation pattern (group-by + sum across 50K+ rows). SQLite is optimized for OLTP, not OLAP.
- **Custom CSS**: Streamlit's default layout wastes vertical space for a dense analytics dashboard. Custom CSS reduces padding and font sizes to keep the full funnel visible without scrolling on 1440px displays.
- **Plotly over Altair**: Plotly provides better control over dual-axis charts (bar + line on the same plot) which is required for the trend view.
