# Admissions Funnel Dashboard

## Overview
This project visualizes the recruitment funnel for the Kogod School of Business, comparing **Fall 2025 (Historical)** vs. **Fall 2026 (Current)**. It includes a robust ETL pipeline using DuckDB and an interactive Streamlit dashboard.

## Features
- **Data Pipeline:** Standardizes diverse Excel sources into a high-performance Parquet file using DuckDB.
- **Strict YTD Comparison:** Implements "Point-in-Time" logic where Fall 2025 metrics are filtered to match the current day/month of the previous year.
- **Executive Dashboard:**
    - **KPI Banner:** Real-time YoY variance for Started, Submitted, Completed, Admitted, and Deposited stages.
    - **Interactive Filters:** Drill down by Academic Program and Residency.
    - **Visualizations:** Funnel Conversion Chart, Demographics Split, and Deposit Pacing Curve.

## Prerequisites
- Python 3.8+
- Recommended: Create a virtual environment (`venv` or `conda`).

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Run Data Pipeline
Process the raw Excel files in `data/raw/` and generate the unified dataset:
```bash
python data_pipeline.py
```
*Output: `data/processed/master_funnel_data.parquet`*

### 2. Launch Dashboard
Start the Streamlit application:
```bash
streamlit run app.py
```
The dashboard will open in your default browser at `http://localhost:8501`.

## Project Structure
```
admissions_funnel_dashboard/
├── app.py                  # Main Streamlit Dashboard
├── data_pipeline.py        # ETL Script (DuckDB + Pandas)
├── requirements.txt        # Python Dependencies
├── cols.txt                # (Helper) Column mapping reference
├── data/
│   ├── raw/                # Source Excel files
│   └── processed/          # Generated Parquet files
└── sql/
    └── funnel_logic.sql    # Logic snippets (integrated in pipeline)
```

## Logic Notes
- **Residency:** Derived from "Primary Non-U.S. Citizenship" or "U.S. Citizen" flags.
- **YoY Comparison:** "Fall 2025" counts are strictly filtered to events occurring on or before the current Month/Day in 2025.
