import pandas as pd  # type: ignore
import os

def extract_columns():
    try:
        df1 = pd.read_excel('data/raw/Fall 2026 Application Data as of 2.13.26.xlsx', nrows=0)
        cols1 = df1.columns.tolist()
    except Exception as e:
        cols1 = [f"Error reading Fall 2026 file: {e}"]

    try:
        df2 = pd.read_excel('data/raw/Recruit Exported Enrollment - F25 to F26 - AI Opp Funnel.xlsx', nrows=0)
        cols2 = df2.columns.tolist()
    except Exception as e:
        cols2 = [f"Error reading Recruit Export file: {e}"]

    with open('cols.txt', 'w') as f:
        f.write('--- Fall 2026 ---\n')
        for c in cols1:
            f.write(f"{c}\n")
        f.write('\n--- Recruit Export ---\n')
        for c in cols2:
            f.write(f"{c}\n")

if __name__ == "__main__":
    extract_columns()
