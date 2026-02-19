
import pandas as pd
import os

RAW_DIR = "data/raw"
F25_FILE = os.path.join(RAW_DIR, "Recruit Exported Enrollment - F25 to F26 - AI Opp Funnel.xlsx")

def check_file(filepath):
    print(f"--- {filepath} Columns ---")
    try:
        df = pd.read_excel(filepath, nrows=1)
        cols = [c for c in df.columns if "efer" in c]
        for c in cols:
            print(f"FOUND: {c}")
    except Exception as e:
        print(f"Error: {e}")

check_file(F25_FILE)
