# Final Submission Structure

```
customer_value_submission/
│
├── README.md                          ← Project overview, methodology, findings, how-to-run
├── requirements.txt                   ← All Python dependencies
├── main_pipeline.py                   ← Full end-to-end analytics pipeline (run this first)
├── app.py                             ← Streamlit dashboard (run: streamlit run app.py)
│
├── data/
│   ├── raw/
│   │   └── shopping_trends.csv        ← Original dataset (3,900 records, 19 columns)
│   ├── cleaned/
│   │   └── cleaned_customer_data.csv  ← Cleaned, standardized, binary flags added
│   ├── features/
│   │   └── customer_features.csv      ← All 51 engineered features per customer
│   └── dashboard/
│       ├── segment_summary.csv        ← 6-segment overview with revenue shares
│       ├── customer_pyramid.csv       ← Panel 1: value tier distribution
│       ├── promo_dependency_retention.csv ← Panel 2: scatter plot data
│       ├── geography_opportunity.csv  ← Panel 3: state-level opportunity scores
│       ├── category_funnel.csv        ← Panel 4: category × purchase history
│       ├── category_summary.csv       ← Category roles and metrics
│       ├── ideal_customer_profile.csv ← ICP attributes with business implications
│       ├── loyalty_definition_comparison.csv ← Def 1 vs Def 2 head-to-head
│       ├── data_dictionary.csv        ← All 51 column definitions
│       ├── demographics_analysis.csv  ← Gender × value tier breakdown
│       └── payment_analysis.csv       ← Payment method × value tier breakdown
│
├── notebooks/
│   └── customer_value_analysis.ipynb  ← Full analytical walkthrough (12 sections)
│
├── sql/
│   ├── schema.sql                     ← Database schema + all Power BI views defined
│   ├── analysis_queries.sql           ← 5 business questions, 20+ queries with comments
│   ├── customer_intelligence.db       ← SQLite database (10 tables, 11 views)
│   └── query_outputs.md               ← Key SQL findings in business language
│
├── docs/
│   ├── executive_summary.md           ← 1-page founder summary
│   ├── final_report.md                ← 7-page professional consulting report
│   ├── retention_playbook.md          ← 4-phase promotional sunset plan + segment actions
│   ├── powerbi_dashboard_guide.md     ← Exact specs for all 4 panels + KPIs
│   ├── data_dictionary.md             ← All columns documented with business logic
│   ├── run_project.md                 ← Step-by-step instructions to run everything
│   ├── submission_checklist.md        ← Problem statement compliance verification
│   └── final_submission_structure.md  ← This file
│
├── outputs/
│   ├── pipeline_run_summary.txt       ← Auto-generated on pipeline run
│   └── final_metrics_summary.csv      ← KPIs for Power BI dashboard cards
│
└── dashboard_screenshots/
    ├── README_add_powerbi_screenshots_here.md  ← Instructions
    ├── 01_full_dashboard.png          ← ADD BEFORE SUBMISSION
    ├── 02_customer_pyramid.png        ← ADD BEFORE SUBMISSION
    ├── 03_promo_retention_scatter.png ← ADD BEFORE SUBMISSION
    ├── 04_geography_map.png           ← ADD BEFORE SUBMISSION
    └── 05_category_funnel.png         ← ADD BEFORE SUBMISSION
```

## File Count Summary

| Location | Files | Notes |
|----------|-------|-------|
| Root | 4 | README, requirements, pipeline, app |
| data/ | 14 | 1 raw + 1 cleaned + 1 features + 11 dashboard |
| notebooks/ | 1 | Full analytical notebook |
| sql/ | 4 | Schema, queries, DB, findings doc |
| docs/ | 8 | All business documentation |
| outputs/ | 2 | Run summary + metrics |
| dashboard_screenshots/ | 1+ | Screenshots to be added |
| **Total** | **35+** | |

## What Each File Answers

| Business Question | Primary File |
|-------------------|-------------|
| Who are loyal vs. discount buyers? | `docs/final_report.md` Section 5–6; `sql/analysis_queries.sql` Q1 |
| What predicts high customer value? | `sql/analysis_queries.sql` Q2; `data/dashboard/segment_summary.csv` |
| Which geographies are underlevered? | `data/dashboard/geography_opportunity.csv`; `sql/analysis_queries.sql` Q3 |
| How to restructure promotions? | `docs/retention_playbook.md`; `sql/analysis_queries.sql` Q4 |
| What is the ideal customer profile? | `data/dashboard/ideal_customer_profile.csv`; `sql/analysis_queries.sql` Q5 |
| Is the loyalty definition defensible? | `data/dashboard/loyalty_definition_comparison.csv`; `docs/final_report.md` Section 5 |
