# Decision Log — Kogod Admissions Funnel Dashboard

## Decision 1: DuckDB over SQLite for analytics layer

**Decision:** Use DuckDB as the in-process analytics engine rather than SQLite or Pandas alone.

**Rationale:** The core operations are analytical — group-by aggregations, window functions for YoY date matching, sum across 50K+ rows. DuckDB's columnar execution engine handles these patterns significantly faster than SQLite's row-oriented engine. It also supports full SQL including `STRFTIME` date functions and `QUALIFY` for window filtering, which the date-anchoring logic requires.

**Tradeoff:** DuckDB adds a dependency. The alternative would be pure Pandas groupby operations, but implementing the date-anchoring logic in Pandas requires multi-step operations that are harder to audit and test than a single SQL query.

---

## Decision 2: File-date anchoring for YoY comparison

**Decision:** Anchor YoY comparisons to the same calendar date (month-day) across cycles rather than comparing raw totals.

**Rationale:** Comparing "total applications by end of Fall 2025" to "applications to date in Fall 2026" produces a meaningless delta — the 2025 cycle is complete while 2026 is in-progress. The correct comparison is "applications received by March 1, 2025" vs. "applications received by March 1, 2026." Slate export files include `file_date` which enables this anchoring in SQL.

**Tradeoff:** Requires that export files include the `file_date` field. If a one-off export omits this field, the comparison reverts to raw totals. The pipeline validates for this field on load.

---

## Decision 3: Automatic Tab/Single-Program view switching

**Decision:** The dashboard switches between an all-programs tab view and a single-program expanded view based on the program filter selection, rather than using explicit navigation tabs or pages.

**Rationale:** Admissions leadership uses the dashboard in two modes: a quick executive scan across all programs (tab view) and a deep drill-down into one program. A single filter control drives both modes without requiring the user to navigate to a different page or click an extra button.

**Tradeoff:** The automatic switching may be surprising to users who select a program filter and expect the tab view to simply filter — instead the entire layout changes. This is mitigated by a brief mode label shown in the dashboard header.

---

## Decision 4: Custom CSS density optimization

**Decision:** Override Streamlit's default padding and font sizes with custom CSS to maximize information density.

**Rationale:** The full admissions funnel has 8 stages × 2 years × 4+ programs. Default Streamlit padding uses approximately 40% of vertical space on margins and gaps. The target audience (admissions directors) is comfortable reading dense tables; the priority is seeing the full funnel without scrolling on a standard 1440px laptop screen.

**Tradeoff:** Custom CSS may break on future Streamlit versions if class names change. The styling is isolated to a single `st.markdown()` block, making it easy to identify and update.

---

## Decision 5: Streamlit over Dash or a custom Flask app

**Decision:** Use Streamlit for the dashboard framework rather than Plotly Dash or a custom Flask + Plotly application.

**Rationale:** Streamlit Cloud provides zero-config deployment from GitHub — the audience is admissions staff, not engineers. A Flask app would require managing a server (Docker, Heroku, or similar). Dash is more flexible but requires explicit callback wiring for every interactive element. Streamlit's reactive model (reruns the script on filter change) is a better match for a single-page analytics dashboard with modest interactivity requirements.

**Tradeoff:** Streamlit is slower to rerender on filter change than Dash (full script rerun vs. partial callback). For a 50K-row dataset, the DuckDB query completes in <100ms; the total rerender time is dominated by Plotly chart rendering (~300ms), which is acceptable for this use case.
