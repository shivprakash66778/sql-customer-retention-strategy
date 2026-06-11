# SQL Query Outputs — Business Findings

**Database:** `sql/customer_intelligence.db`  
**Query file:** `sql/analysis_queries.sql`

This document summarizes the key outputs from each SQL query block in business language. Use this to review findings without running the queries manually.

---

## Q1. Loyal vs. Discount-Driven Customers

**Finding:** The 3,900-customer base splits clearly into two high-value camps:

| Segment | Count | Avg LTV | Promo Score | Retention Proxy |
|---------|-------|---------|-------------|-----------------|
| Loyal High-Value | 599 | $2,937 | 4.8 / 100 | 56.2 / 100 |
| High-Value Promo-Dependent | 450 | ~$2,900 | 84.9 / 100 | 54.7 / 100 |

Both segments spend nearly identically per order (~$76–$77). The difference is entirely in how they arrive at a purchase. Loyal High-Value customers buy at will; Promo-Dependent customers consistently require a discount code to transact.

**Revenue breakdown by buyer type:**
- Fully organic buyers (no promo used): 56.8% of estimated revenue ($3.49M)
- Promo-using buyers: 43.2% ($2.66M)

**Implication:** The brand is not critically promo-dependent, but 21% of revenue sits in a segment whose purchase behavior may collapse if discounts are withdrawn abruptly.

---

## Q2. Behavioral Patterns Predicting High Customer Value

**Top predictors of ending up in the High value tier:**

| Signal | Customers with this signal | % who are High-Value |
|--------|---------------------------|----------------------|
| 30+ previous purchases | 1,631 | 65.0% |
| Review rating ≥ 4.0 | Subset | Higher than avg |
| Never used discount | 2,223 | 33.8% |
| High retention proxy (>60) | Subset | Strongly correlated |

**Key insight:** A customer who has made 30+ previous purchases has a 65% chance of being in the top value tier. This is the single strongest predictor available in this dataset. It makes sense: prior purchase count is a direct proxy for brand embeddedness.

**Loyalty definition validation:**
Definition 1 (Behavioral) produces perfectly monotonic results:
- High Loyalty: avg LTV $2,564 | promo score 18.1 | retention proxy 55.5
- Low Loyalty: avg LTV $758 | promo score 73.6 | retention proxy 32.2

Every tier moves in the expected direction across all four metrics — revenue, promo dependency, satisfaction, and retention signal.

---

## Q3. Underlevered Geographies and Demographics

**High-opportunity states** (scoring 4–5 out of 5 flags):

| State | Customers | Avg Spend | Promo Rate | HV Share | Score |
|-------|-----------|-----------|------------|----------|-------|
| Montana | 96 | $60.25 | 37.5% | Above avg | 5/5 |
| Alaska | 72 | $67.60 | 40.3% | Above avg | 4/5 |
| Alabama | 89 | $59.11 | 40.4% | Above avg | 4/5 |
| Idaho | 93 | $60.08 | 40.9% | Above avg | 4/5 |
| Michigan | 73 | $62.10 | 39.7% | Above avg | 4/5 |

These states show above-average customer density, above-average spend, below-average promo dependency, above-average satisfaction, and above-average share of high-value customers. They have genuine organic brand traction — the brand has not deliberately targeted them but customers there are already its best type.

**Gender:** Both male and female customers are represented roughly equally. Neither gender shows a dramatically different promo dependency profile, though the Loyal High-Value segment skews slightly female.

---

## Q4. Promotional Strategy Restructuring

**Revenue risk categorization:**

| Category | Revenue Est | % of Total |
|----------|-------------|------------|
| Safe (Loyal + Organic Mid) | $2.4M+ | ~40% |
| At-Risk (HV Promo-Dependent) | ~$1.3M | 21% |
| Low-ROI (Bargain Hunters) | ~$100K | 1.7% |

**Who needs discounts to buy:**
- High-Value Promo-Dependent: 100% discount usage, 100% promo code usage
- Low-Repeat Bargain Hunter: ~40% of each
- Loyal High-Value: **0% of either** — they buy without any promotional support

**Promo sunset candidates** (high-value, zero promo dependency, established purchase history): Approximately 299 customers meet the criteria for immediate discount removal: `value_tier = High`, `promo_dependency_score < 20`, `previous_purchases >= 20`, `review_rating >= 3.5`.

---

## Q5. Ideal Customer Profile

**Based on 599 Loyal High-Value customers:**

- Age: 30–57 years (median 44)
- Avg order value: $76
- Previous purchases: 38 (average)
- Review rating: 4.07 / 5.0
- Retention proxy: 56.2 / 100
- Promo dependency: 4.8 / 100 (**near zero**)
- Discount usage: **0%**
- Promo code usage: **0%**
- Top categories: Clothing, Accessories, Footwear
- Top states: Alabama, Montana, Minnesota, Pennsylvania, New Mexico
- Avg LTV estimate: $2,937
- Revenue concentration: **15.4% of customers → 28.6% of revenue**

**Marketing targeting criteria:**
Lookalike audience seed: The 599 Loyal High-Value customer IDs/emails. Paid acquisition creative should emphasize quality, new arrivals, and curated style — not discounts. Channel priority: email (product launches, early access) > social (lifestyle content) > paid search (brand terms).

**Acquisition pipeline** (next-best customers to nurture into ideal tier):
Approximately 150–200 `Organic Mid-Value` customers have: `previous_purchases >= 15`, `promo_dependency < 30`, `review_rating >= 3.5`. These are the near-ideal customers who just need higher AOV and deeper engagement to cross the tier threshold.
