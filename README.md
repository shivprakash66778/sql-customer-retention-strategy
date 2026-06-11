# Decoding Customer Value: A SQL-Driven Retention Strategy

> **Summer Projects '26 — Consulting & Analytics Club, IIT Guwahati**

A professional analytics consulting project that transforms raw transactional data from a D2C fashion brand into a full customer intelligence system: loyalty scoring, behavioral segmentation, promotional strategy, and a founder-ready dashboard.

---

## Business Problem

A direct-to-consumer fashion brand with ~3,900 U.S. customers runs a promotional discount program and wants to know:

**Is it building a genuinely loyal customer base, or is revenue dependent on continuous promotional activity?**

Without answering this, the brand is making marketing and product decisions based on gut feel rather than evidence.

### Five Questions This Project Answers

1. Who are genuinely loyal customers vs. those who only buy with discounts?
2. What behavioral patterns today predict high customer value over time?
3. Which geographies and demographics are commercially underlevered?
4. How should the brand restructure its promotional strategy to protect margins without losing volume?
5. What does the brand's ideal customer profile look like, and how can it acquire more of them?

---

## Data Limitations (Critical)

| Limitation | Impact | How Addressed |
|------------|--------|---------------|
| No loyalty score | Must construct from scratch | Two definitions built, tested, compared |
| No churn label | Cannot measure true attrition | Retention proxy constructed from 5 behavioral signals |
| No timestamps | No recency, no cohort analysis | All metrics are cross-sectional behavioral proxies |
| Single transaction per customer | purchase_amount is one observation | `total_spend_est` = purchase_amount × (previous_purchases + 1) |
| Synthetic dataset | Category patterns are more uniform than real retail | Called out in analysis; findings are directional |

Every analytical concept is constructed from available variables, not assumed. Every limitation is documented.

---

## Methodology

### 1. Data Cleaning
- Standardized all columns to snake_case
- Converted Yes/No fields to binary flags
- Validated numeric ranges
- Mapped purchase frequency strings to annual numeric values
- 0 missing values, 0 duplicates found

### 2. Feature Engineering (51 total columns)

**Customer Value:**
- `total_spend_est` = `purchase_amount × (previous_purchases + 1)`
- `value_tier` = High / Medium / Low (33rd and 66th percentile thresholds)

**Promo Dependency:**
- `promo_dependency_score` (0–100): `40%×discount_flag + 40%×promo_code_flag + 20%×(1 − normalized_purchase_history)`
- `promo_segment`: Organic Loyalist / Selective Promo User / Promo Dependent / Bargain Hunter (quartile-based)

**Retention Proxy (⚠️ NOT true retention — timestamps absent):**
- `retention_proxy_score` (0–100): `35%×prev_purchases + 25%×frequency + 20%×rating + 10%×subscription + 10%×low_promo`
- Range: 4.6 – 89.2 across the full dataset

**Loyalty (two competing definitions):**

| Definition | Variables | Weights |
|-----------|-----------|---------|
| Behavioral (Def 1) | purchase_count, total_spend_est, review_rating, promo_usage_rate | 30/30/20/20 |
| Commercial (Def 2) | total_spend_est, avg_order_value, purchase_freq_annual, is_subscribed, no_discount | 30/25/20/15/10 |

### 3. Loyalty Definition Comparison

| Test | Def 1 | Def 2 |
|------|-------|-------|
| Revenue: High > Low | ✓ | ✓ |
| Promo dependency: High < Low | ✓ (**55pt gap**) | ✓ (5pt gap) |
| Satisfaction: High > Low | ✓ | ✓ |
| Retention proxy: High > Low | ✓ | ✓ |
| **Score** | **4/4** | **4/4** |

**Winner: Definition 1 (Behavioral Loyalty)** — both score 4/4 but Def 1 shows dramatically wider separation on promo dependency (the critical metric for this business question), and directly incorporates satisfaction.

### 4. Customer Segmentation

Six segments, each with explicit variable conditions:

| Segment | Count | Revenue | Promo Score | Retention Proxy |
|---------|-------|---------|-------------|-----------------|
| Loyal High-Value | 599 (15.4%) | 28.6% | 4.8 | 56.2 |
| High-Value Promo-Dependent | 450 (11.5%) | 21.2% | 84.9 | 54.7 |
| At-Risk Dissatisfied | 567 (14.5%) | 18.9% | 43.9 | 40.8 |
| Organic Mid-Value | 557 (14.3%) | 12.1% | 9.3 | 47.3 |
| Low-Repeat Bargain Hunter | 424 (10.9%) | 1.7% | 50.9 | 27.4 |
| Low-Value Low-Engagement | 1,303 (33.4%) | 17.5% | 61.3 | 39.3 |

---

## Key Findings

**1. The brand is not critically promo-dependent — but is exposed in one key segment.**  
56.8% of estimated revenue ($3.49M) comes from organic buyers. However, 21.2% ($1.3M) sits in 450 High-Value Promo-Dependent customers who have 100% discount usage. If those promotions stop, that revenue is at direct risk.

**2. Loyal High-Value customers drive 28.6% of revenue from 15.4% of the base.**  
These 599 customers (avg LTV $2,937) never use discounts. Any promotional discount reaching them is pure margin waste. They are the brand's most valuable asset.

**3. At-Risk Dissatisfied is the most operationally urgent segment.**  
567 medium-to-high value customers show review ratings below 3.0, representing 18.9% of revenue. Without direct recovery action, this is a leading attrition signal.

**4. Montana, Alaska, Alabama, Idaho, and Michigan show genuine organic brand pull.**  
These states score 4–5/5 on the geography opportunity scorecard (density + spend + low promo + satisfaction + high-value share). The brand has organic traction here without having deliberately targeted these markets.

**5. The ideal customer is specific enough to target.**  
Age 30–57, slightly female, Clothing + Accessories buyer, $76/order, 38 prior purchases, 4.07/5 satisfaction, 4.8/100 promo dependency, $2,937 LTV. These 599 customers are the template for all paid acquisition.

---

## Recommendations

### Phase 1 (Weeks 1–4): Remove promos from Loyal High-Value immediately
- **Trigger:** `final_segment = 'Loyal High-Value'`  
- **Action:** Remove from all discount campaigns. Replace with early-access and VIP messaging.  
- **Risk:** Near-zero — they already buy at full price.

### Phase 2 (Weeks 5–16): Staged sunset for High-Value Promo-Dependent
- **Trigger:** `value_tier = 'High'` AND `promo_segment IN ('Promo Dependent', 'Bargain Hunter')`  
- **Action:** 3-stage: reduce depth → shift to value-adds (A/B test) → remove for responders.  
- **Track:** Weekly repeat rate; pause if drops >5%.

### Phase 3 (Weeks 8–20): Deprioritize Low-Repeat Bargain Hunter promo spend
- **Trigger:** `value_tier = 'Low'` AND `previous_purchases <= 5` AND high promo dependency  
- **Action:** Stop promo targeting; redirect budget to Organic Mid-Value nurture.  
- **Impact:** $15–20K marketing cost savings, <2% revenue impact.

---

## Folder Structure

```
customer_value_submission/
├── README.md
├── requirements.txt
├── main_pipeline.py             ← Run this first
├── app.py                       ← Streamlit dashboard
├── data/
│   ├── raw/shopping_trends.csv
│   ├── cleaned/cleaned_customer_data.csv
│   ├── features/customer_features.csv
│   └── dashboard/               ← 11 Power BI-ready CSVs
├── notebooks/customer_value_analysis.ipynb
├── sql/
│   ├── schema.sql
│   ├── analysis_queries.sql     ← 5 questions, 20+ queries
│   ├── customer_intelligence.db ← 10 tables, 11 views
│   └── query_outputs.md
├── docs/
│   ├── executive_summary.md
│   ├── final_report.md
│   ├── retention_playbook.md
│   ├── powerbi_dashboard_guide.md
│   ├── data_dictionary.md
│   ├── run_project.md
│   ├── submission_checklist.md
│   └── final_submission_structure.md
├── outputs/
│   ├── pipeline_run_summary.txt
│   └── final_metrics_summary.csv
└── dashboard_screenshots/
```

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the full pipeline
```bash
python main_pipeline.py
```
Generates all CSVs, the SQLite database, and the run summary. Runtime: ~60 seconds.

### 3. Launch the interactive dashboard
```bash
streamlit run app.py
```
Opens at http://localhost:8501 — 4-panel founder dashboard.

### 4. Open the notebook
```bash
jupyter notebook notebooks/customer_value_analysis.ipynb
```
Full walkthrough with business context at every step. Run all cells.

### 5. Query the SQL database
```python
import sqlite3, pandas as pd
conn = sqlite3.connect('sql/customer_intelligence.db')
pd.read_sql("SELECT * FROM v_segment_summary", conn)
```

---

## How to Use SQL Files

**Schema:** `sql/schema.sql` — documents every table and view. Run this to rebuild views if the DB is reset.

**Queries:** `sql/analysis_queries.sql` — organized into 5 blocks matching the 5 business questions. Each query block has a comment explaining the question and how to interpret the output.

**Power BI views available:**
- `v_customer_pyramid` → Panel 1
- `v_promo_dependency_retention` → Panel 2
- `v_geography_opportunity` → Panel 3
- `v_category_funnel` → Panel 4
- `v_segment_summary` → Full segment table
- `v_ideal_customer_profile` → ICP table

---

## How to Build the Power BI Dashboard

1. Open Power BI Desktop
2. Get Data → Text/CSV → Import all files from `data/dashboard/`
3. Import `outputs/final_metrics_summary.csv` for KPI cards
4. Follow `docs/powerbi_dashboard_guide.md` for exact visual specs

**Four required panels:**
- Panel 1: Customer Value Pyramid (funnel/bar chart)
- Panel 2: Promo Dependency vs. Retention Proxy (scatter plot)
- Panel 3: Geographic Opportunity (US filled map)
- Panel 4: Category Funnel (grouped bar chart)

See `docs/powerbi_dashboard_guide.md` for field mappings, colors, reference lines, and slicer configuration.

---

## Submission Checklist

| Requirement | Status |
|-------------|--------|
| Dataset cleaned + features engineered | ✅ |
| Two loyalty definitions built and compared | ✅ |
| Winner selected with justification | ✅ |
| Every segment traceable to variables | ✅ |
| Retention proxy with limitation note | ✅ |
| SQL queries for all 5 business questions | ✅ |
| Power BI-ready dashboard tables | ✅ |
| Promotional sunset plan (specific) | ✅ |
| Ideal customer profile | ✅ |
| 1-page executive summary | ✅ |
| 7-page final report | ✅ |
| Reproducible from `python main_pipeline.py` | ✅ |
| Power BI screenshots | ⬜ Add to dashboard_screenshots/ |

---

## Tech Stack

| Tool | Use |
|------|-----|
| Python / Pandas | Data cleaning, feature engineering, segmentation |
| scikit-learn | MinMaxScaler for loyalty and retention normalization |
| SQLite | Customer intelligence database (10 tables, 11 views) |
| Streamlit + Plotly | Interactive 4-panel dashboard |
| Jupyter | Evaluator-facing analytical notebook |
| Power BI | Founder dashboard (specs in docs/powerbi_dashboard_guide.md) |

---

*Project: Decoding Customer Value: A SQL-Driven Retention Strategy*  
*Summer Projects '26 — Consulting & Analytics Club, IIT Guwahati*
