-- Standardize Term
CREATE OR REPLACE MACRO normalize_term(t) AS CASE
    WHEN t LIKE '%2025%' THEN 'Fall 2025'
    WHEN t LIKE '%2026%' THEN 'Fall 2026'
    ELSE t
END;

-- Clean Residency
CREATE OR REPLACE MACRO clean_residency(r) AS CASE
    WHEN r LIKE '%International%' THEN 'International'
    WHEN r LIKE '%Domestic%' THEN 'Domestic'
    WHEN r IS NULL THEN 'Unknown'
    ELSE 'Domestic' -- Fallback/Assumption
END;

-- Master Funnel Logic
SELECT
    *,
    -- Funnel Flags (Cumulative)
    CASE WHEN started_date IS NOT NULL THEN 1 ELSE 0 END as is_started,
    CASE WHEN submitted_date IS NOT NULL THEN 1 ELSE 0 END as is_submitted,
    CASE WHEN completed_date IS NOT NULL THEN 1 ELSE 0 END as is_completed,
    CASE WHEN admitted_date IS NOT NULL THEN 1 ELSE 0 END as is_admitted,
    CASE WHEN deposited_date IS NOT NULL THEN 1 ELSE 0 END as is_deposited,
    
    -- Point-in-Time Comparison Flags (YoY)
    -- Logic: If term is 'Fall 2025', count ONLY if event happened by same M/D last year
    -- 'Fall 2026' data is always "current" so we take it as is (up to today)
    
    -- We will inject 'cutoff_date_2025' and 'cutoff_date_2026' as parameters in Python or use a fixed date check here if dynamic
    -- For now, we compute raw flags. The filtering happens in the aggregation layer or via dynamic WHERE clauses.
    -- Better yet, let's pre-calculate 'compare_date' matching the unified timeline.
    
    COALESCE(deposited_date, admitted_date, completed_date, submitted_date, started_date) as last_activity_date

FROM raw_funnel_data
WHERE application_status NOT IN ('Withdrawn', 'Denied', 'Deferred') -- Basic "Still in Play" filter
