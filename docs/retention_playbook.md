# Retention Playbook — Data-Backed Customer Strategy

## Context

This playbook is built from analysis of 3,900 customer records. Every recommendation is grounded in specific segment definitions, traceable to observable variables in the dataset. The goal is to reduce discount dependency without hurting revenue — building toward a customer base that buys because of brand affinity, not because of deal availability.

---

## Part 1: Promotional Sunset Plan

### Phase 1 — Remove Discounts from Loyal High-Value (Weeks 1–4)

**Segment:** Loyal High-Value  
**Trigger condition:** `value_tier = 'High'` AND `loyalty_segment = 'High Loyalty'` AND `promo_segment IN ('Organic Loyalist', 'Selective Promo User')` AND `discount_applied_flag = 0` AND `promo_code_used_flag = 0`  
**Count:** 599 customers (15.4% of base)  
**Revenue share:** 28.6%

**Action:** Remove this segment from all blanket discount email lists, promotional push notifications, and site-wide coupon pop-ups. These customers already buy at full price — any promotional discount reaching them is margin they'd have paid anyway. Replace promotional messaging with:
- "New arrivals first" early-access emails
- "Curated for you" product recommendation emails
- "Members-first" language that signals exclusivity without a discount

**Rollout timeline:** Immediate. Full segment, no A/B split needed. These customers are not promo-sensitive by definition.

**Metric to track:**
- AOV (weekly) — should hold steady or increase
- Repeat purchase rate (monthly) — baseline against last 3 months
- Email engagement rate — should remain high with new messaging

**Expected margin impact:** If average discount saved is 15% of $76 order across 599 customers and 4 annual purchases → estimated ~$27K annual margin recovery.

**Risk:** Near-zero. These customers are demonstrably not buying because of discounts.  
**Mitigation:** Set a watchlist for any customers in this segment whose purchase amount drops >20% in the first 60 days. Investigate individually.

---

### Phase 2 — Staged Discount Reduction for High-Value Promo-Dependent (Weeks 5–16)

**Segment:** High-Value Promo-Dependent  
**Trigger condition:** `value_tier = 'High'` AND `promo_segment IN ('Promo Dependent', 'Bargain Hunter')`  
**Count:** 450 customers (11.5% of base)  
**Revenue share:** 21.2%

**Why this segment:** These customers spend well ($76/order, ~38 prior purchases) but have a 100% discount and promo code usage rate. They clearly have brand engagement — the question is whether the discount is a habit or a necessity. The staged approach tests this without putting $1.3M in revenue at sudden risk.

**Stage A (Weeks 5–8): Reduce discount depth**
- Decrease discount magnitude by 30% (e.g., 20% off → 14% off)
- Maintain promo code availability but reduce code distribution frequency from weekly to bi-weekly
- Trigger: All customers in segment who purchased in the last 90 days

**Stage B (Weeks 9–12): Shift from price discounts to value-adds**
- A/B test (50/50 split):
  - Group A: Reduced discount (from Stage A)
  - Group B: Free shipping upgrade (Standard → Express) + "preferred customer" messaging, no price discount
- Compare: AOV, repeat purchase rate, email open rate

**Stage C (Weeks 13–16): Selective removal**
- Customers in Group B (value-add) who maintained purchase frequency ≥ Stage A baseline → move to full non-promo treatment
- Customers who did not maintain frequency → return to Stage A level and flag for 90-day re-evaluation

**Metric to track:**
- Weekly repeat purchase rate — pause entire phase if segment drops >5% week-over-week
- AOV by treatment group
- Promo code redemption rate (target: decreasing 10% per stage)
- Revenue per customer

**Expected impact:** If 40% of this segment (180 customers) transitions to non-promo purchasing at the same spend level, that's ~$180 × $76 × 4 annual purchases = ~$55K additional annual margin from discount removal. Revenue is preserved; margin improves.

**Risk:** Short-term order frequency dip during Stage B testing. Some price-sensitive customers in this segment may not convert to value-adds.  
**Mitigation:** The 50/50 A/B test in Stage B provides data before committing. Weekly monitoring with a hard pause trigger means maximum exposure is 1 week of dip before rollout stops.

---

### Phase 3 — Deprioritize Low-Repeat Bargain Hunters (Weeks 8–20)

**Segment:** Low-Repeat Bargain Hunter  
**Trigger condition:** `value_tier = 'Low'` AND `promo_segment IN ('Promo Dependent', 'Bargain Hunter')` AND `previous_purchases <= 5`  
**Count:** 424 customers (10.9% of base)  
**Revenue share:** 1.7%

**Why this segment:** Average estimated LTV is ~$249 (3 prior purchases × $60 avg order). Continued promotional investment in this group has negative ROI by any reasonable marketing metric. These customers came for the deal; retaining them with more deals doesn't upgrade them to loyal buyers.

**Action:** Remove from discount email lists (Week 8), SMS promo campaigns (Week 12), and site-wide personalized coupon offers (Week 16). Do NOT suppress from the website or brand communications — they can still buy if they choose. Simply stop actively pushing deals to them.

**Rollout timeline:** Gradual, 12-week phase-out. Maintain a 10% holdout group receiving normal promo treatment to measure natural attrition vs. our removal.

**Metric to track:**
- Marketing spend per customer in this segment (target: near-zero by Week 16)
- Any organic purchases from this segment (without promotional trigger)
- Holdout vs. removed-promo group repeat rate

**Expected impact:** Marketing cost savings of ~$15–20K annually (promo distribution cost + any associated offers for 424 customers). Revenue impact: minimal — 1.7% of total. If any customers from this segment purchase organically, they are automatically reclassified upward.

**Risk:** Losing customers who might have eventually become valuable.  
**Mitigation:** The 10% holdout measures exactly this. If holdout shows materially higher repeat rates than the removed group after 12 weeks, reconsider the removal threshold.

---

### Phase 4 — Nurture Organic Mid-Value Upward (Weeks 4–24)

**Segment:** Organic Mid-Value  
**Trigger condition:** `value_tier = 'Medium'` AND `promo_segment IN ('Organic Loyalist', 'Selective Promo User')`  
**Count:** 557 customers (14.3% of base)  
**Revenue share:** 12.1%

**Why this segment:** These customers already buy organically (promo score: 9.3/100, 0% discount usage). They have 27 prior purchases on average. They're one AOV increase and deeper category engagement away from crossing into the High-value tier. The barrier isn't loyalty — it's spend depth.

**Action:**
- Cross-sell to higher-AOV categories (e.g., Outerwear to existing Clothing buyers)
- Introduce subscription/membership program with free express shipping as the primary benefit
- "Complete the look" product bundles that increase per-order value by $15–25
- Quarterly "preferred customer" preview events (email-based, no discount required)

**Metric to track:**
- AOV trend (target: +10% over 6 months)
- Subscription conversion rate (these customers are currently 0% subscribed — significant upside)
- Category breadth per customer (target: increase by 0.3 additional categories over 6 months)
- Value tier migration: count moving from Medium → High each quarter

**Expected impact:** If 15% of this segment (84 customers) increases AOV by $15 and purchases 4× annually → ~$5K incremental annual revenue, plus subscription fee revenue if introduced.

**Risk:** Low. These are already organic, engaged buyers. The interventions are non-discount, so there's no margin cost and no behavioral dependency risk.

---

## Part 2: Ideal Customer Profile (ICP)

The Ideal Customer Profile is derived from the 599 Loyal High-Value customers who drive 28.6% of estimated revenue from 15.4% of the base.

| Dimension | Profile | How to Use |
|-----------|---------|------------|
| **Age** | 30–57 years (median: 44) | Target mid-career adults in paid acquisition; avoid youth-skewed platforms |
| **Gender** | Slight female majority | Ensure creative represents both; don't over-skew messaging |
| **Top categories** | Clothing → Accessories → Footwear | Lead acquisition campaigns with these categories; they attract high-value buyers |
| **Avg order value** | $76 | Full-price buyer — do not discount in acquisition creative |
| **Previous purchase behavior** | 38 prior purchases avg | This customer has been buying for a long time; acquisition should target engagement, not first-time discount |
| **Review rating** | 4.07 / 5.0 | Satisfied customer — strong candidate for referral program |
| **Retention proxy** | 56.2 / 100 | Deeply engaged; not at short-term churn risk |
| **Promo dependency** | 4.8 / 100 | Does not need incentives to buy |
| **Subscription rate** | 0% | Major untapped revenue lever; a free-shipping subscription would likely convert well |
| **Payment methods** | Credit Card, Cash, PayPal | Diverse — no friction in checkout experience needed |
| **Purchase frequency** | Quarterly (most common) | Email cadence should match this; don't over-email |
| **Top states** | Alabama, Montana, Minnesota, Pennsylvania, New Mexico | Seed lookalike audiences from these geographies |
| **Estimated LTV** | $2,937 | Justifies premium acquisition CPAs |

**Marketing team action:**
1. Export the 599 Loyal High-Value customer emails/IDs from `data/features/customer_features.csv` (filter: `final_segment = 'Loyal High-Value'`)
2. Create a Meta/Google lookalike audience seeded with these customers
3. Creative messaging: quality, new arrivals, curated style, early access — NOT discounts
4. Targeting parameters: age 30–57, interest in fashion/style (not deal-seeking), geographic priority in High Opportunity states

---

## Part 3: Segment-Specific Retention Actions

### Loyal High-Value (599 customers, 28.6% revenue)
**Goal:** Protect and increase share-of-wallet.  
**Action:** Remove from all discount campaigns immediately. Launch VIP treatment: early access to new collections, free premium shipping, personalized product recommendations based on category history.  
**Why:** Any discount is wasted margin. These customers are already deeply committed. The right investment is recognition, not price reduction.  
**Metric:** AOV, repeat rate, LTV growth quarter-over-quarter.

### High-Value Promo-Dependent (450 customers, 21.2% revenue)
**Goal:** Wean off discounts while maintaining purchase frequency.  
**Action:** Execute 3-stage sunset plan (Part 1, Phase 2). Never cold-stop discounts.  
**Why:** Brand affinity exists — these customers have 38 prior purchases. The discount is likely a habit reinforced by our own behavior, not a price necessity.  
**Metric:** Weekly repeat rate, promo redemption rate, Stage B A/B test results.

### At-Risk Dissatisfied (567 customers, 18.9% revenue)
**Goal:** Recover relationship before they attrite.  
**Action:** Segment by value tier and personalize outreach. High-value at-risk customers: direct email or SMS from the founder or customer success team acknowledging their experience and offering resolution (replacement, credit, or feedback call). Medium-value at-risk: automated "we want to make it right" campaign with a service guarantee.  
**Why:** This is the brand's largest operational risk. 567 customers × ~$1.16K avg LTV = $657K in revenue attached to dissatisfied customers.  
**Metric:** Resolution rate, post-outreach satisfaction score (survey), purchase within 90 days.  
**Timeline:** Start immediately. At-risk customers are the most time-sensitive.

### Organic Mid-Value (557 customers, 12.1% revenue)
**Goal:** Upgrade to Loyal High-Value tier.  
**Action:** Cross-sell, subscription offer, "complete the look" bundles.  
**Why:** They're already organic and engaged — the lowest-cost segment to upgrade.  
**Metric:** AOV growth, subscription conversion, tier migration rate.  
**Timeline:** Begin Week 4 (after Phase 1 is operational).

### Low-Repeat Bargain Hunter (424 customers, 1.7% revenue)
**Goal:** Stop wasting marketing budget; allow natural attrition.  
**Action:** Remove from promo campaigns. Keep receiving brand content (lifestyle, product stories). If organic purchase occurs, reclassify automatically.  
**Why:** Negative ROI on continued promotion. Resources are better deployed elsewhere.  
**Metric:** Marketing cost savings, organic return rate.

### Low-Value Low-Engagement (1,303 customers, 17.5% revenue)
**Goal:** Identify salvageable customers; deprioritize the rest.  
**Action:** Single reactivation campaign: "We'd love to see you again" with a time-limited value-add (free shipping, not a discount). Non-responders within 60 days are moved to a low-touch email cadence with no promo spend.  
**Why:** Largest segment by count but very heterogeneous. A one-time sort is efficient.  
**Metric:** Reactivation rate, post-campaign tier classification.
