# How to Run This Project

## Prerequisites

Python 3.9+ is required.

Install all dependencies:

```bash
pip install -r requirements.txt
```

## Step 1: Run the Full Pipeline

From the project root directory:

```bash
python main_pipeline.py
```

This single command:
1. Loads `data/raw/shopping_trends.csv`
2. Cleans and standardizes the data
3. Engineers 32 customer-level features
4. Builds and compares two loyalty definitions
5. Creates the final segmentation
6. Exports 11 CSV files to `data/dashboard/` and `data/cleaned/`
7. Creates the SQLite database at `sql/customer_intelligence.db`
8. Saves a run summary to `outputs/pipeline_run_summary.txt`

**Expected runtime:** Under 60 seconds.

## Step 2: Launch the Interactive Dashboard

```bash
streamlit run app.py
```

Open the URL shown in terminal (usually http://localhost:8501). The dashboard displays all four panels using the CSV outputs from Step 1.

## Step 3: Run the Jupyter Notebook

```bash
jupyter notebook notebooks/customer_value_analysis.ipynb
```

Run all cells in order. The notebook provides a full walkthrough with business context at every step. Some cells query the SQLite database — run Step 1 first.

## Step 4: Query the SQL Database

Using Python:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('sql/customer_intelligence.db')
df = pd.read_sql("SELECT * FROM v_segment_summary", conn)
conn.close()
```

Or use any SQLite client (DB Browser for SQLite, DBeaver, etc.) and point it at `sql/customer_intelligence.db`.

To run all analytical queries:

```python
conn = sqlite3.connect('sql/customer_intelligence.db')
with open('sql/analysis_queries.sql') as f:
    queries = f.read()
# Execute each statement manually or split by '--' blocks
conn.close()
```

## Step 5: Build the Power BI Dashboard

1. Open Power BI Desktop
2. Import CSVs from `data/dashboard/` (Get Data → Text/CSV)
3. Follow `docs/powerbi_dashboard_guide.md` for exact visual specifications
4. Save screenshots to `dashboard_screenshots/`

## File Dependencies

```
data/raw/shopping_trends.csv    ← Required to exist before running pipeline
    ↓ (pipeline generates)
data/cleaned/cleaned_customer_data.csv
data/features/customer_features.csv
data/dashboard/*.csv
sql/customer_intelligence.db
outputs/pipeline_run_summary.txt
outputs/final_metrics_summary.csv
    ↓ (app.py reads from data/dashboard/ and outputs/)
Streamlit Dashboard
    ↓ (notebook reads from data/ and sql/)
Jupyter Notebook
```

## Troubleshooting

**"File not found" errors:** Make sure you are running commands from the project root directory (where `main_pipeline.py` is located).

**Import errors:** Run `pip install -r requirements.txt` again to ensure all packages are installed.

**SQLite database errors:** Delete `sql/customer_intelligence.db` and re-run `python main_pipeline.py` to regenerate it.

**Streamlit "data files not found":** Run `python main_pipeline.py` first to generate the CSV outputs.
