# Project Plan — Kogod Admissions Funnel Dashboard

## Objective

Build an executive-level admissions analytics dashboard for Kogod School of Business that gives admissions leadership a real-time view of the Fall 2026 pipeline versus the same point in Fall 2025. The comparison must be anchored to matching file dates so the delta reflects actual recruiting momentum, not cycle completion differences.

## Scope

### In Scope
- Full 8-stage funnel tracking: Inquiry → Application Started → Submitted → Complete → Admit/Deny/Defer → Enrolled
- Year-over-year comparison with file-date anchoring
- Program-level drill-down (automatic view switching)
- KPI cards with absolute and percentage deltas
- Plotly bar and trend charts with AU brand colors
- Streamlit Cloud deployment

### Out of Scope
- Direct Slate CRM integration (data comes via manual CSV export)
- Predictive enrollment modeling
- Student-level record display (aggregate only)
- Email or notification triggers

## Architecture

Streamlit + DuckDB in-process. No server required. DuckDB loads CSVs at startup, runs SQL aggregations for funnel stages and YoY comparison, returns DataFrames to Streamlit for rendering.

## Execution Phases

### Phase 1 — Core Dashboard (Complete)
- [x] DuckDB data pipeline with funnel_logic.sql
- [x] File-date anchored YoY comparison
- [x] KPI cards with delta logic
- [x] Plotly charts (bar + trend)
- [x] Tab view + Single Program view switching
- [x] Custom CSS density optimization
- [x] Streamlit Cloud deployment

### Phase 2 — Documentation (Complete)
- [x] docs/methodology.md — funnel stages, date anchoring, aggregation, KPI delta logic
- [x] docs/architecture.md — data flow, DuckDB pattern, file structure, deployment
- [x] docs/decision_log.md — 5 decisions: DuckDB, date anchoring, view switching, CSS, Streamlit
- [x] PROJECT_PLAN.md, FINAL_REVIEW.md

## Success Criteria

- [x] YoY comparison anchored to matching file dates (not raw totals)
- [x] Automatic view switching based on program filter state
- [x] Full funnel visible without scrolling at 1440px
- [x] Deployed to Streamlit Cloud
- [x] No AI-generated residue in repository
