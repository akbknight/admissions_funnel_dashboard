import pandas as pd  # type: ignore
import duckdb  # type: ignore
import os
from datetime import datetime
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "master_funnel_data.parquet")

# File Paths
F26_FILE = os.path.join(RAW_DIR, "Fall 2026 Application Data as of 2.13.26.xlsx")
F25_FILE = os.path.join(RAW_DIR, "Recruit Exported Enrollment - F25 to F26 - AI Opp Funnel.xlsx")

def ingest_data():
    """Reads Excel files and normalizes columns."""
    logger.info("Reading Fall 2026 data...")
    # Based on cols.txt: 'Application ID' is key
    con = duckdb.connect()
    
    # Read F26
    # Columns map: 'Application ID' -> id, 'Learning Program Lookup' -> program, 'Academic Term' -> term
    # Dates: 'Application Started Date', 'Submitted', 'Completed', 'Admitted', 'Deposit Date'
    logger.info(f"Loading {F26_FILE}...")
    df_f26 = pd.read_excel(F26_FILE)
    
    # Force Date Conversion
    date_cols_f26 = [
        "Application Started Date", "Applied Date", 
        "Application Complete Date", "Admitted Date", "Deposit Date",
        "Deferred Date"
    ]
    for col in date_cols_f26:
        if col in df_f26.columns:
            df_f26[col] = pd.to_datetime(df_f26[col], errors='coerce')
    
    # Read F25 (Recruit Export)
    # Columns map: 'erpid...' -> id, 'Academic Program...' -> program, 'Entry Term...' -> term
    # Dates: 'Started', 'Submitted', 'Marked Completed On', 'Admitted', 'Confirmed' (Deposit)
    logger.info(f"Loading {F25_FILE}...")
    df_f25 = pd.read_excel(F25_FILE)

    # Force Date Conversion
    date_cols_f25 = [
        "Started (Opportunity) (Opportunity)", 
        "Submitted (Opportunity) (Opportunity)", 
        "Marked Completed On (Application) (Application)", 
        "Admitted (Opportunity) (Opportunity)", 
        "Confirmed (Opportunity) (Opportunity)",
        "Deferred (Opportunity) (Opportunity)"
    ]
    for col in date_cols_f25:
        if col in df_f25.columns:
            df_f25[col] = pd.to_datetime(df_f25[col], errors='coerce')

    return df_f26, df_f25

def process_data(df_f26, df_f25):
    """Clean and unify datasets using DuckDB."""
    con = duckdb.connect()
    con.register('df_f26', df_f26)
    con.register('df_f25', df_f25)

    logger.info("Standardizing schemas...")
    
    # --- TASK 3: DIAGNOSTICS ---
    logger.info("F26 Raw Residency Diagnostics:")
    for col in ["Citizenship Status", "Country of Citizenship", "Is F1 or J1 Visa Required"]:
        if col in df_f26.columns:
            logger.info(f"Unique values in '{col}': {df_f26[col].dropna().unique().tolist()[:10]}")
    
    # Unify F26
    query_f26 = """
        SELECT 
            CAST("Application ID" AS VARCHAR) as id,
            'Fall 2026' as term,
            "Learning Program Lookup" as program,
            CASE 
                WHEN "Citizenship Status" IN ('International', 'Non-U.S. Citizen', 'Non-Citizen', 'Foreign National') THEN 'International'
                WHEN CAST("Is F1 or J1 Visa Required" AS VARCHAR) IN ('Yes', 'TRUE', '1', 'True', 'true') THEN 'International'
                WHEN "Country of Citizenship" IS NOT NULL AND "Country of Citizenship" NOT IN ('United States', 'US', 'USA', 'U.S.', 'United States of America', '') THEN 'International'
                WHEN "Citizenship Status" IN ('U.S. Citizen', 'Domestic', 'Permanent Resident', 'US Citizen') THEN 'Domestic'
                ELSE 'Unknown'
            END as residency,
            "Application Status" as status,
            "Application Substatus" as substatus,
            CAST("Application Started Date" AS DATE) as started_date,
            CAST("Applied Date" AS DATE) as submitted_date,
            CAST("Application Complete Date" AS DATE) as completed_date,
            CAST("Admitted Date" AS DATE) as admitted_date,
            CAST("Deposit Date" AS DATE) as deposited_date,
            CAST("Deferred Date" AS DATE) as deferred_date,
            'F26' as source_system
        FROM df_f26
    """
    
    # Unify F25
    # Mapping 'Confirmed' to 'deposited_date'
    query_f25 = """
        SELECT 
            CAST("erpid (Prospect) (Person)" AS VARCHAR) as id,
            'Fall 2025' as term,
            "Academic Program (Application) (Application)" as program,
            CASE 
                WHEN "Primary Non-U.S. Citizenship (Application) (Application)" IS NOT NULL THEN 'International'
                WHEN "a26 Are you a U.S. Citizen? (Application) (Application)" = 'Yes' THEN 'Domestic'
                ELSE 'Domestic' 
            END as residency,
            "Folder Status" as status,
            NULL as substatus,
            CAST("Started (Opportunity) (Opportunity)" AS DATE) as started_date,
            CAST("Submitted (Opportunity) (Opportunity)" AS DATE) as submitted_date,
            CAST("Marked Completed On (Application) (Application)" AS DATE) as completed_date,
            CAST("Admitted (Opportunity) (Opportunity)" AS DATE) as admitted_date,
            CAST("Confirmed (Opportunity) (Opportunity)" AS DATE) as deposited_date,
            CAST("Deferred (Opportunity) (Opportunity)" AS DATE) as deferred_date,
            'F25' as source_system
        FROM df_f25
    """

    # Union
    unified_query = f"""
        SELECT * FROM ({query_f26}) 
        UNION ALL 
        SELECT * FROM ({query_f25})
    """
    
    con.execute(f"CREATE OR REPLACE TABLE master_raw AS {unified_query}")
    
    logger.info("Applying Transformation Logic...")
    
    # Calculate Cutoff Date for YoY based on File Name or Mod Time
    # Logic: If file is " ... as of 2.13.26", use 2026-02-13 as the anchor.
    base_name = os.path.basename(F26_FILE)
    import re
    date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{2})', base_name)
    
    if date_match:
        m, d, y = date_match.groups()
        # Assume 20xx
        anchor_date = datetime.strptime(f"20{y}-{m}-{d}", "%Y-%m-%d")
        logger.info(f"Derived Anchor Date from filename: {anchor_date.date()}")
    else:
        # Fallback to file mod time or now
        try:
            mod_ts = os.path.getmtime(F26_FILE)
            anchor_date = datetime.fromtimestamp(mod_ts)
        except:
            anchor_date = datetime.now()
            
    # F26 Cutoff: The Anchor Date
    cutoff_f26 = anchor_date.strftime('%Y-%m-%d')
    
    # F25 Cutoff: Same Month/Day but in 2025
    # Handle leap year Feb 29 -> Feb 28
    try:
        cutoff_f25 = anchor_date.replace(year=2025).strftime('%Y-%m-%d')
    except ValueError:
        cutoff_f25 = '2025-02-28'

    logger.info(f"Applying YTD Cutoffs -> F26: {cutoff_f26}, F25: {cutoff_f25}")

    final_query = f"""
        SELECT 
            *,
            -- Basic Flags (Total Historical)
            CASE WHEN started_date IS NOT NULL THEN 1 ELSE 0 END as is_started,
            CASE WHEN submitted_date IS NOT NULL THEN 1 ELSE 0 END as is_submitted,
            CASE WHEN completed_date IS NOT NULL THEN 1 ELSE 0 END as is_completed,
            CASE WHEN admitted_date IS NOT NULL THEN 1 ELSE 0 END as is_admitted,
            CASE WHEN deposited_date IS NOT NULL THEN 1 ELSE 0 END as is_deposited,
            CASE WHEN deferred_date IS NOT NULL THEN 1 ELSE 0 END as is_deferred,
            
            -- YTD Point-in-Time Flags
            -- Logic: Event Date <= Cutoff Date based on Term
            CASE 
                WHEN term = 'Fall 2026' THEN (started_date <= DATE '{cutoff_f26}')
                WHEN term = 'Fall 2025' THEN (started_date <= DATE '{cutoff_f25}')
                ELSE FALSE 
            END as is_ytd_started,
            
            CASE 
                WHEN term = 'Fall 2026' THEN (submitted_date <= DATE '{cutoff_f26}')
                WHEN term = 'Fall 2025' THEN (submitted_date <= DATE '{cutoff_f25}')
                ELSE FALSE 
            END as is_ytd_submitted,
            
            CASE 
                WHEN term = 'Fall 2026' THEN (completed_date <= DATE '{cutoff_f26}')
                WHEN term = 'Fall 2025' THEN (completed_date <= DATE '{cutoff_f25}')
                ELSE FALSE 
            END as is_ytd_completed,
            
            CASE 
                WHEN term = 'Fall 2026' THEN (admitted_date <= DATE '{cutoff_f26}')
                WHEN term = 'Fall 2025' THEN (admitted_date <= DATE '{cutoff_f25}')
                ELSE FALSE 
            END as is_ytd_admitted,
            
            CASE 
                WHEN term = 'Fall 2026' THEN (deposited_date <= DATE '{cutoff_f26}')
                WHEN term = 'Fall 2025' THEN (deposited_date <= DATE '{cutoff_f25}')
                ELSE FALSE 
            END as is_ytd_deposited,
            
            CASE 
                WHEN term = 'Fall 2026' THEN (deferred_date <= DATE '{cutoff_f26}')
                WHEN term = 'Fall 2025' THEN (deferred_date <= DATE '{cutoff_f25}')
                ELSE FALSE 
            END as is_ytd_deferred,

            -- Day of Year for Pacing (0-366)
            DAYOFYEAR(COALESCE(deposited_date, admitted_date, submitted_date, started_date)) as activity_doy
            
        FROM master_raw
    """
    # Execute the transformation query
    con.execute(f"CREATE OR REPLACE TABLE master_processed AS {final_query}")
    
    con.execute("SELECT * FROM master_processed")
    df_processed = con.fetchdf()
    
    # Verification
    print("Generated Columns:", df_processed.columns.tolist())
    
    f26_intl = len(df_processed[(df_processed['term'] == 'Fall 2026') & (df_processed['residency'] == 'International')])
    f26_unk = len(df_processed[(df_processed['term'] == 'Fall 2026') & (df_processed['residency'] == 'Unknown')])
    logger.info(f"F26 International Count: {f26_intl}")
    logger.info(f"F26 Unknown Residency Count: {f26_unk}")
    if f26_intl == 0:
        logger.warning("F26 still has 0 International students. Check raw column values above.")
    if f26_unk > 0:
        logger.warning(f"F26 has {f26_unk} Unknown residency rows. Add more logic to capture them.")
    
    return df_processed

def main():
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    df_f26, df_f25 = ingest_data()
    final_df = process_data(df_f26, df_f25)
    
    logger.info(f"Saving to {OUTPUT_FILE}...")
    final_df.to_parquet(OUTPUT_FILE)
    logger.info("Pipeline Complete.")

if __name__ == "__main__":
    main()
