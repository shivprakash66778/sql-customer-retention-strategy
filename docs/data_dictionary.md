# Data Dictionary

## Raw Dataset Columns (19)

| Column | Type | Description |
|--------|------|-------------|
| Customer ID | Integer | Unique customer identifier |
| Age | Integer | Customer age in years |
| Gender | Text | Male or Female |
| Item Purchased | Text | Specific product name (e.g., Blouse, Sweater) |
| Category | Text | Clothing / Accessories / Footwear / Outerwear |
| Purchase Amount (USD) | Float | Value of the single observed transaction |
| Location | Text | US state of the customer |
| Size | Text | Product size (XS/S/M/L/XL) |
| Color | Text | Product color |
| Season | Text | Season of purchase (Spring/Summer/Fall/Winter) |
| Review Rating | Float | Customer satisfaction score (1.0–5.0) |
| Subscription Status | Text | Whether customer has active subscription (Yes/No) |
| Payment Method | Text | Payment method used for this transaction |
| Shipping Type | Text | Shipping method (Standard, Express, 2-Day, etc.) |
| Discount Applied | Text | Whether a discount was applied (Yes/No) |
| Promo Code Used | Text | Whether a promo code was used (Yes/No) |
| Previous Purchases | Integer | Count of prior purchases — primary loyalty proxy |
| Preferred Payment Method | Text | Customer's stated preferred payment method |
| Frequency of Purchases | Text | Stated purchase frequency (Weekly/Monthly/etc.) |

## Engineered Feature Columns (32 additional)

### Binary Flags
| Column | Type | Construction | Business Use |
|--------|------|-------------|--------------|
| discount_applied_flag | 0/1 | 1 if discount_applied = 'Yes' | Enables arithmetic operations |
| promo_code_used_flag | 0/1 | 1 if promo_code_used = 'Yes' | Enables arithmetic operations |
| is_subscribed | 0/1 | 1 if subscription_status = 'Yes' | Commitment signal |
| purchase_freq_annual | Float | Maps frequency strings to annual numbers | Frequency calculations |

### Value Metrics
| Column | Type | Construction | Business Use |
|--------|------|-------------|--------------|
| total_spend_est | Float | purchase_amount × (previous_purchases + 1) | Lifetime value estimate |
| avg_order_value | Float | = purchase_amount (one observation) | Per-transaction value |
| purchase_count | Integer | previous_purchases + 1 | Total transactions |
| est_annual_spend | Float | purchase_amount × purchase_freq_annual | Annual run-rate |
| value_tier | Text | High/Medium/Low — 33rd and 66th percentiles of total_spend_est | Economic segmentation |

### Promo Dependency
| Column | Type | Construction | Business Use |
|--------|------|-------------|--------------|
| promo_usage_rate | Float 0–1 | avg(discount_flag, promo_flag) | Simple promo usage |
| promo_dependency_score | Float 0–100 | 40%×discount + 40%×promo + 20%×(1−purchase_norm) | Weighted promo reliance |
| promo_segment | Text | Quartile-based: Organic / Selective / Promo Dependent / Bargain Hunter | Campaign targeting |

### Satisfaction
| Column | Type | Construction | Business Use |
|--------|------|-------------|--------------|
| satisfaction_tier | Text | Dissatisfied (<3.0) / Neutral (3.0–4.0) / Satisfied (≥4.0) | Risk identification |
| satisfaction_flag | 0/1 | 1 if review_rating ≥ 4.0 | Binary filter |
| dissatisfied_high_value | 0/1 | 1 if High value AND Dissatisfied | Urgent recovery flag |

### Retention Proxy
**⚠️ Note: Timestamps are absent in this dataset. True retention cannot be calculated. This is a defensible engagement proxy only.**

| Column | Type | Construction | Business Use |
|--------|------|-------------|--------------|
| retention_proxy_score | Float 0–100 | 35%×prev_purchases + 25%×frequency + 20%×rating + 10%×subscription + 10%×low promo | Relative engagement ranking |
| retention_proxy_tier | Text | Low/Medium/High Retention Signal (terciles) | Segment-level filtering |
| repeat_buyer | 0/1 | 1 if previous_purchases ≥ 5 | Binary repeat flag |
| high_frequency_buyer | 0/1 | 1 if purchase_freq_annual ≥ 12 | Frequency flag |
| purchase_history_tier | Text | New (0-5) / Developing (6-15) / Established (16+) | Category funnel analysis |

### Loyalty Scores
| Column | Type | Construction | Business Use |
|--------|------|-------------|--------------|
| loyalty_score_1 | Float 0–1 | 30%×purchase_count + 30%×total_spend + 20%×satisfaction + 20%×low promo | Behavioral loyalty score |
| loyalty_def1 | Text | Low/Medium/High Loyalty (terciles of loyalty_score_1) | Behavioral loyalty tier |
| loyalty_score_2 | Float 0–1 | 30%×spend + 25%×AOV + 20%×frequency + 15%×subscription + 10%×no discount | Commercial loyalty score |
| loyalty_def2 | Text | Low/Medium/High Loyalty (terciles of loyalty_score_2) | Commercial loyalty tier |
| loyalty_segment | Text | Selected loyalty tier (winner: Definition 1 Behavioral) | Used in final segmentation |

### Geography
| Column | Type | Construction | Business Use |
|--------|------|-------------|--------------|
| geo_opportunity | Text | High/Medium/Low — 5-flag scoring (density, spend, promo, satisfaction, HV share) | Market investment priority |
| opportunity_score | Integer 0–5 | Count of favorable flags | Geographic scoring |
| geo_avg_spend | Float | State-level average purchase amount | Geographic spend depth |
| geo_promo_rate | Float | State-level average promo usage rate | Geographic promo profile |
| geo_hv_share | Float | Fraction of high-value customers in state | Geographic quality |

### Segmentation
| Column | Type | Construction | Business Use |
|--------|------|-------------|--------------|
| final_segment | Text | Rule-based assignment (see main_pipeline.py Section 9) | Primary customer grouping for all analysis |

## Segment Definitions (Traceable)

| Segment | Exact Variable Conditions |
|---------|--------------------------|
| Loyal High-Value | value_tier=High AND loyalty_segment=High Loyalty AND promo_segment ∈ {Organic Loyalist, Selective Promo User} |
| High-Value Promo-Dependent | value_tier=High AND promo_segment ∈ {Promo Dependent, Bargain Hunter} |
| At-Risk Dissatisfied | satisfaction_tier=Dissatisfied AND value_tier ∈ {High, Medium} (evaluated FIRST — priority 1) |
| Organic Mid-Value | value_tier=Medium AND promo_segment ∈ {Organic Loyalist, Selective Promo User} |
| Low-Repeat Bargain Hunter | value_tier=Low AND promo_segment ∈ {Promo Dependent, Bargain Hunter} AND previous_purchases ≤ 5 |
| Low-Value Low-Engagement | All remaining customers (catch-all) |
