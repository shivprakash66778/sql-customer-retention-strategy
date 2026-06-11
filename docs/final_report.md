# Decoding Customer Value: A SQL-Driven Retention Strategy
## Final Analytical Report

**Prepared for:** Founding Team  
**Project Type:** Customer Intelligence & Retention Strategy  
**Dataset:** 3,900 customer records | D2C Fashion Brand | United States  
**Methodology:** Python (feature engineering) + SQL (segmentation) + Composite loyalty modeling

---

## 1. Executive Summary

A D2C fashion brand with 3,900 U.S. customers wants to know whether its promotional program is building a loyal customer base or simply attracting deal hunters who will not return once discounts stop.

**The core finding:** The brand is in a structurally sound but operationally exposed position. 56.8% of estimated revenue comes from fully organic buyers who transact without any discount support. However, 21.2% of revenue is concentrated in 450 High-Value Promo-Dependent customers who consistently use both discount codes and promo codes for every purchase. If those promotions are withdrawn without a managed transition, that revenue is at risk.

**Three immediate actions:**
1. Stop discounting the 599 Loyal High-Value customers — they already buy at full price. Any discount reaching them is pure margin loss.
2. Begin a 12-week staged transition for the 450 High-Value Promo-Dependent segment: reduce discount depth, shift to non-monetary value, track weekly repeat rate.
3. Reallocate the promo budget currently spent on 424 Low-Repeat Bargain Hunters (1.7% of revenue) to nurturing the 557 Organic Mid-Value customers who are the natural pipeline to the top tier.

---

## 2. Problem Framing

The brand asked a deceptively simple question: *Is our promotional program building loyalty, or buying transactions?*

Answering it is harder than it sounds. The dataset has no loyalty score, no churn label, and no timestamps. Every analytical concept — loyalty, retention, customer value — must be constructed from the available behavioral signals.

**Available signals:**
- Previous purchases (repeat behavior proxy)
- Purchase amount (transaction-level value)
- Review rating (satisfaction proxy)
- Discount applied / promo code used (promo dependency)
- Purchase frequency (engagement cadence)
- Subscription status (commitment signal)
- Location, age, gender, category, payment method (demographic and preference attributes)

**What cannot be measured:**
- True churn (no timestamps → no inactivity window)
- Customer acquisition date (no cohort analysis possible)
- Revenue trend per customer (no time series)
- True retention rate (only a proxy is constructible)

These limitations are acknowledged explicitly throughout the analysis. Every metric is labeled as a proxy where appropriate, with the construction logic fully documented.

---

## 3. Data Description and Limitations

| Attribute | Value |
|-----------|-------|
| Total records | 3,900 |
| Features (raw) | 19 |
| Features (engineered) | 51 |
| Missing values | None |
| Duplicates | None |
| Geographic coverage | 50 U.S. states + DC |
| Categories | Clothing, Accessories, Footwear, Outerwear |

**Key limitations:**
- **Single transaction per customer.** Purchase amount represents one observed transaction. Total lifetime value is estimated as `purchase_amount × (previous_purchases + 1)` — this is a useful proxy but not a true transactional sum.
- **Previous purchases is ordinal-ish but not timestamped.** We know a customer has made 30 prior purchases but not when. Recency cannot be isolated.
- **Synthetic dataset.** Patterns across categories are more uniform than real retail data would show. Category differentiation is meaningful directionally but not as sharp as live data would produce.

---

## 4. Feature Engineering

Every engineered feature is constructed with explicit business logic. Features that do not lead to a decision were not included.

### Customer Value Metrics

| Feature | Construction | Business Logic |
|---------|-------------|----------------|
| `total_spend_est` | `purchase_amount × (previous_purchases + 1)` | Estimated lifetime spend — the customer's total economic contribution |
| `value_tier` | Terciles of `total_spend_est` (33rd, 66th percentile) | Segments customers by economic weight: High ($1,845+), Medium ($880–$1,845), Low (<$880) |
| `est_annual_spend` | `purchase_amount × purchase_freq_annual` | Projected annual value if current behavior persists |

### Promo Dependency Metrics

| Feature | Construction | Business Logic |
|---------|-------------|----------------|
| `promo_dependency_score` | `0.4×discount_flag + 0.4×promo_flag + 0.2×(1 − prev_purchases_norm) × 100` | 0–100 scale; infrequent buyers who use promos are more concerning than frequent buyers who occasionally use them |
| `promo_segment` | Quartile-based: Organic Loyalist / Selective Promo User / Promo Dependent / Bargain Hunter | Actionable groupings for promotional targeting |

### Retention Proxy

**Critical note:** Since the dataset has no timestamps, true retention cannot be calculated. The `retention_proxy_score` is a composite engagement signal, not a prediction of whether a customer will buy again.

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Previous purchases (normalized) | 35% | More past purchases = more deeply embedded in the brand habit |
| Purchase frequency (normalized) | 25% | More frequent buyers have a shorter gap to next purchase |
| Review rating (normalized) | 20% | Satisfied customers are less likely to seek alternatives |
| Subscription status | 10% | An active subscriber has explicitly committed to the brand |
| Low promo dependency (inverted) | 10% | Organic buyers' behavior is not contingent on promotions being offered |

**Score range:** 4.6 – 89.2 (mean: 43.7). Segments now show meaningful differentiation: Loyal High-Value (56.2) vs. Low-Repeat Bargain Hunters (27.4).

---

## 5. Loyalty Definitions

The problem statement requires at least two competing loyalty definitions, tested and compared.

### Definition 1: Behavioral Loyalty
*Captures brand attachment through what customers DO — their purchase habits, satisfaction, and organic buying.*

**Variables:** `purchase_count`, `total_spend_est`, `review_rating`, `promo_usage_rate`  
**Weights:** 30% purchase frequency + 30% spend + 20% satisfaction + 20% low promo usage

### Definition 2: Commercial Loyalty  
*Captures economic commitment — how much customers SPEND and whether they've made binding choices (subscription, full-price purchase).*

**Variables:** `total_spend_est`, `avg_order_value`, `purchase_freq_annual`, `is_subscribed`, `discount_applied_flag` (inverted)  
**Weights:** 30% spend + 25% AOV + 20% frequency + 15% subscription + 10% no discount

### Comparison

Both definitions are evaluated against four monotonicity tests. A well-constructed loyalty score should produce High Loyalty customers who are clearly better than Low Loyalty customers on every relevant metric.

| Metric | Def 1 Pass | Def 2 Pass |
|--------|-----------|-----------|
| Revenue: High > Low | ✓ | ✓ |
| Promo dependency: High < Low | ✓ | ✓ |
| Satisfaction: High > Low | ✓ | ✓ |
| Retention proxy: High > Low | ✓ | ✓ |
| **Total** | **4/4** | **4/4** |

Both definitions achieve 4/4 in this dataset, which is a sign of high internal consistency. **Definition 1 (Behavioral) is selected** because:
- It incorporates satisfaction (review_rating) directly, which Definition 2 does not
- Its promo dependency separation between tiers is more pronounced (73.6 vs 18.1 for Def 1, compared to 47.7 vs 42.3 for Def 2 — Def 2's tiers are far less separated on this critical metric)
- It captures behavioral attachment rather than economic capacity alone

---

## 6. Final Customer Segmentation

Six segments, each defined by explicit variable conditions.

| Segment | Count | Revenue Share | Definition |
|---------|-------|--------------|------------|
| **Loyal High-Value** | 599 (15.4%) | 28.6% | value_tier=High + High Loyalty + promo_segment ∈ {Organic Loyalist, Selective Promo User} |
| **High-Value Promo-Dependent** | 450 (11.5%) | 21.2% | value_tier=High + promo_segment ∈ {Promo Dependent, Bargain Hunter} |
| **At-Risk Dissatisfied** | 567 (14.5%) | 18.9% | satisfaction_tier=Dissatisfied + value_tier ∈ {High, Medium} |
| **Organic Mid-Value** | 557 (14.3%) | 12.1% | value_tier=Medium + promo_segment ∈ {Organic Loyalist, Selective Promo User} |
| **Low-Repeat Bargain Hunter** | 424 (10.9%) | 1.7% | value_tier=Low + promo_segment ∈ {Promo Dependent, Bargain Hunter} + previous_purchases ≤ 5 |
| **Low-Value Low-Engagement** | 1,303 (33.4%) | 17.5% | All remaining customers |

**Segment naming note:** The previous "One-Time Bargain Hunter" label has been corrected to **"Low-Repeat Bargain Hunter"** — the segment includes customers with 1–5 previous purchases (not exclusively one-time buyers), all in the Low value tier with high promo dependency. The new name is more accurate.

**At-Risk Dissatisfied** (567 customers, 18.9% of revenue) is the most operationally urgent segment. These are medium-to-high value customers showing dissatisfaction signals (review_rating < 3.0). Without intervention, their purchase history and spending capacity are at risk of being redirected to a competitor.

---

## 7. SQL-Driven Insights

Five business questions answered via SQL analysis on the SQLite database:

### Q1 — Loyal vs. Discount-Driven
The Loyal High-Value segment and the High-Value Promo-Dependent segment have nearly identical average order values (~$76–$77) but fundamentally different behavior. One buys at will (promo score: 4.8); the other always requires a code (promo score: 84.9). The brand's discount program is not creating loyalty in the high-spend group — it's being harvested by already-engaged buyers.

### Q2 — Behavioral Predictors of Value
The strongest predictor of high-value tier membership is `previous_purchases >= 30` (65% of such customers are High-value). Loyalty Definition 1 is validated: High Loyalty customers show LTV $2,564 vs. Low Loyalty $758 — a 3.4× difference.

### Q3 — Underlevered Geographies
Montana, Alaska, Alabama, Idaho, and Michigan score 4–5/5 on the geography opportunity scorecard. These states have above-average customer density, spend, satisfaction, and high-value share, plus below-average promo dependency. The brand appears to have organic traction here without having deliberately targeted these markets.

### Q4 — Promotional Strategy
Approximately $2.4M in estimated revenue (Loyal + Organic Mid-Value customers) can be managed at full margin immediately — these customers don't use promos. The ~$1.3M in HV Promo-Dependent revenue requires a staged approach. The ~$100K spent on Low-Repeat Bargain Hunters is low-ROI by any measure.

### Q5 — Ideal Customer Profile
Age 30–57, slightly female, buys Clothing/Accessories at $76/order, 38 prior purchases, 4.07/5 satisfaction, near-zero promo dependency. This customer drives 28.6% of revenue from 15.4% of the base — a disproportionate contribution that justifies priority protection and lookalike acquisition investment.

---

## 8. Dashboard Design

Four panels, designed for a non-technical founding team:

1. **Customer Value Pyramid** — Funnel chart showing High/Medium/Low value tier distribution with revenue share overlay. Key message: what fraction of customers drive what fraction of revenue.

2. **Promo Dependency vs. Retention Proxy** — Scatter plot with segments as bubbles (size = customer count). X-axis: promo dependency score. Y-axis: retention proxy score. Quadrant logic: top-left is the ideal (low promo, high retention signal); bottom-right is the risk zone.

3. **Geographic Opportunity Map** — US filled map colored by opportunity score. States in green (4–5/5) have organic brand pull and can absorb paid acquisition without the discount crutch.

4. **Category Funnel** — Grouped bar chart showing customer count by category × purchase history tier. Which categories attract newer customers vs. retain established ones.

See `docs/powerbi_dashboard_guide.md` for exact visual specifications, field mappings, and filter configurations.

---

## 9. Retention Playbook Summary

Full details in `docs/retention_playbook.md`. Summary of the four-phase promotional sunset plan:

| Phase | Timing | Segment | Action | Risk |
|-------|--------|---------|--------|------|
| 1 | Weeks 1–4 | Loyal High-Value | Remove all blanket promos | Near-zero |
| 2 | Weeks 5–16 | HV Promo-Dependent | Stage down: reduce depth → value-add → remove | Medium |
| 3 | Weeks 8–20 | Low-Repeat Bargain Hunter | Stop promo targeting, redirect budget | Low |
| 4 | Weeks 4–24 | Organic Mid-Value | Nurture upward: cross-sell, subscription | Low |

---

## 10. Final Recommendation

The brand should answer its own question honestly: it is running a hybrid business — part brand-loyalty driven, part promotion-driven. The healthy news is that the organic half is larger (56.8% of revenue). The risk is that the promotional half is concentrated in a high-spend segment (HV Promo-Dependent) that hasn't been tested without discounts.

The recommended path is not to cut discounts — it's to run a controlled experiment. Phase 1 (remove promos from already-organic Loyal High-Value customers) is zero-risk and immediately margin-accretive. Phase 2 (staged transition for HV Promo-Dependent) is a managed test with weekly monitoring. Phases 3 and 4 redirect budget rather than eliminate it.

If the brand executes this plan, the expected outcome over 6 months is:
- Margin improvement from ~$0 additional revenue but lower discount cost on 599 organic customers
- 40% of HV Promo-Dependent potentially transitioning to non-promo purchasing (estimated ~$520K in revenue now earned at full margin)
- Organic Mid-Value AOV growth of 10–15% through cross-sell and subscription nudges
- Reallocation of bargain-hunter promo budget (~$15–20K estimated marketing spend) to higher-ROI segments

The biggest risk is not acting and watching the promotional program continue to train the customer base to expect discounts that erode margins without building loyalty.
