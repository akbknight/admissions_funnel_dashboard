
import pandas as pd  # type: ignore
import os

RAW_DIR = "data/raw"
F26_FILE = os.path.join(RAW_DIR, "Fall 2026 Application Data as of 2.13.26.xlsx")
F25_FILE = os.path.join(RAW_DIR, "Recruit Exported Enrollment - F25 to F26 - AI Opp Funnel.xlsx")

def check_file(filepath, label):
    print(f"--- {label} Columns ---")
    try:
        df = pd.read_excel(filepath, nrows=1)
        cols = sorted([c for c in df.columns if "efer" in c or "riginal Term" in c])
        print(cols)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

check_file(F26_FILE, "F26")
check_file(F25_FILE, "F25")
