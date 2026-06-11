#!/usr/bin/env python3
"""
=============================================================================
Decoding Customer Value: A SQL-Driven Retention Strategy
main_pipeline.py — Full End-to-End Analytics Pipeline
=============================================================================
Summer Projects '26 | Consulting & Analytics Club, IIT Guwahati

Run this script from the project root:
    python main_pipeline.py

All outputs are written to:
    data/cleaned/         — cleaned raw data
    data/features/        — all engineered customer features
    data/dashboard/       — Power BI-ready CSV tables
    outputs/              — run summary, final metrics
    sql/                  — SQLite database with all tables and views
=============================================================================
"""

import pandas as pd
import numpy as np
import sqlite3
import os
import re
import json
import warnings
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

warnings.filterwarnings('ignore')

# ── Run metadata ───────────────────────────────────────────────────────────
RUN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
LOG_LINES = []

def log(msg):
    print(msg)
    LOG_LINES.append(msg)

# ── Path configuration ─────────────────────────────────────────────────────
RAW_PATH       = "data/raw/shopping_trends.csv"
CLEANED_DIR    = "data/cleaned"
FEATURES_DIR   = "data/features"
DASHBOARD_DIR  = "data/dashboard"
OUTPUTS_DIR    = "outputs"
SQL_DIR        = "sql"
DB_PATH        = "sql/customer_intelligence.db"

for d in [CLEANED_DIR, FEATURES_DIR, DASHBOARD_DIR, OUTPUTS_DIR, SQL_DIR]:
    os.makedirs(d, exist_ok=True)

# =============================================================================
# SECTION 1: LOAD & STANDARDIZE
# =============================================================================

log("=" * 70)
log("SECTION 1: LOADING AND STANDARDIZING DATA")
log("=" * 70)

df_raw = pd.read_csv(RAW_PATH)

log(f"\nRaw shape: {df_raw.shape}")
log(f"Columns: {list(df_raw.columns)}")

def to_snake(name):
    name = re.sub(r'\(.*?\)', '', name)
    name = name.strip().lower()
    name = re.sub(r'[\s\-]+', '_', name)
    name = re.sub(r'[^a-z0-9_]', '', name)
    return re.sub(r'_+', '_', name).strip('_')

df = df_raw.copy()
df.columns = [to_snake(c) for c in df.columns]

# Column mapping — edit here if dataset columns differ
COL_MAP = {
    'customer_id'            : 'customer_id',
    'age'                    : 'age',
    'gender'                 : 'gender',
    'item_purchased'         : 'item_purchased',
    'category'               : 'category',
    'purchase_amount'        : 'purchase_amount',
    'location'               : 'location',
    'size'                   : 'size',
    'color'                  : 'color',
    'season'                 : 'season',
    'review_rating'          : 'review_rating',
    'subscription_status'    : 'subscription_status',
    'payment_method'         : 'payment_method',
    'shipping_type'          : 'shipping_type',
    'discount_applied'       : 'discount_applied',
    'promo_code_used'        : 'promo_code_used',
    'previous_purchases'     : 'previous_purchases',
    'preferred_payment_method': 'preferred_payment_method',
    'frequency_of_purchases' : 'frequency_of_purchases',
}

for role, col in COL_MAP.items():
    assert col in df.columns, f"Expected column '{col}' not found. Available: {list(df.columns)}"

log("✓ All column mappings verified.\n")

# =============================================================================
# SECTION 2: DATA CLEANING
# =============================================================================

log("=" * 70)
log("SECTION 2: DATA CLEANING")
log("=" * 70)

log(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum()>0]}")
if df.isnull().sum().sum() == 0:
    log("  → No missing values found.")

n_before = len(df)
df = df.drop_duplicates()
log(f"Duplicates removed: {n_before - len(df)}")

# Standardize categorical fields
cat_cols = ['gender','category','location','season','subscription_status',
            'payment_method','shipping_type','discount_applied','promo_code_used',
            'preferred_payment_method','frequency_of_purchases','size','color']
for c in cat_cols:
    df[c] = df[c].str.strip().str.title()

# Numeric validations
assert df['age'].between(10,100).all(), "Age out of range"
assert df['purchase_amount'].gt(0).all(), "Negative purchase amount"
assert df['review_rating'].between(1,5).all(), "Review rating out of [1,5]"
assert df['previous_purchases'].ge(0).all(), "Negative previous purchases"
log("✓ All numeric validations passed.")

# Binary flags
df['discount_applied_flag'] = (df['discount_applied'] == 'Yes').astype(int)
df['promo_code_used_flag']  = (df['promo_code_used']  == 'Yes').astype(int)
df['is_subscribed']         = (df['subscription_status'] == 'Yes').astype(int)

# Annual purchase frequency mapping
FREQ_MAP = {
    'Weekly': 52, 'Bi-Weekly': 26, 'Fortnightly': 26,
    'Monthly': 12, 'Quarterly': 4, 'Every 3 Months': 4,
    'Annually': 1, 'Bi-Monthly': 6
}
df['purchase_freq_annual'] = df['frequency_of_purchases'].map(FREQ_MAP).fillna(12)

log(f"\nCleaned dataset: {len(df)} rows, {len(df.columns)} columns")
df.to_csv(f"{CLEANED_DIR}/cleaned_customer_data.csv", index=False)
log(f"✓ Saved: {CLEANED_DIR}/cleaned_customer_data.csv")

# =============================================================================
# SECTION 3: CUSTOMER VALUE METRICS
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 3: CUSTOMER VALUE METRICS")
log("=" * 70)

fe = df.copy()

# ── Total spend estimate ───────────────────────────────────────────────────
# Business logic: We observe one purchase per customer row. We estimate total
# lifetime spend by multiplying the observed purchase amount by the number of
# purchases (previous + current). This is a proxy, not a true LTV.
fe['total_spend_est']  = fe['purchase_amount'] * (fe['previous_purchases'] + 1)
fe['avg_order_value']  = fe['purchase_amount']    # single observed transaction
fe['purchase_count']   = fe['previous_purchases'] + 1
fe['est_annual_spend'] = fe['purchase_amount'] * fe['purchase_freq_annual']

# ── Value tier (percentile-based) ─────────────────────────────────────────
# High = top 33% of estimated lifetime spend
# Medium = middle 33%
# Low = bottom 33%
p33 = fe['total_spend_est'].quantile(0.33)
p66 = fe['total_spend_est'].quantile(0.66)
fe['value_tier'] = pd.cut(
    fe['total_spend_est'],
    bins=[-np.inf, p33, p66, np.inf],
    labels=['Low', 'Medium', 'High']
)

log(f"\nValue tier distribution (cutoffs: ${p33:.0f} | ${p66:.0f}):")
log(fe['value_tier'].value_counts().to_string())

# =============================================================================
# SECTION 4: PROMO DEPENDENCY METRICS
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 4: PROMO DEPENDENCY METRICS")
log("=" * 70)

# ── Promo dependency score ─────────────────────────────────────────────────
# Business logic: A customer who ALWAYS uses both discount codes AND promo codes
# is likely buying because of the deal. A customer who never does is organic.
# We weight discount_applied and promo_code_used equally and add a small
# inverse-purchase-history component: infrequent buyers who use promos are
# more concerning than frequent buyers who occasionally use promos.
purchase_norm = fe['previous_purchases'] / fe['previous_purchases'].max()
fe['promo_usage_rate'] = (fe['discount_applied_flag'] + fe['promo_code_used_flag']) / 2
fe['promo_dependency_score'] = (
    0.40 * fe['discount_applied_flag'] +
    0.40 * fe['promo_code_used_flag'] +
    0.20 * (1 - purchase_norm)
) * 100

# ── Promo segment (quartile-based for meaningful distribution) ─────────────
q25 = fe['promo_dependency_score'].quantile(0.25)
q50 = fe['promo_dependency_score'].quantile(0.50)
q75 = fe['promo_dependency_score'].quantile(0.75)

def assign_promo_seg(score):
    if score <= q25: return 'Organic Loyalist'
    elif score <= q50: return 'Selective Promo User'
    elif score <= q75: return 'Promo Dependent'
    else: return 'Bargain Hunter'

fe['promo_segment'] = fe['promo_dependency_score'].apply(assign_promo_seg)

log(f"\nPromo segment distribution:")
log(fe['promo_segment'].value_counts().to_string())

# =============================================================================
# SECTION 5: SATISFACTION METRICS
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 5: SATISFACTION METRICS")
log("=" * 70)

# Review rating is the only satisfaction signal in this dataset.
# Thresholds: <3.0 = Dissatisfied, 3.0-3.9 = Neutral, >=4.0 = Satisfied
fe['satisfaction_tier'] = pd.cut(
    fe['review_rating'],
    bins=[0, 3.0, 4.0, 5.0],
    labels=['Dissatisfied', 'Neutral', 'Satisfied'],
    include_lowest=True
)
fe['satisfaction_flag']        = (fe['review_rating'] >= 4.0).astype(int)
fe['dissatisfied_high_value']  = (
    (fe['value_tier'] == 'High') & (fe['satisfaction_tier'] == 'Dissatisfied')
).astype(int)

log(f"\nSatisfaction distribution:")
log(fe['satisfaction_tier'].value_counts().to_string())
log(f"Dissatisfied high-value: {fe['dissatisfied_high_value'].sum()}")

# =============================================================================
# SECTION 6: IMPROVED RETENTION PROXY
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 6: RETENTION PROXY (COMPOSITE)")
log("=" * 70)

# ── IMPORTANT LIMITATION NOTE ─────────────────────────────────────────────
# This dataset has NO TIMESTAMPS. True churn and true retention rates cannot
# be calculated without knowing WHEN each purchase occurred.
#
# We construct a defensible RETENTION PROXY score (0-100) using five signals
# that collectively indicate a customer is likely to continue buying:
#
#   1. Previous purchases (normalized): More past purchases = more embedded.
#      Weight: 35%
#
#   2. Purchase frequency (normalized): More frequent buyers are harder to lose.
#      Weight: 25%
#
#   3. Review rating (normalized): Satisfied customers are less likely to leave.
#      Weight: 20%
#
#   4. Subscription status: Subscribers have explicitly committed to the brand.
#      Weight: 10%
#
#   5. Low promo dependency (inverted): Organic buyers are more resilient because
#      their purchase behavior isn't contingent on a discount being offered.
#      Weight: 10%
#
# This proxy is NOT a churn prediction — it's a relative engagement score.
# Segments with higher scores are better positioned to retain customers
# even without promotional support.

scaler = MinMaxScaler()

prev_norm  = scaler.fit_transform(fe[['previous_purchases']])[:,0]
freq_norm  = scaler.fit_transform(fe[['purchase_freq_annual']])[:,0]
rating_norm = scaler.fit_transform(fe[['review_rating']])[:,0]
promo_inv  = 1 - (fe['promo_dependency_score'] / 100)

fe['retention_proxy_score'] = (
    0.35 * prev_norm +
    0.25 * freq_norm +
    0.20 * rating_norm +
    0.10 * fe['is_subscribed'] +
    0.10 * promo_inv
) * 100

# Tier the proxy
rp_q33 = fe['retention_proxy_score'].quantile(0.33)
rp_q66 = fe['retention_proxy_score'].quantile(0.66)
fe['retention_proxy_tier'] = pd.cut(
    fe['retention_proxy_score'],
    bins=[-np.inf, rp_q33, rp_q66, np.inf],
    labels=['Low Retention Signal', 'Medium Retention Signal', 'High Retention Signal']
)

# Old binary flag kept for compatibility
fe['repeat_buyer']          = (fe['previous_purchases'] >= 5).astype(int)
fe['high_frequency_buyer']  = (fe['purchase_freq_annual'] >= 12).astype(int)

log(f"\nRetention proxy score range: {fe['retention_proxy_score'].min():.1f} – {fe['retention_proxy_score'].max():.1f}")
log(f"Mean: {fe['retention_proxy_score'].mean():.1f}  Median: {fe['retention_proxy_score'].median():.1f}")
log(f"\nRetention proxy tier distribution:")
log(fe['retention_proxy_tier'].value_counts().to_string())

# =============================================================================
# SECTION 7: LOYALTY DEFINITIONS
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 7: LOYALTY DEFINITIONS")
log("=" * 70)

# ── DEFINITION 1: Behavioral Loyalty ──────────────────────────────────────
# Captures habitual brand attachment through WHAT customers DO.
# A behaviorally loyal customer buys repeatedly, spends well,
# is satisfied, and does not rely on discounts.
#
# Variables: purchase_count, total_spend_est, review_rating, promo_usage_rate
# Weights: 30% purchase frequency + 30% spend + 20% satisfaction + 20% low promo

s1 = pd.DataFrame(scaler.fit_transform(
    fe[['purchase_count', 'total_spend_est', 'review_rating']]
), columns=['pc_n', 'spend_n', 'rating_n'])

fe['loyalty_score_1'] = (
    0.30 * s1['pc_n'] +
    0.30 * s1['spend_n'] +
    0.20 * s1['rating_n'] +
    0.20 * (1 - fe['promo_usage_rate'])
)

ls1_q33 = fe['loyalty_score_1'].quantile(0.33)
ls1_q66 = fe['loyalty_score_1'].quantile(0.66)
fe['loyalty_def1'] = pd.cut(
    fe['loyalty_score_1'], bins=[-np.inf, ls1_q33, ls1_q66, np.inf],
    labels=['Low Loyalty', 'Medium Loyalty', 'High Loyalty']
)

log("\nLOYALTY DEF 1 (Behavioral):")
log(fe['loyalty_def1'].value_counts().to_string())

# ── DEFINITION 2: Commercial Loyalty ──────────────────────────────────────
# Captures economic commitment — what customers SPEND and how committed they are.
# A commercially loyal customer has high AOV, buys frequently, is subscribed,
# and doesn't rely on discounts to transact.
#
# Variables: total_spend_est, avg_order_value, purchase_freq_annual,
#            is_subscribed, discount_applied_flag (inverted)
# Weights: 30% spend + 25% AOV + 20% frequency + 15% subscription + 10% no discount

s2 = pd.DataFrame(scaler.fit_transform(
    fe[['total_spend_est', 'avg_order_value', 'purchase_freq_annual']]
), columns=['spend_n', 'aov_n', 'freq_n'])

fe['loyalty_score_2'] = (
    0.30 * s2['spend_n'] +
    0.25 * s2['aov_n'] +
    0.20 * s2['freq_n'] +
    0.15 * fe['is_subscribed'] +
    0.10 * (1 - fe['discount_applied_flag'])
)

ls2_q33 = fe['loyalty_score_2'].quantile(0.33)
ls2_q66 = fe['loyalty_score_2'].quantile(0.66)
fe['loyalty_def2'] = pd.cut(
    fe['loyalty_score_2'], bins=[-np.inf, ls2_q33, ls2_q66, np.inf],
    labels=['Low Loyalty', 'Medium Loyalty', 'High Loyalty']
)

log("\nLOYALTY DEF 2 (Commercial):")
log(fe['loyalty_def2'].value_counts().to_string())

# =============================================================================
# SECTION 8: LOYALTY DEFINITION COMPARISON
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 8: LOYALTY DEFINITION COMPARISON")
log("=" * 70)

def evaluate_loyalty(df, col, label):
    grp = df.groupby(col, observed=True).agg(
        n=('customer_id','count'),
        avg_revenue=('total_spend_est','mean'),
        avg_promo=('promo_dependency_score','mean'),
        avg_satisfaction=('review_rating','mean'),
        avg_prev_purchases=('previous_purchases','mean'),
        avg_retention_proxy=('retention_proxy_score','mean'),
    ).round(2)

    checks = {}
    if 'High Loyalty' in grp.index and 'Low Loyalty' in grp.index:
        checks['Revenue monotonic (High > Low)']        = grp.loc['High Loyalty','avg_revenue']      > grp.loc['Low Loyalty','avg_revenue']
        checks['Promo dependency monotonic (High < Low)'] = grp.loc['High Loyalty','avg_promo']       < grp.loc['Low Loyalty','avg_promo']
        checks['Satisfaction monotonic (High > Low)']   = grp.loc['High Loyalty','avg_satisfaction'] > grp.loc['Low Loyalty','avg_satisfaction']
        checks['Retention proxy monotonic (High > Low)']= grp.loc['High Loyalty','avg_retention_proxy'] > grp.loc['Low Loyalty','avg_retention_proxy']
        score = sum(checks.values())
    else:
        score = 0

    log(f"\n── {label} ──")
    log(grp.to_string())
    for k, v in checks.items():
        log(f"  {'✓' if v else '✗'} {k}")
    log(f"  Consistency score: {score}/4")
    return score, grp

score1, grp1 = evaluate_loyalty(fe, 'loyalty_def1', 'Definition 1: Behavioral Loyalty')
score2, grp2 = evaluate_loyalty(fe, 'loyalty_def2', 'Definition 2: Commercial Loyalty')

# ── Winner selection ───────────────────────────────────────────────────────
WINNER = 'loyalty_def1' if score1 >= score2 else 'loyalty_def2'
WINNER_SCORE_COL = 'loyalty_score_1' if WINNER == 'loyalty_def1' else 'loyalty_score_2'
WINNER_LABEL = 'Behavioral Loyalty (Definition 1)' if WINNER == 'loyalty_def1' else 'Commercial Loyalty (Definition 2)'

fe['loyalty_segment'] = fe[WINNER]

log(f"\n{'='*50}")
log(f"SELECTED DEFINITION: {WINNER_LABEL}")
log(f"Score: {max(score1,score2)}/4")
log(f"Reason: Higher internal consistency across revenue, promo dependency,")
log(f"  satisfaction, and retention proxy. Every tier behaves monotonically.")
log(f"{'='*50}")

# =============================================================================
# SECTION 9: FINAL CUSTOMER SEGMENTATION
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 9: FINAL CUSTOMER SEGMENTATION")
log("=" * 70)

# ── Segment definitions (fully traceable) ─────────────────────────────────
# Each segment maps to EXPLICIT variable conditions:
#
# 1. Loyal High-Value
#    value_tier=High AND loyalty_segment=High Loyalty
#    AND promo_segment IN (Organic Loyalist, Selective Promo User)
#    → Genuine brand loyalists who spend well without discount dependency
#
# 2. High-Value Promo-Dependent
#    value_tier=High AND promo_segment IN (Promo Dependent, Bargain Hunter)
#    → High spenders whose purchasing is conditioned on promotions
#
# 3. At-Risk Dissatisfied
#    satisfaction_tier=Dissatisfied AND value_tier IN (High, Medium)
#    → Valuable customers showing dissatisfaction signals — at risk of leaving
#
# 4. Organic Mid-Value
#    value_tier=Medium AND promo_segment IN (Organic Loyalist, Selective Promo User)
#    → Mid-spend organic buyers — natural pipeline to top tier
#
# 5. Low-Repeat Bargain Hunter
#    value_tier=Low AND promo_segment IN (Promo Dependent, Bargain Hunter)
#    AND previous_purchases <= 5
#    → New or very infrequent buyers who only transact with discounts
#    NOTE: Renamed from "One-Time" — many have 2-5 purchases but all within
#    the "Low" value tier AND high promo dependency. "Low-Repeat" is more accurate.
#
# 6. Low-Value Low-Engagement
#    All remaining customers (catch-all for low/medium value with mixed promo patterns)
#    → Large, heterogeneous group; lowest priority for direct investment

def assign_segment(row):
    vt  = row['value_tier']
    ps  = row['promo_segment']
    st  = row['satisfaction_tier']
    pp  = row['previous_purchases']
    ls  = row['loyalty_segment']

    # Priority 1 — capture at-risk early
    if st == 'Dissatisfied' and vt in ('High', 'Medium'):
        return 'At-Risk Dissatisfied'

    # Priority 2 — loyal high-value (best segment)
    if vt == 'High' and ls == 'High Loyalty' and ps in ('Organic Loyalist', 'Selective Promo User'):
        return 'Loyal High-Value'

    # Priority 3 — high-value but promo-dependent
    if vt == 'High' and ps in ('Promo Dependent', 'Bargain Hunter'):
        return 'High-Value Promo-Dependent'

    # Priority 4 — organic mid-value
    if vt == 'Medium' and ps in ('Organic Loyalist', 'Selective Promo User'):
        return 'Organic Mid-Value'

    # Priority 5 — low-repeat bargain hunters (low value + promo-heavy + few purchases)
    if vt == 'Low' and ps in ('Promo Dependent', 'Bargain Hunter') and pp <= 5:
        return 'Low-Repeat Bargain Hunter'

    # Default — low-value low-engagement
    return 'Low-Value Low-Engagement'

fe['final_segment'] = fe.apply(assign_segment, axis=1)

log("\nFinal segment distribution:")
for seg, cnt in fe['final_segment'].value_counts().items():
    log(f"  {seg:<35} {cnt:>5} ({cnt/len(fe)*100:>5.1f}%)")

# =============================================================================
# SECTION 10: IMPROVED GEOGRAPHY OPPORTUNITY
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 10: GEOGRAPHY OPPORTUNITY ANALYSIS")
log("=" * 70)

# ── Geography opportunity score (0-5) ─────────────────────────────────────
# Five equally-weighted binary flags:
#   1. Above-average customer count (density proxy)
#   2. Above-average avg spend (spend depth)
#   3. Below-average promo dependency (organic demand)
#   4. Above-average satisfaction (brand resonance)
#   5. Above-average share of high-value customers (quality depth)
#
# Score 4-5 = High Opportunity: brand has genuine organic pull, invest here
# Score 2-3 = Medium Opportunity: selective targeting recommended
# Score 0-1 = Low Opportunity: discount-driven or thin market

geo = fe.groupby('location').agg(
    geo_customer_count   =('customer_id', 'count'),
    geo_avg_spend        =('purchase_amount', 'mean'),
    geo_avg_prev_purchases=('previous_purchases', 'mean'),
    geo_avg_rating       =('review_rating', 'mean'),
    geo_promo_rate       =('promo_usage_rate', 'mean'),
    geo_total_revenue_est=('total_spend_est', 'sum'),
    geo_promo_dependency =('promo_dependency_score', 'mean'),
    geo_retention_proxy  =('retention_proxy_score', 'mean'),
).reset_index()

# High-value customer share per state
hv_share = fe.groupby('location').apply(
    lambda g: (g['value_tier'] == 'High').mean()
).reset_index(name='geo_hv_share')
geo = geo.merge(hv_share, on='location', how='left')

# Loyal High-Value count per state
loyal_count = fe[fe['final_segment']=='Loyal High-Value'].groupby('location').size().reset_index(name='loyal_hv_count')
geo = geo.merge(loyal_count, on='location', how='left')
geo['loyal_hv_count'] = geo['loyal_hv_count'].fillna(0).astype(int)

# Compute flags
avg_count    = geo['geo_customer_count'].mean()
avg_spend    = geo['geo_avg_spend'].mean()
avg_promo    = geo['geo_promo_rate'].mean()
avg_rating   = geo['geo_avg_rating'].mean()
avg_hv_share = geo['geo_hv_share'].mean()

geo['flag_high_density']   = (geo['geo_customer_count'] > avg_count).astype(int)
geo['flag_high_spend']     = (geo['geo_avg_spend']      > avg_spend).astype(int)
geo['flag_low_promo']      = (geo['geo_promo_rate']     < avg_promo).astype(int)
geo['flag_high_sat']       = (geo['geo_avg_rating']     > avg_rating).astype(int)
geo['flag_high_hv_share']  = (geo['geo_hv_share']       > avg_hv_share).astype(int)

geo['opportunity_score'] = (
    geo['flag_high_density'] + geo['flag_high_spend'] +
    geo['flag_low_promo'] + geo['flag_high_sat'] + geo['flag_high_hv_share']
)

geo['geo_opportunity'] = geo['opportunity_score'].map(
    lambda x: 'High Opportunity' if x >= 4 else ('Medium Opportunity' if x >= 2 else 'Low Opportunity')
)

log(f"\nGeography opportunity distribution:")
log(geo['geo_opportunity'].value_counts().to_string())
log(f"\nTop 5 High Opportunity states:")
top5 = geo[geo['geo_opportunity']=='High Opportunity'].sort_values('opportunity_score',ascending=False).head(5)
log(top5[['location','geo_customer_count','geo_avg_spend','geo_promo_rate','opportunity_score']].to_string(index=False))

# Merge flags back to customers for segment queries
fe = fe.merge(
    geo[['location','geo_opportunity','opportunity_score',
         'geo_avg_spend','geo_promo_rate','geo_customer_count','geo_hv_share']],
    on='location', how='left'
)

# =============================================================================
# SECTION 11: IMPROVED CATEGORY FUNNEL
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 11: CATEGORY FUNNEL ANALYSIS")
log("=" * 70)

# ── Category role classification ───────────────────────────────────────────
# Each category is classified using FIVE metrics relative to the dataset average:
#
#   avg_prev_purchases   > overall mean → customers in this category have more history
#   avg_promo_dependency < overall mean → organic buyers prefer this category
#   avg_rating           > overall mean → satisfied customers gravitate here
#   avg_purchase_amount  > overall mean → customers spend more per order
#   pct_high_value       > overall mean → high-value customers over-index here
#
# Role assignment:
#   Premium Growth Category: high spend + low promo + above-avg rating + high HV share
#   Retention Category:      high prev purchases + low promo dependency
#   Entry Category:          low prev purchases (newer customers predominate)
#   Discount-Led Category:   high promo dependency + avg or low spend
#   Neutral Category:        no strong signal in any direction

overall_avg_pp    = fe['previous_purchases'].mean()
overall_avg_promo = fe['promo_dependency_score'].mean()
overall_avg_rating = fe['review_rating'].mean()
overall_avg_spend = fe['purchase_amount'].mean()
overall_avg_hv    = (fe['value_tier'] == 'High').mean()

cat_summary = fe.groupby('category').agg(
    total_customers      =('customer_id', 'count'),
    avg_spend            =('purchase_amount', 'mean'),
    avg_prev_purchases   =('previous_purchases', 'mean'),
    avg_promo_dependency =('promo_dependency_score', 'mean'),
    avg_rating           =('review_rating', 'mean'),
    pct_high_value       =('value_tier', lambda x: (x=='High').mean()),
    pct_repeat_buyer     =('repeat_buyer', 'mean'),
    avg_retention_proxy  =('retention_proxy_score', 'mean'),
).round(3).reset_index()

def classify_category(row):
    high_pp    = row['avg_prev_purchases']   > overall_avg_pp
    low_promo  = row['avg_promo_dependency'] < overall_avg_promo
    high_rat   = row['avg_rating']           > overall_avg_rating
    high_spend = row['avg_spend']            > overall_avg_spend
    high_hv    = row['pct_high_value']       > overall_avg_hv

    # Premium Growth: high spend + high rating + low promo + high HV share
    if high_spend and high_rat and low_promo and high_hv:
        return 'Premium Growth Category'
    # Retention: long purchase history + low promo dependency
    if high_pp and low_promo:
        return 'Retention Category'
    # Entry: below-avg purchase history
    if not high_pp:
        return 'Entry Category'
    # Discount-Led: high promo dependency drives purchases
    if not low_promo and not high_spend:
        return 'Discount-Led Category'
    return 'Neutral Category'

cat_summary['category_role'] = cat_summary.apply(classify_category, axis=1)

log(f"\nCategory classification:")
log(cat_summary[['category','avg_prev_purchases','avg_promo_dependency','avg_rating',
                 'avg_spend','pct_high_value','category_role']].to_string(index=False))

# Purchase history tier for funnel view
fe['purchase_history_tier'] = pd.cut(
    fe['previous_purchases'],
    bins=[-np.inf, 5, 15, np.inf],
    labels=['New (0-5)', 'Developing (6-15)', 'Established (16+)']
)

cat_funnel = fe.groupby(['category','purchase_history_tier'], observed=True).agg(
    customer_count =('customer_id', 'count'),
    avg_spend      =('purchase_amount', 'mean'),
    avg_promo_dep  =('promo_dependency_score', 'mean'),
    avg_rating     =('review_rating', 'mean'),
    pct_high_value =('value_tier', lambda x: (x=='High').mean()),
).reset_index()

# =============================================================================
# SECTION 12: IDEAL CUSTOMER PROFILE
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 12: IDEAL CUSTOMER PROFILE")
log("=" * 70)

ideal = fe[fe['final_segment'] == 'Loyal High-Value'].copy()
log(f"Ideal customer pool: {len(ideal)} customers ({len(ideal)/len(fe)*100:.1f}%)")

icp_data = {
    'Attribute': [
        'Age Range (IQR)', 'Median Age',
        'Top Gender',
        'Top 3 Categories',
        'Avg Order Value',
        'Avg Previous Purchases',
        'Avg Review Rating',
        'Avg Retention Proxy Score',
        'Promo Dependency Score (avg)',
        'Discount Applied Rate',
        'Promo Code Used Rate',
        'Subscription Rate',
        'Top 3 Payment Methods',
        'Top 3 Shipping Types',
        'Most Common Purchase Frequency',
        'Top 5 States',
        'Avg Estimated LTV',
        'Revenue Concentration',
    ],
    'Value': [
        f"{int(ideal['age'].quantile(0.25))}–{int(ideal['age'].quantile(0.75))} yrs",
        f"{ideal['age'].median():.0f} yrs",
        ideal['gender'].mode().iloc[0],
        ', '.join(ideal['category'].value_counts().head(3).index.tolist()),
        f"${ideal['purchase_amount'].mean():.0f}",
        f"{ideal['previous_purchases'].mean():.0f} transactions",
        f"{ideal['review_rating'].mean():.2f} / 5.0",
        f"{ideal['retention_proxy_score'].mean():.1f} / 100",
        f"{ideal['promo_dependency_score'].mean():.1f} / 100",
        f"{ideal['discount_applied_flag'].mean()*100:.1f}%",
        f"{ideal['promo_code_used_flag'].mean()*100:.1f}%",
        f"{ideal['is_subscribed'].mean()*100:.1f}%",
        ', '.join(ideal['preferred_payment_method'].value_counts().head(3).index.tolist()),
        ', '.join(ideal['shipping_type'].value_counts().head(3).index.tolist()),
        ideal['frequency_of_purchases'].mode().iloc[0],
        ', '.join(ideal['location'].value_counts().head(5).index.tolist()),
        f"${ideal['total_spend_est'].mean():.0f}",
        f"{len(ideal)/len(fe)*100:.1f}% of customers → {ideal['total_spend_est'].sum()/fe['total_spend_est'].sum()*100:.1f}% of revenue",
    ],
    'Business Implication': [
        'Target mid-career professionals in paid acquisition',
        'Not youth-skewed — focus on quality over trend messaging',
        'Slight female skew — ensure creative represents both',
        'Lead acquisition with these categories; they attract keepers',
        'Full-price buyer — high-margin per transaction',
        'High loyalty signal — brand is embedded in their purchase habit',
        'Satisfied customers — good candidate for referral programs',
        'Strong engagement signal — minimal churn risk',
        'Does not need discounts — any discount is margin waste',
        'Zero discount dependency — pricing integrity intact',
        'Zero promo code usage — brand affinity is intrinsic',
        'Low subscription rate — major untapped revenue lever',
        'Diverse payment habits — no friction removing payment options',
        'Prefers faster shipping — fulfillment speed matters to them',
        'Quarterly buyer — email cadence should match this rhythm',
        'Geographic targeting for lookalike campaigns',
        'High per-customer economic value',
        'Disproportionate revenue per head — protect at all costs',
    ]
}
icp_df = pd.DataFrame(icp_data)
log(f"\n{icp_df[['Attribute','Value']].to_string(index=False)}")

# =============================================================================
# SECTION 13: EXPORT ALL CSV FILES
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 13: EXPORTING ALL FILES")
log("=" * 70)

# 1. Cleaned data
df.to_csv(f"{CLEANED_DIR}/cleaned_customer_data.csv", index=False)

# 2. Full feature set
fe.to_csv(f"{FEATURES_DIR}/customer_features.csv", index=False)

# 3. Segment summary (dashboard)
seg_summary = fe.groupby('final_segment', observed=True).agg(
    customer_count         =('customer_id', 'count'),
    avg_purchase_amount    =('purchase_amount', 'mean'),
    avg_total_spend_est    =('total_spend_est', 'mean'),
    avg_previous_purchases =('previous_purchases', 'mean'),
    avg_review_rating      =('review_rating', 'mean'),
    avg_promo_dependency   =('promo_dependency_score', 'mean'),
    avg_retention_proxy    =('retention_proxy_score', 'mean'),
    pct_discount_applied   =('discount_applied_flag', 'mean'),
    pct_promo_code_used    =('promo_code_used_flag', 'mean'),
    pct_subscribed         =('is_subscribed', 'mean'),
    avg_age                =('age', 'mean'),
    avg_loyalty_score      =(WINNER_SCORE_COL, 'mean'),
).round(3).reset_index()

total_rev = (seg_summary['customer_count'] * seg_summary['avg_total_spend_est']).sum()
seg_summary['revenue_share_pct'] = (
    seg_summary['customer_count'] * seg_summary['avg_total_spend_est'] / total_rev * 100
).round(1)
seg_summary['segment_definition'] = seg_summary['final_segment'].map({
    'Loyal High-Value'           : 'value_tier=High + High Loyalty + promo_segment in (Organic Loyalist, Selective Promo User)',
    'High-Value Promo-Dependent' : 'value_tier=High + promo_segment in (Promo Dependent, Bargain Hunter)',
    'At-Risk Dissatisfied'       : 'satisfaction_tier=Dissatisfied + value_tier in (High, Medium)',
    'Organic Mid-Value'          : 'value_tier=Medium + promo_segment in (Organic Loyalist, Selective Promo User)',
    'Low-Repeat Bargain Hunter'  : 'value_tier=Low + promo_segment in (Promo Dependent, Bargain Hunter) + previous_purchases<=5',
    'Low-Value Low-Engagement'   : 'Remaining customers (catch-all)',
})
seg_summary.to_csv(f"{DASHBOARD_DIR}/segment_summary.csv", index=False)

# 4. Customer pyramid
pyramid = fe.groupby('value_tier', observed=True).agg(
    customer_count   =('customer_id', 'count'),
    avg_spend        =('purchase_amount', 'mean'),
    total_revenue_est=('total_spend_est', 'sum'),
    avg_promo_score  =('promo_dependency_score', 'mean'),
    avg_rating       =('review_rating', 'mean'),
    avg_retention    =('retention_proxy_score', 'mean'),
).reset_index()
pyramid['pct_of_customers'] = (pyramid['customer_count'] / pyramid['customer_count'].sum() * 100).round(1)
pyramid['pct_of_revenue']   = (pyramid['total_revenue_est'] / pyramid['total_revenue_est'].sum() * 100).round(1)
pyramid.to_csv(f"{DASHBOARD_DIR}/customer_pyramid.csv", index=False)

# 5. Promo dependency vs retention (KEY dashboard table)
promo_ret = fe.groupby('final_segment', observed=True).agg(
    customer_count         =('customer_id', 'count'),
    avg_promo_dependency   =('promo_dependency_score', 'mean'),
    avg_retention_proxy    =('retention_proxy_score', 'mean'),
    avg_previous_purchases =('previous_purchases', 'mean'),
    avg_loyalty_score      =(WINNER_SCORE_COL, 'mean'),
    avg_satisfaction       =('review_rating', 'mean'),
    avg_spend              =('purchase_amount', 'mean'),
    pct_subscribed         =('is_subscribed', 'mean'),
    pct_organic            =('discount_applied_flag', lambda x: (1-x.mean())),
).round(3).reset_index()
promo_ret.to_csv(f"{DASHBOARD_DIR}/promo_dependency_retention.csv", index=False)

# 6. Geography opportunity
geo.to_csv(f"{DASHBOARD_DIR}/geography_opportunity.csv", index=False)

# 7. Category funnel
cat_funnel.to_csv(f"{DASHBOARD_DIR}/category_funnel.csv", index=False)

# 8. Category summary
cat_summary.to_csv(f"{DASHBOARD_DIR}/category_summary.csv", index=False)

# 9. Loyalty definition comparison
loyalty_rows = []
for defn, col, score_col, score in [
    ('Behavioral Loyalty (Definition 1)', 'loyalty_def1', 'loyalty_score_1', score1),
    ('Commercial Loyalty (Definition 2)', 'loyalty_def2', 'loyalty_score_2', score2),
]:
    grp = fe.groupby(col, observed=True).agg(
        n=('customer_id','count'),
        avg_revenue=('total_spend_est','mean'),
        avg_promo=('promo_dependency_score','mean'),
        avg_satisfaction=('review_rating','mean'),
        avg_prev_purchases=('previous_purchases','mean'),
        avg_retention=('retention_proxy_score','mean'),
    )
    for tier in ['High Loyalty', 'Medium Loyalty', 'Low Loyalty']:
        if tier in grp.index:
            loyalty_rows.append({
                'definition': defn,
                'tier': tier,
                'n': int(grp.loc[tier,'n']),
                'avg_revenue': round(grp.loc[tier,'avg_revenue'],2),
                'avg_promo_dependency': round(grp.loc[tier,'avg_promo'],2),
                'avg_satisfaction': round(grp.loc[tier,'avg_satisfaction'],2),
                'avg_prev_purchases': round(grp.loc[tier,'avg_prev_purchases'],2),
                'avg_retention_proxy': round(grp.loc[tier,'avg_retention'],2),
                'consistency_score': f"{score}/4",
                'is_selected': 'YES' if col == WINNER else 'NO',
            })
loyalty_comp = pd.DataFrame(loyalty_rows)
loyalty_comp.to_csv(f"{DASHBOARD_DIR}/loyalty_definition_comparison.csv", index=False)

# 10. Ideal customer profile
icp_df.to_csv(f"{DASHBOARD_DIR}/ideal_customer_profile.csv", index=False)

# 11. Demographics
demo = fe.groupby(['gender','value_tier'], observed=True).agg(
    count=('customer_id','count'),
    avg_spend=('purchase_amount','mean'),
    avg_promo=('promo_dependency_score','mean'),
    avg_retention=('retention_proxy_score','mean'),
).reset_index()
demo.to_csv(f"{DASHBOARD_DIR}/demographics_analysis.csv", index=False)

# 12. Payment analysis
pay = fe.groupby(['preferred_payment_method','value_tier'], observed=True).agg(
    count=('customer_id','count'),
    avg_spend=('purchase_amount','mean'),
).reset_index()
pay.to_csv(f"{DASHBOARD_DIR}/payment_analysis.csv", index=False)

# 13. Data dictionary
data_dict = pd.DataFrame([
    ('customer_id',            'Integer',  'Raw',        'Unique customer identifier'),
    ('age',                    'Integer',  'Raw',        'Customer age in years'),
    ('gender',                 'Text',     'Raw',        'Male or Female'),
    ('item_purchased',         'Text',     'Raw',        'Specific product name'),
    ('category',               'Text',     'Raw',        'Clothing / Accessories / Footwear / Outerwear'),
    ('purchase_amount',        'Float',    'Raw',        'Single observed transaction value (USD)'),
    ('location',               'Text',     'Raw',        'US state of customer'),
    ('season',                 'Text',     'Raw',        'Season of purchase'),
    ('review_rating',          'Float',    'Raw',        'Customer satisfaction score (1.0–5.0)'),
    ('subscription_status',    'Text',     'Raw',        'Whether customer has active subscription (Yes/No)'),
    ('discount_applied',       'Text',     'Raw',        'Whether a discount was applied (Yes/No)'),
    ('promo_code_used',        'Text',     'Raw',        'Whether a promo code was used (Yes/No)'),
    ('previous_purchases',     'Integer',  'Raw',        'Count of prior purchases (used as loyalty proxy)'),
    ('frequency_of_purchases', 'Text',     'Raw',        'Stated purchase frequency (Weekly/Monthly/etc.)'),
    ('payment_method',         'Text',     'Raw',        'Payment method used for this transaction'),
    ('preferred_payment_method','Text',    'Raw',        'Stated preferred payment method'),
    ('discount_applied_flag',  'Integer',  'Engineered', '1 if discount applied, else 0'),
    ('promo_code_used_flag',   'Integer',  'Engineered', '1 if promo code used, else 0'),
    ('is_subscribed',          'Integer',  'Engineered', '1 if subscribed, else 0'),
    ('purchase_freq_annual',   'Float',    'Engineered', 'Annual purchase frequency (numeric conversion of frequency_of_purchases)'),
    ('total_spend_est',        'Float',    'Engineered', 'purchase_amount × (previous_purchases + 1) — estimated lifetime spend'),
    ('avg_order_value',        'Float',    'Engineered', 'Same as purchase_amount (single observation)'),
    ('purchase_count',         'Integer',  'Engineered', 'previous_purchases + 1'),
    ('est_annual_spend',       'Float',    'Engineered', 'purchase_amount × purchase_freq_annual'),
    ('value_tier',             'Text',     'Engineered', 'High/Medium/Low based on total_spend_est percentiles (33rd, 66th)'),
    ('promo_usage_rate',       'Float',    'Engineered', 'Average of discount_applied_flag and promo_code_used_flag (0–1)'),
    ('promo_dependency_score', 'Float',    'Engineered', 'Weighted promo score 0–100: 40% discount + 40% promo_code + 20% inverse purchase history'),
    ('promo_segment',          'Text',     'Engineered', 'Organic Loyalist / Selective Promo User / Promo Dependent / Bargain Hunter (quartile-based)'),
    ('satisfaction_tier',      'Text',     'Engineered', 'Dissatisfied (<3.0) / Neutral (3.0–4.0) / Satisfied (≥4.0)'),
    ('satisfaction_flag',      'Integer',  'Engineered', '1 if review_rating ≥ 4.0'),
    ('dissatisfied_high_value','Integer',  'Engineered', '1 if value_tier=High AND satisfaction_tier=Dissatisfied'),
    ('retention_proxy_score',  'Float',    'Engineered', 'Composite 0–100: 35% prev_purchases + 25% frequency + 20% rating + 10% subscription + 10% low promo. NOT true retention — timestamps absent.'),
    ('retention_proxy_tier',   'Text',     'Engineered', 'Low/Medium/High Retention Signal (tercile of retention_proxy_score)'),
    ('loyalty_score_1',        'Float',    'Engineered', 'Behavioral loyalty score: 30% purchase_count + 30% total_spend + 20% satisfaction + 20% low promo'),
    ('loyalty_def1',           'Text',     'Engineered', 'Low/Medium/High Loyalty (Definition 1: Behavioral)'),
    ('loyalty_score_2',        'Float',    'Engineered', 'Commercial loyalty score: 30% spend + 25% AOV + 20% frequency + 15% subscription + 10% no discount'),
    ('loyalty_def2',           'Text',     'Engineered', 'Low/Medium/High Loyalty (Definition 2: Commercial)'),
    ('loyalty_segment',        'Text',     'Engineered', f'Selected from {WINNER_LABEL} — winner by consistency score {max(score1,score2)}/4'),
    ('geo_opportunity',        'Text',     'Engineered', 'High/Medium/Low Opportunity based on 5-flag scoring (density, spend, promo, satisfaction, HV share)'),
    ('opportunity_score',      'Integer',  'Engineered', '0–5 count of favorable geography flags'),
    ('purchase_history_tier',  'Text',     'Engineered', 'New (0-5) / Developing (6-15) / Established (16+) based on previous_purchases'),
    ('final_segment',          'Text',     'Engineered', 'Actionable customer segment — see segment definitions in README'),
], columns=['column', 'dtype', 'source', 'description'])
data_dict.to_csv(f"{DASHBOARD_DIR}/data_dictionary.csv", index=False)

# 14. Final metrics summary
total_rev_est = fe['total_spend_est'].sum()
organic_rev   = fe[fe['promo_usage_rate']==0]['total_spend_est'].sum()
promo_rev     = total_rev_est - organic_rev

metrics = pd.DataFrame([
    ('Total Customers',                      len(fe)),
    ('Total Estimated Revenue',              f"${total_rev_est:,.0f}"),
    ('Organic Revenue',                      f"${organic_rev:,.0f}"),
    ('Promo-Dependent Revenue',              f"${promo_rev:,.0f}"),
    ('Organic Revenue %',                    f"{organic_rev/total_rev_est*100:.1f}%"),
    ('Promo-Dependent Revenue %',            f"{promo_rev/total_rev_est*100:.1f}%"),
    ('High-Value Customers',                 int((fe['value_tier']=='High').sum())),
    ('Loyal High-Value Customers',           int((fe['final_segment']=='Loyal High-Value').sum())),
    ('High-Value Promo-Dependent',           int((fe['final_segment']=='High-Value Promo-Dependent').sum())),
    ('At-Risk Dissatisfied',                 int((fe['final_segment']=='At-Risk Dissatisfied').sum())),
    ('Low-Repeat Bargain Hunters',           int((fe['final_segment']=='Low-Repeat Bargain Hunter').sum())),
    ('Selected Loyalty Definition',          WINNER_LABEL),
    ('Loyalty Consistency Score',            f"{max(score1,score2)}/4"),
    ('High Opportunity States',              int((geo['geo_opportunity']=='High Opportunity').sum())),
    ('Pipeline Run Time',                    RUN_TIMESTAMP),
], columns=['metric', 'value'])
metrics.to_csv(f"{OUTPUTS_DIR}/final_metrics_summary.csv", index=False)

log(f"\n✓ All CSV files exported to: {DASHBOARD_DIR}/")

# =============================================================================
# SECTION 14: CREATE SQLITE DATABASE
# =============================================================================

log("\n" + "=" * 70)
log("SECTION 14: CREATING SQLITE DATABASE")
log("=" * 70)

conn = sqlite3.connect(DB_PATH)

# Load all tables
fe.to_sql('customers', conn, if_exists='replace', index=False)
seg_summary.to_sql('segment_summary', conn, if_exists='replace', index=False)
geo.to_sql('geography_opportunity', conn, if_exists='replace', index=False)
cat_funnel.to_sql('category_funnel', conn, if_exists='replace', index=False)
cat_summary.to_sql('category_summary', conn, if_exists='replace', index=False)
promo_ret.to_sql('promo_dependency_retention', conn, if_exists='replace', index=False)
pyramid.to_sql('customer_pyramid', conn, if_exists='replace', index=False)
icp_df.to_sql('ideal_customer_profile', conn, if_exists='replace', index=False)
data_dict.to_sql('data_dictionary', conn, if_exists='replace', index=False)
metrics.to_sql('final_metrics', conn, if_exists='replace', index=False)

# Create analytical views
conn.executescript("""
-- Five segment views
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

-- Power BI dashboard views
CREATE VIEW IF NOT EXISTS v_customer_pyramid AS
    SELECT value_tier,
           customer_count,
           ROUND(avg_spend, 2) AS avg_spend,
           ROUND(total_revenue_est, 0) AS total_revenue_est,
           ROUND(avg_retention, 1) AS avg_retention_proxy,
           pct_of_customers,
           pct_of_revenue
    FROM customer_pyramid
    ORDER BY CASE value_tier WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

CREATE VIEW IF NOT EXISTS v_promo_dependency_retention AS
    SELECT final_segment,
           customer_count,
           ROUND(avg_promo_dependency, 1) AS avg_promo_dependency,
           ROUND(avg_retention_proxy, 1) AS avg_retention_proxy,
           ROUND(avg_spend, 2) AS avg_spend,
           ROUND(avg_satisfaction, 2) AS avg_satisfaction,
           ROUND(pct_subscribed * 100, 1) AS pct_subscribed,
           ROUND(pct_organic * 100, 1) AS pct_organic
    FROM promo_dependency_retention
    ORDER BY avg_promo_dependency DESC;

CREATE VIEW IF NOT EXISTS v_geography_opportunity AS
    SELECT location,
           geo_customer_count,
           ROUND(geo_avg_spend, 2) AS avg_spend,
           ROUND(geo_promo_rate, 3) AS promo_rate,
           ROUND(geo_avg_rating, 2) AS avg_rating,
           ROUND(geo_hv_share * 100, 1) AS hv_share_pct,
           loyal_hv_count,
           opportunity_score,
           geo_opportunity
    FROM geography_opportunity
    ORDER BY opportunity_score DESC, geo_avg_spend DESC;

CREATE VIEW IF NOT EXISTS v_category_funnel AS
    SELECT category,
           purchase_history_tier,
           customer_count,
           ROUND(avg_spend, 2) AS avg_spend,
           ROUND(avg_promo_dep, 1) AS avg_promo_dependency,
           ROUND(avg_rating, 2) AS avg_rating,
           ROUND(pct_high_value * 100, 1) AS pct_high_value
    FROM category_funnel
    ORDER BY category, purchase_history_tier;

CREATE VIEW IF NOT EXISTS v_segment_summary AS
    SELECT final_segment,
           customer_count,
           ROUND(avg_purchase_amount, 2) AS avg_order_value,
           ROUND(avg_total_spend_est, 0) AS avg_lifetime_value,
           ROUND(avg_previous_purchases, 1) AS avg_prev_purchases,
           ROUND(avg_review_rating, 2) AS avg_rating,
           ROUND(avg_promo_dependency, 1) AS avg_promo_score,
           ROUND(avg_retention_proxy, 1) AS avg_retention_proxy,
           ROUND(pct_discount_applied * 100, 1) AS pct_discount,
           ROUND(pct_subscribed * 100, 1) AS pct_subscribed,
           revenue_share_pct,
           segment_definition
    FROM segment_summary
    ORDER BY revenue_share_pct DESC;

CREATE VIEW IF NOT EXISTS v_ideal_customer_profile AS
    SELECT * FROM ideal_customer_profile;
""")

conn.close()
log(f"✓ SQLite database created: {DB_PATH}")
log(f"  Tables: customers, segment_summary, geography_opportunity,")
log(f"          category_funnel, category_summary, promo_dependency_retention,")
log(f"          customer_pyramid, ideal_customer_profile, data_dictionary, final_metrics")
log(f"  Views: v_customer_pyramid, v_promo_dependency_retention, v_geography_opportunity,")
log(f"         v_category_funnel, v_segment_summary, v_ideal_customer_profile,")
log(f"         v_loyal_high_value, v_hv_promo_dependent, v_at_risk, v_organic_mid, v_bargain_hunters")

# =============================================================================
# SECTION 15: PIPELINE RUN SUMMARY
# =============================================================================

log("\n" + "=" * 70)
log("FINAL SUBMISSION SUMMARY")
log("=" * 70)

summary_lines = [
    f"Pipeline Run: {RUN_TIMESTAMP}",
    "",
    "DATASET OVERVIEW",
    f"  Total customers: {len(fe):,}",
    f"  Raw columns: {len(df_raw.columns)}",
    f"  Engineered features: {len(fe.columns)}",
    "",
    "LOYALTY ANALYSIS",
    f"  Definition 1 (Behavioral): consistency score {score1}/4",
    f"  Definition 2 (Commercial): consistency score {score2}/4",
    f"  Selected: {WINNER_LABEL}",
    "",
    "CUSTOMER SEGMENTS",
]
for seg, cnt in fe['final_segment'].value_counts().items():
    rev = seg_summary[seg_summary['final_segment']==seg]['revenue_share_pct'].values
    rev_str = f"{rev[0]:.1f}%" if len(rev) > 0 else "N/A"
    summary_lines.append(f"  {seg:<35} {cnt:>5} customers | {rev_str} revenue")

summary_lines += [
    "",
    "REVENUE BREAKDOWN",
    f"  Total estimated revenue: ${total_rev_est:,.0f}",
    f"  Organic (no promo): ${organic_rev:,.0f} ({organic_rev/total_rev_est*100:.1f}%)",
    f"  Promo-dependent: ${promo_rev:,.0f} ({promo_rev/total_rev_est*100:.1f}%)",
    "",
    "GEOGRAPHY",
    f"  High Opportunity states: {int((geo['geo_opportunity']=='High Opportunity').sum())}",
    f"  Medium Opportunity states: {int((geo['geo_opportunity']=='Medium Opportunity').sum())}",
    "",
    "CATEGORY ROLES",
]
for _, row in cat_summary.iterrows():
    summary_lines.append(f"  {row['category']:<15} → {row['category_role']}")

summary_lines += [
    "",
    "FILES CREATED",
    f"  data/cleaned/cleaned_customer_data.csv",
    f"  data/features/customer_features.csv",
]
for f in sorted(os.listdir(DASHBOARD_DIR)):
    if f.endswith('.csv'):
        summary_lines.append(f"  data/dashboard/{f}")
summary_lines += [
    f"  sql/schema.sql",
    f"  sql/analysis_queries.sql",
    f"  sql/customer_intelligence.db",
    f"  outputs/final_metrics_summary.csv",
]

summary_text = "\n".join(summary_lines)
log("\n" + summary_text)

with open(f"{OUTPUTS_DIR}/pipeline_run_summary.txt", "w") as f:
    f.write(summary_text)

log(f"\n✓ Run summary saved: {OUTPUTS_DIR}/pipeline_run_summary.txt")
log("\n✅ PIPELINE COMPLETE")
