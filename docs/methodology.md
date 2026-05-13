# Methodology — Kogod Admissions Funnel Dashboard

## Problem Context

Admissions leadership at Kogod School of Business needs to track the Fall 2026 recruiting pipeline against the same point in the Fall 2025 cycle. The core measurement challenge is comparison anchoring: a raw "applications received" count on March 1, 2026 is not comparable to the full-year 2025 total. Meaningful YoY comparison requires restricting both cycles to records with matching file dates — the same point in the recruiting timeline.

---

## Data Source

Input data comes from the Slate CRM system as two export files per cycle:
- **Prospects / Inquiries**: Records of students who have shown initial interest (website forms, events, recruiter contacts)
- **Applications / Decisions**: Records of submitted applications with current decision status

The dashboard processes these exports using `data_pipeline.py`, which loads them into DuckDB and applies the funnel logic.

---

## Funnel Stage Definitions

| Stage | Definition |
|-------|-----------|
| Inquiries | Student record entered in Slate via any lead source |
| Applications Started | Application opened but not yet submitted |
| Applications Submitted | Complete application received |
| Complete | Application complete (all required materials received) |
| Decision — Admit | Admissions decision: Admit |
| Decision — Deny | Admissions decision: Deny / Withdraw |
| Decision — Defer | Admissions decision: Deferred to next cycle |
| Enrolled | Student confirmed enrollment and paid deposit |

---

## Year-Over-Year Comparison Logic

The comparison is anchored to file date. For each record in Fall 2026, the comparison includes only Fall 2025 records with a file date ≤ the same calendar date (month-day) in 2025. This is implemented in `sql/funnel_logic.sql`:

```sql
WHERE STRFTIME('%m-%d', file_date_2025) <= STRFTIME('%m-%d', CURRENT_DATE)
```

This ensures that "Applications as of March 1, 2026" is compared to "Applications as of March 1, 2025" — not the full 2025 cycle total.

---

## Aggregation

DuckDB handles all aggregation in-process — no separate database server required. The full funnel query (`sql/funnel_logic.sql`) runs in under 100ms against typical export sizes (5,000–50,000 records). Pandas is used only for final DataFrame construction and Plotly input formatting.

---

## Program-Level Drill-Down

The dashboard automatically switches between two display modes:
- **Tab view (All Programs)**: When no program filter is active — shows one tab per program with KPI cards and charts
- **Single Program view**: When a specific program is selected — shows expanded analysis for that program with trend charts by application date

The filter state drives the mode switch in Streamlit's session state, keeping the UI clean without requiring a separate navigation structure.

---

## KPI Delta Logic

KPI cards display both the absolute delta (Fall 2026 minus Fall 2025) and the percentage delta. The percentage is calculated as:

```
delta_pct = (value_2026 - value_2025) / value_2025 × 100
```

Zero-division (when 2025 value is 0) is handled by displaying "N/A" rather than infinity.
