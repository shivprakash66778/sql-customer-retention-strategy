-- =============================================================================
-- Decoding Customer Value: A SQL-Driven Retention Strategy
-- analysis_queries.sql — All business intelligence queries
-- =============================================================================
-- Run against: sql/customer_intelligence.db
-- Execute pipeline first: python main_pipeline.py
--
-- STRUCTURE:
--   Q1. Loyal customers vs. discount-only buyers
--   Q2. Behavioral patterns predicting high customer value
--   Q3. Geography and demographics: underlevered markets
--   Q4. Promotional strategy restructuring
--   Q5. Ideal customer profile
--   DASHBOARD. Power BI view queries
-- =============================================================================


-- =============================================================================
-- Q1: WHO ARE GENUINELY LOYAL CUSTOMERS VS. DISCOUNT-DRIVEN BUYERS?
-- Business context: The brand needs to know whether its promotional program
-- is building real brand affinity or simply attracting deal seekers who won't
-- return once discounts are removed.
-- =============================================================================

-- Q1a. Top-level segment landscape
-- Interpretation: Compare Loyal High-Value vs High-Value Promo-Dependent.
-- Both groups spend well, but one requires discounts; the other does not.
SELECT
    final_segment,
    COUNT(*)                                    AS customer_count,
    ROUND(AVG(purchase_amount), 2)              AS avg_order_value,
    ROUND(AVG(total_spend_est), 0)              AS avg_lifetime_value_est,
    ROUND(AVG(promo_dependency_score), 1)       AS avg_promo_dependency,
    ROUND(AVG(pct_discount_applied_raw) * 100, 1) AS pct_using_discounts,
    ROUND(AVG(review_rating), 2)                AS avg_satisfaction,
    ROUND(AVG(retention_proxy_score), 1)        AS avg_retention_proxy,
    ROUND(AVG(previous_purchases), 1)           AS avg_previous_purchases
FROM (
    SELECT *,
           discount_applied_flag AS pct_discount_applied_raw
    FROM customers
)
GROUP BY final_segment
ORDER BY avg_lifetime_value_est DESC;

-- Q1b. Head-to-head: Loyal High-Value vs. High-Value Promo-Dependent
-- Interpretation: These two segments have similar AOV but very different
-- promo dependency. Promo-dependent customers are profitable IF they keep buying;
-- without discounts, that behavior is uncertain.
SELECT
    final_segment,
    COUNT(*)                                AS n,
    ROUND(AVG(purchase_amount), 2)          AS avg_order_value,
    ROUND(AVG(total_spend_est), 0)          AS avg_ltv_est,
    ROUND(AVG(promo_dependency_score), 1)   AS promo_score,
    ROUND(AVG(review_rating), 2)            AS satisfaction,
    ROUND(AVG(retention_proxy_score), 1)    AS retention_proxy,
    ROUND(SUM(total_spend_est), 0)          AS total_revenue_contribution
FROM customers
WHERE final_segment IN ('Loyal High-Value', 'High-Value Promo-Dependent')
GROUP BY final_segment;

-- Q1c. Revenue at risk: organic vs. promo-using customers
-- Interpretation: What share of estimated revenue depends on promotions?
SELECT
    CASE WHEN promo_usage_rate > 0 THEN 'Promo-Using' ELSE 'Fully Organic' END AS buyer_type,
    COUNT(*)                                AS customer_count,
    ROUND(SUM(total_spend_est), 0)          AS total_revenue_est,
    ROUND(SUM(total_spend_est) * 100.0 /
          (SELECT SUM(total_spend_est) FROM customers), 1) AS pct_of_total_revenue
FROM customers
GROUP BY buyer_type;

-- Q1d. Promo dependency score distribution by loyalty tier
-- Interpretation: Behaviorally loyal customers should show lower promo dependency.
-- This validates that Loyalty Definition 1 captures genuine organic attachment.
SELECT
    loyalty_def1,
    COUNT(*)                              AS n,
    ROUND(AVG(promo_dependency_score), 1) AS avg_promo_score,
    ROUND(AVG(total_spend_est), 0)        AS avg_ltv,
    ROUND(AVG(retention_proxy_score), 1)  AS avg_retention_proxy
FROM customers
GROUP BY loyalty_def1
ORDER BY CASE loyalty_def1 WHEN 'High Loyalty' THEN 1 WHEN 'Medium Loyalty' THEN 2 ELSE 3 END;

-- Q1e. Subscription × promo: are subscribers more organic?
-- Interpretation: Subscribers have made a commitment signal. Check whether
-- they're also less promo-dependent.
SELECT
    is_subscribed,
    COUNT(*)                                  AS n,
    ROUND(AVG(promo_dependency_score), 1)     AS avg_promo_score,
    ROUND(AVG(retention_proxy_score), 1)      AS avg_retention_proxy,
    ROUND(AVG(total_spend_est), 0)            AS avg_ltv
FROM customers
GROUP BY is_subscribed;


-- =============================================================================
-- Q2: WHAT BEHAVIORAL PATTERNS PREDICT HIGH CUSTOMER VALUE?
-- Business context: Identify which customer behaviors are correlated with
-- high lifetime value. This informs what behaviors to nurture in newer customers.
-- =============================================================================

-- Q2a. Value tier profile
-- Interpretation: How do High/Medium/Low customers differ behaviorally?
-- The gap between High and Low shows which variables drive value separation.
SELECT
    value_tier,
    COUNT(*)                                    AS n,
    ROUND(AVG(age), 1)                          AS avg_age,
    ROUND(AVG(purchase_amount), 2)              AS avg_order_value,
    ROUND(AVG(previous_purchases), 1)           AS avg_prev_purchases,
    ROUND(AVG(review_rating), 2)                AS avg_rating,
    ROUND(AVG(promo_dependency_score), 1)       AS avg_promo_score,
    ROUND(AVG(retention_proxy_score), 1)        AS avg_retention_proxy,
    ROUND(AVG(is_subscribed) * 100, 1)          AS pct_subscribed,
    ROUND(AVG(purchase_freq_annual), 1)         AS avg_annual_frequency
FROM customers
GROUP BY value_tier
ORDER BY CASE value_tier WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

-- Q2b. Predictor signals: % of high-value customers in each behavorial subgroup
-- Interpretation: Higher % = stronger predictor of high value.
SELECT predictor, n_customers, pct_high_value FROM (
    SELECT '30+ previous purchases'       AS predictor, COUNT(*) AS n_customers,
           ROUND(AVG(CASE WHEN value_tier='High' THEN 100.0 ELSE 0 END), 1) AS pct_high_value
    FROM customers WHERE previous_purchases >= 30
    UNION ALL
    SELECT 'Review rating >= 4.0', COUNT(*),
           ROUND(AVG(CASE WHEN value_tier='High' THEN 100.0 ELSE 0 END), 1)
    FROM customers WHERE review_rating >= 4.0
    UNION ALL
    SELECT 'Never used discount', COUNT(*),
           ROUND(AVG(CASE WHEN value_tier='High' THEN 100.0 ELSE 0 END), 1)
    FROM customers WHERE discount_applied_flag = 0
    UNION ALL
    SELECT 'Subscriber', COUNT(*),
           ROUND(AVG(CASE WHEN value_tier='High' THEN 100.0 ELSE 0 END), 1)
    FROM customers WHERE is_subscribed = 1
    UNION ALL
    SELECT 'Weekly buyer', COUNT(*),
           ROUND(AVG(CASE WHEN value_tier='High' THEN 100.0 ELSE 0 END), 1)
    FROM customers WHERE frequency_of_purchases = 'Weekly'
    UNION ALL
    SELECT 'High retention proxy (score>60)', COUNT(*),
           ROUND(AVG(CASE WHEN value_tier='High' THEN 100.0 ELSE 0 END), 1)
    FROM customers WHERE retention_proxy_score > 60
) ORDER BY pct_high_value DESC;

-- Q2c. Loyalty score vs. value tier: does behavioral loyalty track commercial value?
-- Interpretation: If loyalty definition 1 is well-constructed, High Loyalty
-- customers should also be predominantly in the High value tier.
SELECT
    loyalty_def1,
    value_tier,
    COUNT(*)                    AS n,
    ROUND(AVG(total_spend_est), 0) AS avg_ltv
FROM customers
GROUP BY loyalty_def1, value_tier
ORDER BY CASE loyalty_def1 WHEN 'High Loyalty' THEN 1 WHEN 'Medium Loyalty' THEN 2 ELSE 3 END,
         CASE value_tier WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

-- Q2d. Age and frequency as value predictors
SELECT
    CASE WHEN age < 25 THEN '18-24'
         WHEN age < 35 THEN '25-34'
         WHEN age < 45 THEN '35-44'
         WHEN age < 55 THEN '45-54'
         ELSE '55+' END       AS age_group,
    COUNT(*)                   AS n,
    ROUND(AVG(purchase_amount), 2)     AS avg_spend,
    ROUND(AVG(total_spend_est), 0)     AS avg_ltv,
    ROUND(AVG(promo_dependency_score), 1) AS avg_promo,
    ROUND(AVG(retention_proxy_score), 1) AS avg_retention
FROM customers
GROUP BY age_group
ORDER BY age_group;


-- =============================================================================
-- Q3: WHICH GEOGRAPHIES AND DEMOGRAPHICS ARE COMMERCIALLY UNDERLEVERED?
-- Business context: Identify states where genuine brand traction exists
-- (high organic spend, satisfied customers, high-value share) but may not
-- yet be deliberately targeted by the brand's marketing.
-- =============================================================================

-- Q3a. High-opportunity geographies
-- Interpretation: States with high opportunity scores show all five positive
-- signals: density, spend depth, organic buying, satisfaction, and HV share.
-- These are the states where paid acquisition has the highest floor quality.
SELECT
    location,
    geo_customer_count,
    ROUND(geo_avg_spend, 2)           AS avg_spend,
    ROUND(geo_promo_rate, 3)          AS promo_rate,
    ROUND(geo_avg_rating, 2)          AS avg_rating,
    ROUND(geo_hv_share * 100, 1)      AS hv_share_pct,
    loyal_hv_count,
    opportunity_score,
    geo_opportunity
FROM geography_opportunity
WHERE geo_opportunity = 'High Opportunity'
ORDER BY opportunity_score DESC, geo_avg_spend DESC;

-- Q3b. Where are loyal customers concentrated?
SELECT
    location,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN final_segment = 'Loyal High-Value' THEN 1 ELSE 0 END) AS loyal_hv,
    SUM(CASE WHEN final_segment = 'High-Value Promo-Dependent' THEN 1 ELSE 0 END) AS hv_promo_dep,
    SUM(CASE WHEN final_segment = 'At-Risk Dissatisfied' THEN 1 ELSE 0 END) AS at_risk,
    ROUND(AVG(purchase_amount), 2) AS avg_spend
FROM customers
GROUP BY location
HAVING total_customers >= 50
ORDER BY loyal_hv DESC
LIMIT 15;

-- Q3c. Demographics: gender × value
SELECT
    gender,
    COUNT(*)                                         AS n,
    ROUND(AVG(purchase_amount), 2)                   AS avg_spend,
    ROUND(AVG(total_spend_est), 0)                   AS avg_ltv,
    ROUND(AVG(promo_dependency_score), 1)            AS avg_promo,
    SUM(CASE WHEN value_tier='High' THEN 1 ELSE 0 END)   AS high_value_n,
    ROUND(SUM(CASE WHEN value_tier='High' THEN 1.0 ELSE 0 END)
          / COUNT(*) * 100, 1)                       AS pct_high_value
FROM customers
GROUP BY gender;

-- Q3d. Age group × promo dependency: who can be weaned off discounts?
SELECT
    CASE WHEN age < 35 THEN 'Under 35'
         WHEN age < 50 THEN '35-49'
         ELSE '50+' END        AS age_band,
    COUNT(*)                    AS n,
    ROUND(AVG(promo_dependency_score), 1) AS avg_promo_score,
    ROUND(AVG(retention_proxy_score), 1)  AS avg_retention_proxy,
    ROUND(AVG(total_spend_est), 0)        AS avg_ltv
FROM customers
GROUP BY age_band
ORDER BY age_band;

-- Q3e. Payment method preferences among high-value customers
SELECT
    preferred_payment_method,
    COUNT(*)                    AS n,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers WHERE value_tier='High'), 1) AS pct_of_high_value,
    ROUND(AVG(purchase_amount), 2) AS avg_spend
FROM customers
WHERE value_tier = 'High'
GROUP BY preferred_payment_method
ORDER BY n DESC;


-- =============================================================================
-- Q4: HOW SHOULD THE BRAND RESTRUCTURE ITS PROMOTIONAL STRATEGY?
-- Business context: The brand should protect margins while preserving volume.
-- Key insight: Reducing discounts for customers who buy organically anyway
-- is a safe margin win. Reducing discounts for promo-dependent high spenders
-- requires a gradual, tracked approach.
-- =============================================================================

-- Q4a. Revenue safe zones vs. at-risk zones
-- Interpretation: "Safe Revenue" (organic + loyal) can tolerate discount removal.
-- "At-Risk Revenue" requires a staged approach.
SELECT scenario, n_customers, total_revenue_est, pct_of_total FROM (
    SELECT 'Safe Revenue: Loyal High-Value + Organic Mid' AS scenario,
           COUNT(*)                           AS n_customers,
           ROUND(SUM(total_spend_est), 0)     AS total_revenue_est,
           ROUND(SUM(total_spend_est) * 100.0 /
                 (SELECT SUM(total_spend_est) FROM customers), 1) AS pct_of_total
    FROM customers
    WHERE final_segment IN ('Loyal High-Value', 'Organic Mid-Value')
    UNION ALL
    SELECT 'At-Risk Revenue: HV Promo-Dependent',
           COUNT(*), ROUND(SUM(total_spend_est), 0),
           ROUND(SUM(total_spend_est) * 100.0 /
                 (SELECT SUM(total_spend_est) FROM customers), 1)
    FROM customers WHERE final_segment = 'High-Value Promo-Dependent'
    UNION ALL
    SELECT 'Low-ROI Promo Spend: Low-Repeat Bargain Hunters',
           COUNT(*), ROUND(SUM(total_spend_est), 0),
           ROUND(SUM(total_spend_est) * 100.0 /
                 (SELECT SUM(total_spend_est) FROM customers), 1)
    FROM customers WHERE final_segment = 'Low-Repeat Bargain Hunter'
);

-- Q4b. Promo usage by segment (who needs discounts to buy?)
SELECT
    final_segment,
    COUNT(*)                                   AS n,
    ROUND(AVG(discount_applied_flag) * 100, 1) AS pct_discount,
    ROUND(AVG(promo_code_used_flag) * 100, 1)  AS pct_promo_code,
    ROUND(AVG(promo_dependency_score), 1)      AS avg_promo_score,
    ROUND(AVG(purchase_amount), 2)             AS avg_spend,
    ROUND(AVG(retention_proxy_score), 1)       AS retention_proxy
FROM customers
GROUP BY final_segment
ORDER BY avg_promo_score DESC;

-- Q4c. Promo sunset candidates: high-value customers who already buy without promos
-- These customers are ready for immediate discount removal — no behavioral change needed.
SELECT
    customer_id, age, gender, location, category,
    purchase_amount, previous_purchases,
    ROUND(review_rating, 1)          AS rating,
    ROUND(promo_dependency_score, 1) AS promo_score,
    ROUND(retention_proxy_score, 1)  AS retention_proxy,
    final_segment
FROM customers
WHERE value_tier = 'High'
  AND promo_dependency_score < 20
  AND previous_purchases >= 20
  AND review_rating >= 3.5
ORDER BY total_spend_est DESC
LIMIT 25;

-- Q4d. Category-level promo dependency
-- Interpretation: Categories with high promo rates are discount-led.
-- Reducing blanket discounts in these categories risks volume; categories
-- with low promo rates can tolerate removal immediately.
SELECT
    category,
    COUNT(*)                                   AS n,
    ROUND(AVG(discount_applied_flag) * 100, 1) AS pct_discount,
    ROUND(AVG(promo_code_used_flag) * 100, 1)  AS pct_promo_code,
    ROUND(AVG(promo_dependency_score), 1)      AS avg_promo_score,
    ROUND(AVG(purchase_amount), 2)             AS avg_spend,
    ROUND(AVG(review_rating), 2)               AS avg_rating
FROM customers
GROUP BY category
ORDER BY avg_promo_score DESC;

-- Q4e. Hypothetical margin impact of sunset (rough estimate)
-- Assumes discount = ~15% off average ticket. Savings if Loyal + Organic
-- customers are removed from blanket discount campaigns.
SELECT
    ROUND(COUNT(*) * AVG(purchase_amount) * 0.15, 0) AS estimated_annual_discount_savings_usd,
    COUNT(*) AS affected_customers
FROM customers
WHERE final_segment IN ('Loyal High-Value', 'Organic Mid-Value')
  AND discount_applied_flag = 0;  -- already not using — safety count


-- =============================================================================
-- Q5: WHAT DOES THE IDEAL CUSTOMER PROFILE LOOK LIKE?
-- Business context: Define the brand's best customer type with enough specificity
-- that a marketing team can create lookalike audiences and targeting criteria.
-- =============================================================================

-- Q5a. Ideal customer aggregate profile
SELECT
    ROUND(AVG(age), 1)                              AS avg_age,
    ROUND(MIN(age), 0) || '-' || ROUND(MAX(age),0) AS age_full_range,
    ROUND(AVG(purchase_amount), 2)                  AS avg_order_value,
    ROUND(AVG(previous_purchases), 1)               AS avg_prev_purchases,
    ROUND(AVG(review_rating), 2)                    AS avg_rating,
    ROUND(AVG(promo_dependency_score), 1)           AS avg_promo_score,
    ROUND(AVG(retention_proxy_score), 1)            AS avg_retention_proxy,
    ROUND(AVG(total_spend_est), 0)                  AS avg_ltv_est,
    ROUND(AVG(is_subscribed) * 100, 1)              AS pct_subscribed
FROM customers
WHERE final_segment = 'Loyal High-Value';

-- Q5b. Ideal customer: demographic breakdown
SELECT gender, COUNT(*) AS n,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers WHERE final_segment='Loyal High-Value'), 1) AS pct
FROM customers WHERE final_segment = 'Loyal High-Value' GROUP BY gender;

-- Q5c. Ideal customer: category preferences
SELECT category, COUNT(*) AS n,
       ROUND(AVG(purchase_amount), 2) AS avg_spend,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers WHERE final_segment='Loyal High-Value'), 1) AS pct
FROM customers WHERE final_segment = 'Loyal High-Value'
GROUP BY category ORDER BY n DESC;

-- Q5d. Ideal customer: geographic concentration
SELECT location, COUNT(*) AS n,
       ROUND(AVG(purchase_amount), 2) AS avg_spend,
       ROUND(AVG(total_spend_est), 0) AS avg_ltv
FROM customers WHERE final_segment = 'Loyal High-Value'
GROUP BY location ORDER BY n DESC LIMIT 10;

-- Q5e. Ideal customer: purchase frequency distribution
SELECT frequency_of_purchases, COUNT(*) AS n,
       ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM customers WHERE final_segment='Loyal High-Value'),1) AS pct
FROM customers WHERE final_segment = 'Loyal High-Value'
GROUP BY frequency_of_purchases ORDER BY n DESC;

-- Q5f. Acquisition pipeline: customers who resemble ideal but aren't there yet
-- These are the candidates for nurture to top tier.
SELECT
    customer_id, age, gender, location, category,
    purchase_amount, previous_purchases,
    ROUND(review_rating, 1)            AS rating,
    ROUND(promo_dependency_score, 1)   AS promo_score,
    ROUND(retention_proxy_score, 1)    AS retention_proxy,
    final_segment
FROM customers
WHERE value_tier = 'Medium'
  AND promo_dependency_score < 30
  AND review_rating >= 3.5
  AND previous_purchases >= 15
ORDER BY total_spend_est DESC
LIMIT 20;


-- =============================================================================
-- DASHBOARD QUERIES — Power BI view outputs
-- =============================================================================

SELECT * FROM v_customer_pyramid;
SELECT * FROM v_promo_dependency_retention;
SELECT * FROM v_geography_opportunity;
SELECT * FROM v_category_funnel;
SELECT * FROM v_segment_summary;
SELECT * FROM v_ideal_customer_profile;
