# Final Review — Kogod Admissions Funnel Dashboard

## Summary

Executive-level Streamlit dashboard for Kogod School of Business admissions leadership. Tracks the full 8-stage application funnel for Fall 2026 vs. Fall 2025 with year-over-year comparison anchored to matching file dates. Uses DuckDB in-process analytics for fast aggregation. Deployed to Streamlit Cloud.

---

## What Was Built

### Core Analytics
- **Data pipeline** (`data_pipeline.py`): DuckDB loads Slate CRM export CSVs; runs `sql/funnel_logic.sql` for funnel aggregation with date anchoring
- **YoY date anchoring**: Comparison restricted to records with `STRFTIME('%m-%d', file_date) <= STRFTIME('%m-%d', CURRENT_DATE)` — ensures Fall 2026 vs. Fall 2025 at the same point in the recruiting cycle
- **Funnel stages**: Inquiries → Applications Started → Submitted → Complete → Admit / Deny / Defer → Enrolled
- **KPI delta logic**: Absolute delta + percentage delta per stage; zero-division handled with N/A display

### UI
- **Tab view**: When no program filter — one tab per program with KPI cards and bar charts
- **Single Program view**: When program selected — expanded analysis with trend chart by application date
- **Custom CSS**: High-density layout keeping full funnel visible at 1440px without scrolling
- **AU brand colors**: Dashboard uses American University brand color scheme

### Tech Stack

| Layer | Technology |
|-------|-----------|
| App framework | Streamlit |
| Analytics | DuckDB + Pandas |
| Charts | Plotly Express / Plotly Graph Objects |
| Styling | Custom CSS, Inter font |
| Deployment | Streamlit Cloud |

---

## Documentation Added

- `docs/methodology.md` — funnel stage definitions, date anchoring logic, KPI delta math, DuckDB rationale
- `docs/architecture.md` — data flow, file structure, display logic, deployment
- `docs/decision_log.md` — 5 decisions: DuckDB, date anchoring, view switching, CSS density, Streamlit

---

## Stray Files Removed

- `check_deferred.py`, `check_deferred_2.py` — ad-hoc analysis scripts
- `cols.txt` — column inspection artifact
- `extract_cols.py`, `verify_cols.py` — one-off data exploration scripts
- `R` — stray file from exploratory work

---

## Deployment

- Live URL: https://admissionsfunneldashboard-8pbzttpynneixaywcls7rx.streamlit.app/
- Streamlit Cloud redeploys automatically on push to main
- Data files are NOT committed to the repo (contain student records)

---

## Known Limitations

1. Data loading requires manual CSV export from Slate — no direct CRM integration
2. Date anchoring depends on `file_date` field being present in exports
3. Rerender speed (~300ms) is dominated by Plotly chart rendering, not DuckDB query time
