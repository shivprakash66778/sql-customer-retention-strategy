-- =============================================================================
-- Decoding Customer Value: A SQL-Driven Retention Strategy
-- schema.sql — Database schema and view definitions
-- =============================================================================
-- Database: SQLite (customer_intelligence.db)
-- Run pipeline first: python main_pipeline.py
-- The pipeline creates all tables. This file documents the schema and
-- re-creates views if the DB is reset.
-- =============================================================================

-- ── Core customer table ────────────────────────────────────────────────────
-- One row per customer. Includes raw columns + all engineered features.
CREATE TABLE IF NOT EXISTS customers (
    -- Raw fields
    customer_id                INTEGER  PRIMARY KEY,
    age                        INTEGER,
    gender                     TEXT,
    item_purchased             TEXT,
    category                   TEXT,
    purchase_amount            REAL,
    location                   TEXT,
    size                       TEXT,
    color                      TEXT,
    season                     TEXT,
    review_rating              REAL,
    subscription_status        TEXT,
    payment_method             TEXT,
    shipping_type              TEXT,
    discount_applied           TEXT,
    promo_code_used            TEXT,
    previous_purchases         INTEGER,
    preferred_payment_method   TEXT,
    frequency_of_purchases     TEXT,

    -- Binary flags
    discount_applied_flag      INTEGER,  -- 1=Yes, 0=No
    promo_code_used_flag       INTEGER,  -- 1=Yes, 0=No
    is_subscribed              INTEGER,  -- 1=Yes, 0=No
    purchase_freq_annual       REAL,     -- Annual frequency (numeric)

    -- Value metrics
    total_spend_est            REAL,     -- purchase_amount × (previous_purchases+1)
    avg_order_value            REAL,     -- = purchase_amount (single observation)
    purchase_count             INTEGER,  -- previous_purchases + 1
    est_annual_spend           REAL,     -- purchase_amount × purchase_freq_annual
    value_tier                 TEXT,     -- High / Medium / Low (33/66 percentiles)

    -- Promo metrics
    promo_usage_rate           REAL,     -- avg(discount_flag, promo_flag) 0–1
    promo_dependency_score     REAL,     -- 0–100 composite score
    promo_segment              TEXT,     -- Organic Loyalist / Selective Promo User /
                                         -- Promo Dependent / Bargain Hunter

    -- Satisfaction
    satisfaction_tier          TEXT,     -- Dissatisfied / Neutral / Satisfied
    satisfaction_flag          INTEGER,  -- 1 if rating >= 4.0
    dissatisfied_high_value    INTEGER,  -- 1 if High value AND Dissatisfied

    -- Retention proxy (NOTE: timestamps absent — this is a proxy, not true retention)
    retention_proxy_score      REAL,     -- 0–100: 35% prev + 25% freq + 20% rating + 10% sub + 10% low promo
    retention_proxy_tier       TEXT,     -- Low / Medium / High Retention Signal

    -- Behavioral flags
    repeat_buyer               INTEGER,  -- 1 if previous_purchases >= 5
    high_frequency_buyer       INTEGER,  -- 1 if purchase_freq_annual >= 12
    purchase_history_tier      TEXT,     -- New(0-5) / Developing(6-15) / Established(16+)

    -- Loyalty scores
    loyalty_score_1            REAL,     -- Behavioral loyalty (0–1)
    loyalty_def1               TEXT,     -- Low / Medium / High Loyalty
    loyalty_score_2            REAL,     -- Commercial loyalty (0–1)
    loyalty_def2               TEXT,     -- Low / Medium / High Loyalty
    loyalty_segment            TEXT,     -- Selected definition tier

    -- Geography
    geo_opportunity            TEXT,     -- High / Medium / Low Opportunity
    opportunity_score          INTEGER,  -- 0–5 flag count
    geo_avg_spend              REAL,
    geo_promo_rate             REAL,
    geo_customer_count         INTEGER,
    geo_hv_share               REAL,     -- fraction of high-value customers in state

    -- Final segment
    final_segment              TEXT      -- Actionable segment label
);

-- ── Dashboard summary tables ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS segment_summary (
    final_segment              TEXT  PRIMARY KEY,
    customer_count             INTEGER,
    avg_purchase_amount        REAL,
    avg_total_spend_est        REAL,
    avg_previous_purchases     REAL,
    avg_review_rating          REAL,
    avg_promo_dependency       REAL,
    avg_retention_proxy        REAL,
    pct_discount_applied       REAL,
    pct_promo_code_used        REAL,
    pct_subscribed             REAL,
    avg_age                    REAL,
    avg_loyalty_score          REAL,
    revenue_share_pct          REAL,
    segment_definition         TEXT
);

CREATE TABLE IF NOT EXISTS geography_opportunity (
    location                   TEXT  PRIMARY KEY,
    geo_customer_count         INTEGER,
    geo_avg_spend              REAL,
    geo_avg_prev_purchases     REAL,
    geo_avg_rating             REAL,
    geo_promo_rate             REAL,
    geo_total_revenue_est      REAL,
    geo_promo_dependency       REAL,
    geo_retention_proxy        REAL,
    geo_hv_share               REAL,
    loyal_hv_count             INTEGER,
    flag_high_density          INTEGER,
    flag_high_spend            INTEGER,
    flag_low_promo             INTEGER,
    flag_high_sat              INTEGER,
    flag_high_hv_share         INTEGER,
    opportunity_score          INTEGER,
    geo_opportunity            TEXT
);

CREATE TABLE IF NOT EXISTS category_funnel (
    category                   TEXT,
    purchase_history_tier      TEXT,
    customer_count             INTEGER,
    avg_spend                  REAL,
    avg_promo_dep              REAL,
    avg_rating                 REAL,
    pct_high_value             REAL,
    PRIMARY KEY (category, purchase_history_tier)
);

CREATE TABLE IF NOT EXISTS category_summary (
    category                   TEXT  PRIMARY KEY,
    total_customers            INTEGER,
    avg_spend                  REAL,
    avg_prev_purchases         REAL,
    avg_promo_dependency       REAL,
    avg_rating                 REAL,
    pct_high_value             REAL,
    pct_repeat_buyer           REAL,
    avg_retention_proxy        REAL,
    category_role              TEXT
);

CREATE TABLE IF NOT EXISTS customer_pyramid (
    value_tier                 TEXT  PRIMARY KEY,
    customer_count             INTEGER,
    avg_spend                  REAL,
    total_revenue_est          REAL,
    avg_promo_score            REAL,
    avg_rating                 REAL,
    avg_retention              REAL,
    pct_of_customers           REAL,
    pct_of_revenue             REAL
);

CREATE TABLE IF NOT EXISTS promo_dependency_retention (
    final_segment              TEXT  PRIMARY KEY,
    customer_count             INTEGER,
    avg_promo_dependency       REAL,
    avg_retention_proxy        REAL,
    avg_previous_purchases     REAL,
    avg_loyalty_score          REAL,
    avg_satisfaction           REAL,
    avg_spend                  REAL,
    pct_subscribed             REAL,
    pct_organic                REAL
);

CREATE TABLE IF NOT EXISTS ideal_customer_profile (
    Attribute                  TEXT  PRIMARY KEY,
    Value                      TEXT,
    Business_Implication       TEXT
);

-- ── Power BI dashboard views ───────────────────────────────────────────────

-- Panel 1: Customer Value Pyramid
CREATE VIEW IF NOT EXISTS v_customer_pyramid AS
    SELECT value_tier,
           customer_count,
           ROUND(avg_spend, 2)           AS avg_spend,
           ROUND(total_revenue_est, 0)   AS total_revenue_est,
           ROUND(avg_retention, 1)       AS avg_retention_proxy,
           pct_of_customers,
           pct_of_revenue
    FROM customer_pyramid
    ORDER BY CASE value_tier WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

-- Panel 2: Promo Dependency vs. Retention Proxy
CREATE VIEW IF NOT EXISTS v_promo_dependency_retention AS
    SELECT final_segment,
           customer_count,
           ROUND(avg_promo_dependency, 1)  AS avg_promo_dependency,
           ROUND(avg_retention_proxy, 1)   AS avg_retention_proxy,
           ROUND(avg_spend, 2)             AS avg_spend,
           ROUND(avg_satisfaction, 2)      AS avg_satisfaction,
           ROUND(pct_subscribed * 100, 1)  AS pct_subscribed,
           ROUND(pct_organic * 100, 1)     AS pct_organic
    FROM promo_dependency_retention
    ORDER BY avg_promo_dependency DESC;

-- Panel 3: Geographic Opportunity Map
CREATE VIEW IF NOT EXISTS v_geography_opportunity AS
    SELECT location,
           geo_customer_count,
           ROUND(geo_avg_spend, 2)          AS avg_spend,
           ROUND(geo_promo_rate, 3)         AS promo_rate,
           ROUND(geo_avg_rating, 2)         AS avg_rating,
           ROUND(geo_hv_share * 100, 1)     AS hv_share_pct,
           loyal_hv_count,
           opportunity_score,
           geo_opportunity
    FROM geography_opportunity
    ORDER BY opportunity_score DESC, geo_avg_spend DESC;

-- Panel 4: Category Funnel
CREATE VIEW IF NOT EXISTS v_category_funnel AS
    SELECT category,
           purchase_history_tier,
           customer_count,
           ROUND(avg_spend, 2)              AS avg_spend,
           ROUND(avg_promo_dep, 1)          AS avg_promo_dependency,
           ROUND(avg_rating, 2)             AS avg_rating,
           ROUND(pct_high_value * 100, 1)   AS pct_high_value
    FROM category_funnel
    ORDER BY category, purchase_history_tier;

-- Full segment summary
CREATE VIEW IF NOT EXISTS v_segment_summary AS
    SELECT final_segment,
           customer_count,
           ROUND(avg_purchase_amount, 2)    AS avg_order_value,
           ROUND(avg_total_spend_est, 0)    AS avg_lifetime_value,
           ROUND(avg_previous_purchases, 1) AS avg_prev_purchases,
           ROUND(avg_review_rating, 2)      AS avg_rating,
           ROUND(avg_promo_dependency, 1)   AS avg_promo_score,
           ROUND(avg_retention_proxy, 1)    AS avg_retention_proxy,
           ROUND(pct_discount_applied*100, 1) AS pct_discount,
           ROUND(pct_subscribed * 100, 1)   AS pct_subscribed,
           revenue_share_pct,
           segment_definition
    FROM segment_summary
    ORDER BY revenue_share_pct DESC;

-- Ideal customer profile
CREATE VIEW IF NOT EXISTS v_ideal_customer_profile AS
    SELECT * FROM ideal_customer_profile;

-- ── Segment filter views ───────────────────────────────────────────────────
CREATE VIEW IF NOT EXISTS v_loyal_high_value AS
    SELECT * FROM customers WHERE final_segment = 'Loyal High-Value';

CREATE VIEW IF NOT EXISTS v_hv_promo_dependent AS
    SELECT * FROM customers WHERE final_segment = 'High-Value Promo-Dependent';

CREATE VIEW IF NOT EXISTS v_at_risk AS
    SELECT * FROM customers WHERE final_segment = 'At-Risk Dissatisfied';

CREATE VIEW IF NOT EXISTS v_organic_mid AS
    SELECT * FROM customers WHERE final_segment = 'Organic Mid-Value';

CREATE VIEW IF NOT EXISTS v_bargain_hunters AS
    SELECT * FROM customers WHERE final_segment = 'Low-Repeat Bargain Hunter';

-- ── Indexes for query performance ─────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_segment    ON customers(final_segment);
CREATE INDEX IF NOT EXISTS idx_value_tier ON customers(value_tier);
CREATE INDEX IF NOT EXISTS idx_location   ON customers(location);
CREATE INDEX IF NOT EXISTS idx_category   ON customers(category);
CREATE INDEX IF NOT EXISTS idx_loyalty    ON customers(loyalty_segment);
CREATE INDEX IF NOT EXISTS idx_promo_seg  ON customers(promo_segment);
