# Power BI Dashboard Implementation Guide

## Dashboard Overview

**Title:** Customer Intelligence Dashboard — Founder View  
**Target audience:** Non-technical founding team  
**Purpose:** Answer one question per panel; no data science jargon  
**Layout:** 2×2 grid with KPI header row  

---

## KPI Header Row (Top of Dashboard)

Add 6 KPI cards across the top before the 4 panels:

| KPI Card | Data Source | Field | Format |
|----------|-------------|-------|--------|
| Total Customers | `final_metrics` | value where metric = 'Total Customers' | Integer |
| Estimated Revenue | `final_metrics` | value where metric = 'Total Estimated Revenue' | Text |
| Organic Revenue % | `final_metrics` | value where metric = 'Organic Revenue %' | Text |
| Promo-Dependent Revenue % | `final_metrics` | value where metric = 'Promo-Dependent Revenue %' | Text |
| Loyal High-Value Customers | `final_metrics` | value where metric = 'Loyal High-Value Customers' | Integer |
| At-Risk Dissatisfied | `final_metrics` | value where metric = 'At-Risk Dissatisfied' | Integer (red card) |

**KPI card colors:** Green for positive metrics (organic %, loyal HV count). Red for risk metrics (at-risk count, promo-dependent %). Use conditional formatting where possible.

---

## Panel 1: Customer Value Pyramid

**Title:** "How is customer value distributed?"  
**Subtitle:** "High-value customers are 34% of the base but drive 43%+ of revenue"  
**Data source:** `data/dashboard/customer_pyramid.csv` → table `customer_pyramid`

**Visual type:** Funnel chart (wide at top = High value, narrow at bottom = Low value)  
*Alternative if funnel unavailable: Stacked horizontal bar chart*

| Setting | Value |
|---------|-------|
| Category axis | `value_tier` (sort: High → Medium → Low) |
| Values | `pct_of_revenue` (primary bar) |
| Secondary measure | `pct_of_customers` (as a line or data label) |
| Color | High = Navy (#1a2e4a), Medium = Steel Blue (#4472C4), Low = Light Gray (#D9D9D9) |
| Data labels | Show both: "X% of customers → Y% of revenue" |
| Tooltip | `customer_count`, `avg_spend`, `total_revenue_est`, `avg_retention_proxy` |

**Business interpretation:**  
A healthy pyramid concentrates revenue in the top tier. If the High tier shows revenue share >> customer share, the brand has a core of high-value customers worth protecting above all else. If it's flat (revenue share ≈ customer share), there's no differentiation and the brand is a commodity purchase.

---

## Panel 2: Promo Dependency vs. Retention Proxy

**Title:** "Who needs discounts to buy — and who doesn't?"  
**Subtitle:** "Top-left = organic loyalists; Bottom-right = discount-trained buyers"  
**Data source:** `data/dashboard/promo_dependency_retention.csv` → table `promo_dependency_retention`

**Visual type:** Scatter plot (bubble chart)

| Setting | Value |
|---------|-------|
| X-axis | `avg_promo_dependency` (0–100 scale; label: "Promo Dependency Score") |
| Y-axis | `avg_retention_proxy` (0–100 scale; label: "Retention Signal Score") |
| Bubble size | `customer_count` |
| Bubble color | `final_segment` (categorical color scheme) |
| Data labels | Show `final_segment` name on each bubble |
| Tooltip | `customer_count`, `avg_spend`, `avg_satisfaction`, `pct_subscribed` |
| Reference lines | Vertical line at X=50 (promo threshold); Horizontal line at Y=50 (retention threshold) |

**Quadrant labels (add as text boxes):**
- Top-left (X<50, Y>50): "Brand Loyalists — Protect" (green)
- Top-right (X>50, Y>50): "Promo-Dependent — Wean Off" (orange)
- Bottom-left (X<50, Y<50): "Developing — Nurture" (blue)
- Bottom-right (X>50, Y<50): "Deal Hunters — Deprioritize" (red/gray)

**Color scheme suggestion:**
- Loyal High-Value: Navy
- High-Value Promo-Dependent: Orange
- Organic Mid-Value: Green
- At-Risk Dissatisfied: Red
- Low-Repeat Bargain Hunter: Gray
- Low-Value Low-Engagement: Light gray

**Business interpretation:**  
Loyal High-Value should appear in the top-left (low promo, high retention signal). High-Value Promo-Dependent should appear in the top-right (high promo, medium-high retention signal). The bubble sizes show customer counts — a large orange bubble in the top-right signals meaningful revenue at risk if promotions are removed without a managed transition.

---

## Panel 3: Geographic Opportunity Map

**Title:** "Where does organic brand traction exist?"  
**Subtitle:** "Green states have high spend, low promo dependency, and satisfied customers — genuine brand pull"  
**Data source:** `data/dashboard/geography_opportunity.csv` → table `geography_opportunity`

**Visual type:** Filled Map (US states)  
*Note: Requires Power BI Maps visual. Ensure location field is set to "State/Province" in data model.*

| Setting | Value |
|---------|-------|
| Location | `location` (set field type: State/Province, Country: United States) |
| Color saturation | `opportunity_score` (0–5 scale) |
| Color palette | 0 = light gray → 5 = deep green |
| Legend | Opportunity score 0–5 |
| Tooltip | `geo_customer_count`, `avg_spend`, `promo_rate`, `hv_share_pct`, `loyal_hv_count`, `geo_opportunity` |
| Filter | Add slicer: `geo_opportunity` (High / Medium / Low) |

**Supplementary table (below or beside map):**  
Add a table visual showing Top 10 states sorted by `opportunity_score` descending:

| Column | Label |
|--------|-------|
| `location` | State |
| `geo_customer_count` | Customers |
| `avg_spend` | Avg Spend ($) |
| `promo_rate` | Promo Rate |
| `hv_share_pct` | HV Share (%) |
| `loyal_hv_count` | Loyal HV Count |
| `geo_opportunity` | Opportunity Level |

**Business interpretation:**  
Green states are where the brand has unprompted brand pull — customers there spend well without needing discounts and rate the brand highly. These are the priority states for paid acquisition. High-spend states with high promo dependency (would appear orange if shown separately) are discount-driven markets — growth there would require sustained promotion investment.

---

## Panel 4: Category Funnel

**Title:** "Which categories attract new customers vs. retain established ones?"  
**Subtitle:** "Bars show customer count per purchase history tier — where do buyers start, and where do they stay?"  
**Data source:** `data/dashboard/category_funnel.csv` → table `category_funnel`

**Visual type:** Grouped bar chart (clustered)

| Setting | Value |
|---------|-------|
| X-axis | `category` (Accessories, Clothing, Footwear, Outerwear) |
| Y-axis | `customer_count` |
| Legend (series) | `purchase_history_tier` (New 0-5, Developing 6-15, Established 16+) |
| Colors | New = Light Blue, Developing = Steel Blue, Established = Dark Navy |
| Tooltip | `avg_spend`, `avg_promo_dependency`, `avg_rating`, `pct_high_value` |
| Sort | X-axis alphabetical (or by total customer count) |

**Add secondary visual:** A table using `category_summary.csv` showing category roles:

| Column | Label |
|--------|-------|
| `category` | Category |
| `avg_prev_purchases` | Avg Purchase History |
| `avg_promo_dependency` | Avg Promo Dependency |
| `avg_rating` | Avg Rating |
| `category_role` | Category Role |

Apply conditional formatting on `category_role` column:
- Premium Growth Category: Gold
- Retention Category: Green
- Entry Category: Blue
- Discount-Led Category: Orange
- Neutral Category: Gray

**Business interpretation:**  
Categories where the "Established (16+)" bar dominates are retention categories — high-history customers gravitate here. Categories dominated by "New (0-5)" are entry categories — they attract customers earlier in their brand journey. Categories with high promo dependency signal deal-driven demand. The brand should invest in retention categories to keep customers buying and monitor entry categories for category-specific discount reduction opportunities.

---

## Dashboard Slicers (Cross-Filtering)

Place a slicer panel on the left side of the dashboard with:

| Slicer | Field | Type |
|--------|-------|------|
| Segment Filter | `final_segment` | Multi-select dropdown |
| Value Tier | `value_tier` | Single-select buttons |
| Category | `category` | Multi-select |
| Season | `season` | Multi-select |
| Geography | `geo_opportunity` | Single-select buttons (All / High / Medium / Low) |

All slicers should cross-filter all four panels.

---

## Data Model (Relationships)

The dashboard CSVs are designed to be **standalone** (pre-aggregated). You do not need relationships between tables for the four main panels.

If you want to enable cross-filtering from the customers table into summary tables:
- `customers.final_segment` → `segment_summary.final_segment` (Many:1)
- `customers.location` → `geography_opportunity.location` (Many:1)
- `customers.category` → `category_summary.category` (Many:1)

---

## How to Import Data

1. Open Power BI Desktop
2. Home → Get Data → Text/CSV
3. Import these files in order:
   - `data/dashboard/customer_pyramid.csv`
   - `data/dashboard/promo_dependency_retention.csv`
   - `data/dashboard/geography_opportunity.csv`
   - `data/dashboard/category_funnel.csv`
   - `data/dashboard/category_summary.csv`
   - `data/dashboard/segment_summary.csv`
   - `outputs/final_metrics_summary.csv`
4. In Power Query, verify: numeric columns are Decimal Number or Whole Number; text columns are Text
5. Set `location` field in `geography_opportunity` → Data category: State or Province

---

## Screenshots to Add Before Submission

Before submitting, take and add to `dashboard_screenshots/`:

1. **`01_full_dashboard.png`** — Full Power BI dashboard page showing all four panels and KPI row
2. **`02_customer_pyramid.png`** — Panel 1 zoomed in, showing value tier distribution
3. **`03_promo_retention_scatter.png`** — Panel 2 scatter plot with all segment bubbles labeled
4. **`04_geography_map.png`** — Panel 3 US map with state colors visible
5. **`05_category_funnel.png`** — Panel 4 grouped bar chart with all categories

Export at 1920×1080 resolution minimum. PNG format preferred.

---

## Suggested Dashboard Themes

**Color palette:**
- Primary: #1a2e4a (dark navy)
- Secondary: #4472C4 (blue)
- Accent: #E67E22 (orange — risk)
- Positive: #27AE60 (green — opportunity)
- Neutral: #95A5A6 (gray)
- Background: #F8F9FA (near-white)

**Font:** Segoe UI (Power BI default) or Calibri  
**Title font size:** 14pt bold  
**Body font size:** 10–11pt
