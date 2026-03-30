
import duckdb  # type: ignore
try:
    df = duckdb.sql("SELECT * FROM 'data/processed/master_funnel_data.parquet' LIMIT 1").df()
    print("COLUMNS_FOUND:", df.columns.tolist())
    required = ['is_ytd_started', 'is_ytd_submitted', 'is_ytd_completed', 'is_ytd_admitted', 'is_ytd_deposited', 'is_ytd_deferred']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print("MISSING:", missing)
        exit(1)
    else:
        print("SUCCESS: All required columns found.")
except Exception as e:
    print(e)
    exit(1)
