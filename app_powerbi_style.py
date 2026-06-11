"""
app.py — Customer Intelligence Dashboard
Matches: customer_value_dashboard.pdf (Power BI white-theme layout)
Run: streamlit run app.py
Requires: pip install streamlit pandas plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Customer Value Intelligence: D2C Fashion Brand",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Force white/light theme matching customer_value_dashboard.pdf ──────────
st.markdown("""
<style>
/* Page background white */
.stApp { background-color: #ffffff; }
[data-testid="stAppViewContainer"] { background-color: #ffffff; }
[data-testid="stMain"] { background-color: #ffffff; }
[data-testid="block-container"] { background-color: #ffffff; padding-top: 1rem; }

/* Remove default dark tones */
section[data-testid="stSidebar"] { background-color: #f7fafc; }

/* KPI metric cards */
[data-testid="metric-container"] {
    background-color: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 10px 14px;
}
[data-testid="stMetricLabel"] { font-size: 11px !important; color: #718096 !important; }
[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; color: #1a2e4a !important; }

/* Panel card style */
div[data-testid="stVerticalBlock"] > div {
    background: transparent;
}

/* Slicer selectbox */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e0 !important;
    border-radius: 4px !important;
    font-size: 13px !important;
    color: #2d3748 !important;
}

/* Panel header text */
h3 { color: #1a2e4a !important; font-size: 14px !important; font-weight: 700 !important; }
.panel-subtitle { font-size: 11px; color: #718096; margin-top: -10px; margin-bottom: 6px; }

/* Chart container border */
.chart-card {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    background: #ffffff;
    margin-bottom: 8px;
}

/* Title bar */
.title-bar {
    background: #1a2e4a;
    color: white;
    padding: 14px 20px 10px 20px;
    border-radius: 6px;
    margin-bottom: 14px;
}
.title-bar h1 {
    color: white !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    margin: 0 !important;
}
.title-bar p {
    color: #a0aec0 !important;
    font-size: 11px !important;
    margin: 3px 0 0 0 !important;
}

/* Divider */
hr { border-top: 1px solid #e2e8f0 !important; margin: 8px 0 !important; }

/* Slicer label */
.slicer-label { font-size: 11px; color: #718096; font-weight: 600; margin-bottom: 2px; }

/* Table styling */
[data-testid="stDataFrame"] table {
    font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data loading ───────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = "data/dashboard"
    return {
        "pyramid"   : pd.read_csv(f"{base}/customer_pyramid.csv"),
        "promo_ret" : pd.read_csv(f"{base}/promo_dependency_retention.csv"),
        "geo"       : pd.read_csv(f"{base}/geography_opportunity.csv"),
        "cat_funnel": pd.read_csv(f"{base}/category_funnel.csv"),
        "cat_sum"   : pd.read_csv(f"{base}/category_summary.csv"),
        "seg_sum"   : pd.read_csv(f"{base}/segment_summary.csv"),
        "icp"       : pd.read_csv(f"{base}/ideal_customer_profile.csv"),
        "metrics"   : pd.read_csv("outputs/final_metrics_summary.csv"),
        "features"  : pd.read_csv("data/features/customer_features.csv"),
    }

try:
    data = load_data()
except FileNotFoundError:
    st.error("⚠️ Data files not found. Run `python main_pipeline.py` first.")
    st.stop()

def get_metric(df, key):
    row = df[df['metric'] == key]
    return row['value'].values[0] if len(row) > 0 else "N/A"

metrics  = data["metrics"]
features = data["features"]

# ── Colour constants (matching customer_value_dashboard.pdf) ───────────────
WHITE        = "#ffffff"
LIGHT_BG     = "#f7fafc"
BORDER       = "#e2e8f0"
NAVY         = "#1a2e4a"
BLUE         = "#2c5282"
DGRAY        = "#718096"
BLACK        = "#2d3748"

# Segment colours — exact match to Power BI dashboard
SEG_COLOR_MAP = {
    "Champion"           : "#6c63e0",   # purple
    "High-Value-At-Risk" : "#e06c63",   # red/coral
    "Loyal-Mid-Value"    : "#27ae60",   # green
    "Promo-Hunter"       : "#e0a363",   # orange/gold
    "Standard"           : "#8c8c8c",   # gray
}

# Map segment names from pipeline → Power BI template names
SEG_RENAME = {
    "Loyal High-Value"           : "Champion",
    "At-Risk Dissatisfied"       : "High-Value-At-Risk",
    "Organic Mid-Value"          : "Loyal-Mid-Value",
    "High-Value Promo-Dependent" : "Promo-Hunter",
    "Low-Value Low-Engagement"   : "Standard",
    "Low-Repeat Bargain Hunter"  : "Standard",   # merged into Standard for pyramid
}

# ── Title bar ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-bar">
  <h1>Customer Value Intelligence: D2C Fashion Brand</h1>
  <p>Decoding Customer Value: A SQL-Driven Retention Strategy &nbsp;|&nbsp; Summer Projects '26 &nbsp;|&nbsp; IIT Guwahati</p>
</div>
""", unsafe_allow_html=True)

# ── Slicer row (Season / Gender — matches template top filters) ────────────
slicer_col1, slicer_col2, slicer_spacer = st.columns([1.2, 1.2, 8])

seasons  = ["All"] + sorted(features["season"].dropna().unique().tolist())
genders  = ["All"] + sorted(features["gender"].dropna().unique().tolist())

with slicer_col1:
    st.markdown('<div class="slicer-label">Season</div>', unsafe_allow_html=True)
    sel_season = st.selectbox("", seasons, key="season", label_visibility="collapsed")

with slicer_col2:
    st.markdown('<div class="slicer-label">Gender</div>', unsafe_allow_html=True)
    sel_gender = st.selectbox("", genders, key="gender", label_visibility="collapsed")

# Apply slicer filters to feature data
filtered = features.copy()
if sel_season != "All":
    filtered = filtered[filtered["season"] == sel_season]
if sel_gender != "All":
    filtered = filtered[filtered["gender"] == sel_gender]

# ── KPI Row (6 cards — matching dashboard.pdf KPI strip) ──────────────────
st.markdown("<hr>", unsafe_allow_html=True)
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Customers",      f"{len(filtered):,}")
k2.metric("Est. Revenue",         f"${filtered['total_spend_est'].sum():,.0f}")
k3.metric("Organic Revenue",      f"{(filtered[filtered['promo_usage_rate']==0]['total_spend_est'].sum() / filtered['total_spend_est'].sum() * 100):.1f}%")
k4.metric("Promo-Dependent Rev",  f"{(filtered[filtered['promo_usage_rate']>0]['total_spend_est'].sum() / filtered['total_spend_est'].sum() * 100):.1f}%")
k5.metric("Loyal High-Value",     f"{(filtered['final_segment']=='Loyal High-Value').sum():,}")
k6.metric("At-Risk Dissatisfied", f"{(filtered['final_segment']=='At-Risk Dissatisfied').sum():,}")
st.markdown("<hr>", unsafe_allow_html=True)

# ── Build segment-level data from filtered features ────────────────────────
def build_segment_counts(df):
    """Map pipeline segments → Power BI template names and aggregate."""
    df2 = df.copy()
    df2["pbi_segment"] = df2["final_segment"].map(SEG_RENAME).fillna("Standard")
    counts = df2.groupby("pbi_segment").agg(
        count=("customer_id", "count"),
        avg_promo=("promo_dependency_score", "mean"),
        avg_retention=("retention_proxy_score", "mean"),
        avg_spend=("purchase_amount", "mean"),
    ).reset_index()
    # Order matching template: Standard, Promo-Hunter, Loyal-Mid-Value,
    #                          High-Value-At-Risk, Champion
    order = ["Standard", "Promo-Hunter", "Loyal-Mid-Value", "High-Value-At-Risk", "Champion"]
    counts["pbi_segment"] = pd.Categorical(counts["pbi_segment"], categories=order, ordered=True)
    counts = counts.sort_values("count", ascending=False)
    return counts

seg_df = build_segment_counts(filtered)

# ── PANEL LAYOUT: 2 columns ────────────────────────────────────────────────
col_l, col_r = st.columns(2, gap="medium")

# ════════════════════════════════════════════════════════════════════════════
# PANEL 1 — Customer Pyramid: Value Distribution
# Matches template: horizontal bar chart, segments on Y-axis, count on X-axis
# ════════════════════════════════════════════════════════════════════════════
with col_l:
    st.markdown("**Customer Pyramid - Value Distribution**")
    st.markdown('<div class="panel-subtitle">How is customer value distributed across the base?</div>',
                unsafe_allow_html=True)

    seg_for_pyramid = seg_df.sort_values("count", ascending=True)  # ascending = top bar = largest

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=seg_for_pyramid["count"],
        y=seg_for_pyramid["pbi_segment"],
        orientation="h",
        marker=dict(
            color=[SEG_COLOR_MAP.get(s, "#8c8c8c") for s in seg_for_pyramid["pbi_segment"]],
            line=dict(width=0),
        ),
        text=seg_for_pyramid["count"],
        textposition="outside",
        textfont=dict(size=11, color=BLACK),
        hovertemplate="<b>%{y}</b><br>Count: %{x:,}<extra></extra>",
    ))

    fig1.update_layout(
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        height=300,
        margin=dict(l=0, r=40, t=10, b=30),
        xaxis=dict(
            title="Count of Customer ID",
            title_font=dict(size=11, color=DGRAY),
            tickfont=dict(size=10, color=DGRAY),
            showgrid=True,
            gridcolor=BORDER,
            gridwidth=0.5,
            zeroline=False,
            range=[0, seg_for_pyramid["count"].max() * 1.18],
        ),
        yaxis=dict(
            title="customer_segment",
            title_font=dict(size=11, color=DGRAY),
            tickfont=dict(size=11, color=BLACK),
            showgrid=False,
        ),
        showlegend=False,
    )
    st.plotly_chart(fig1, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# PANEL 2 — Promo Dependency by Segment
# Matches template: vertical bar chart, promo_dep score on Y, segments on X
# ════════════════════════════════════════════════════════════════════════════
with col_r:
    st.markdown("**Promo Dependency by Segment**")
    st.markdown('<div class="panel-subtitle">Average promo dependency score per segment</div>',
                unsafe_allow_html=True)

    # Order matching template: Promo-Hunter, Champion, Loyal-Mid-Value, High-Value-At-Risk, Standard
    promo_order = ["Promo-Hunter", "Champion", "Loyal-Mid-Value", "High-Value-At-Risk", "Standard"]
    seg_promo = seg_df.copy()
    seg_promo["pbi_segment"] = pd.Categorical(seg_promo["pbi_segment"],
                                               categories=promo_order, ordered=True)
    seg_promo = seg_promo.sort_values("pbi_segment")

    # Normalize promo score to 0–1 scale matching template y-axis (0.0–1.0)
    seg_promo["avg_promo_norm"] = seg_promo["avg_promo"] / 100

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=seg_promo["pbi_segment"],
        y=seg_promo["avg_promo_norm"],
        marker=dict(
            color=[SEG_COLOR_MAP.get(s, "#8c8c8c") for s in seg_promo["pbi_segment"]],
            line=dict(width=0),
        ),
        text=seg_promo["avg_promo_norm"].apply(lambda v: f"{v:.2f}"),
        textposition="outside",
        textfont=dict(size=11, color=BLACK),
        hovertemplate="<b>%{x}</b><br>Promo Dep: %{y:.2f}<extra></extra>",
    ))

    fig2.update_layout(
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        height=300,
        margin=dict(l=0, r=10, t=20, b=10),
        xaxis=dict(
            title="customer_segment",
            title_font=dict(size=11, color=DGRAY),
            tickfont=dict(size=10, color=BLACK),
            tickangle=-25,
            showgrid=False,
        ),
        yaxis=dict(
            title="Average of promo_dep...",
            title_font=dict(size=11, color=DGRAY),
            tickfont=dict(size=10, color=DGRAY),
            showgrid=True,
            gridcolor=BORDER,
            gridwidth=0.5,
            zeroline=True,
            zerolinecolor=BORDER,
            range=[0, 1.15],
            tickvals=[0.0, 0.5, 1.0],
            ticktext=["0.0", "0.5", "1.0"],
        ),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Bottom row ─────────────────────────────────────────────────────────────
col_bl, col_br = st.columns(2, gap="medium")

# ════════════════════════════════════════════════════════════════════════════
# PANEL 3 — Geographic Opportunity: Spend vs Promo Dependency
# Matches template: Choropleth map + Market Type legend
# (High Opportunity / Low Priority / Organic Low Spend / Promo Dependent)
# ════════════════════════════════════════════════════════════════════════════
with col_bl:
    st.markdown("**Geographic Opportunity: Spend vs Promo Dependency**")
    st.markdown('<div class="panel-subtitle">Which markets show genuine brand pull vs. discount-driven demand?</div>',
                unsafe_allow_html=True)

    geo = data["geo"].copy()

    # Build Market Type matching Power BI legend categories:
    # High Opportunity  → opportunity_score >= 4 + low promo
    # Organic Low Spend → low promo but low customer count/spend
    # Promo Dependent   → high promo, medium/low opportunity
    # Low Priority      → everything else (low score)
    def market_type(row):
        if row["opportunity_score"] >= 4:
            return "High Opportunity"
        elif row["geo_promo_rate"] < 0.42 and row["opportunity_score"] >= 2:
            return "Organic Low Spend"
        elif row["geo_promo_rate"] >= 0.45:
            return "Promo Dependent"
        else:
            return "Low Priority"

    geo["market_type"] = geo.apply(market_type, axis=1)

    # Apply slicer filter to geo if we have filtered data
    if sel_season != "All" or sel_gender != "All":
        geo_filtered = filtered.groupby("location").agg(
            geo_customer_count=("customer_id", "count"),
            geo_avg_spend=("purchase_amount", "mean"),
            geo_promo_rate=("promo_usage_rate", "mean"),
            opportunity_score=("opportunity_score", "first"),
        ).reset_index()
        geo_filtered["market_type"] = geo_filtered.apply(market_type, axis=1)
        geo_plot = geo_filtered
    else:
        geo_plot = geo

    MARKET_COLORS = {
        "High Opportunity"  : "#27ae60",
        "Organic Low Spend" : "#3498db",
        "Promo Dependent"   : "#e74c3c",
        "Low Priority"      : "#95a5a6",
    }

    fig3 = px.choropleth(
        geo_plot,
        locations="location",
        locationmode="USA-states",
        color="market_type",
        color_discrete_map=MARKET_COLORS,
        scope="usa",
        hover_name="location",
        hover_data={
            "geo_customer_count": True,
            "geo_avg_spend"     : ":.2f",
            "geo_promo_rate"    : ":.3f",
            "opportunity_score" : True,
            "market_type"       : True,
        },
        labels={
            "market_type"        : "Market Type",
            "geo_customer_count" : "Customers",
            "geo_avg_spend"      : "Avg Spend ($)",
            "geo_promo_rate"     : "Promo Rate",
            "opportunity_score"  : "Score",
        },
        category_orders={"market_type": ["High Opportunity", "Low Priority",
                                          "Organic Low Spend", "Promo Dependent"]},
    )
    fig3.update_layout(
        height=320,
        paper_bgcolor=WHITE,
        geo=dict(bgcolor=WHITE, lakecolor=WHITE, landcolor="#f0f0f0",
                 showlakes=True, showland=True, showframe=False,
                 coastlinecolor="#cccccc"),
        legend=dict(
            title="Market Type",
            title_font=dict(size=11, color=BLACK),
            font=dict(size=10, color=BLACK),
            orientation="h",
            x=0, y=-0.08,
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=0, r=0, t=0, b=40),
    )
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("Top 10 High-Opportunity States"):
        top10 = geo.sort_values("opportunity_score", ascending=False).head(10)
        st.dataframe(
            top10[["location", "geo_customer_count", "geo_avg_spend",
                   "geo_promo_rate", "opportunity_score", "market_type"]].rename(columns={
                "location"          : "State",
                "geo_customer_count": "Customers",
                "geo_avg_spend"     : "Avg Spend",
                "geo_promo_rate"    : "Promo Rate",
                "opportunity_score" : "Score",
                "market_type"       : "Market Type",
            }),
            hide_index=True, use_container_width=True,
        )

# ════════════════════════════════════════════════════════════════════════════
# PANEL 4 — Category Funnel: Entry Point vs Retention
# Matches template: horizontal bar chart, two bars per category
# (Entry-Point = avg prev purchases for new customers,
#  Retention   = avg prev purchases for established customers)
# X-axis = Average of Previous Purchases (0–40 range)
# ════════════════════════════════════════════════════════════════════════════
with col_br:
    st.markdown("**Category Funnel: Entry Point vs Retention**")
    st.markdown('<div class="panel-subtitle">Which categories attract new buyers vs. retain established ones?</div>',
                unsafe_allow_html=True)

    cf = data["cat_funnel"].copy()

    # Apply slicer filter
    if sel_season != "All" or sel_gender != "All":
        cf_src = filtered.copy()
        cf_src["purchase_history_tier"] = pd.cut(
            cf_src["previous_purchases"],
            bins=[-1, 5, 15, 200],
            labels=["New (0-5)", "Developing (6-15)", "Established (16+)"]
        )
        cf = cf_src.groupby(["category", "purchase_history_tier"], observed=True).agg(
            customer_count   =("customer_id", "count"),
            avg_spend        =("purchase_amount", "mean"),
            avg_promo_dep    =("promo_dependency_score", "mean"),
            avg_rating       =("review_rating", "mean"),
            avg_prev_purchases=("previous_purchases", "mean"),
        ).reset_index()
    else:
        # Compute avg previous purchases per category × tier from features
        cf_full = features.copy()
        cf_full["purchase_history_tier"] = pd.cut(
            cf_full["previous_purchases"],
            bins=[-1, 5, 15, 200],
            labels=["New (0-5)", "Developing (6-15)", "Established (16+)"]
        )
        cf_avg = cf_full.groupby(["category", "purchase_history_tier"], observed=True).agg(
            avg_prev_purchases=("previous_purchases", "mean"),
            customer_count=("customer_id", "count"),
        ).reset_index()
        cf = cf_avg

    # Build Entry-Point (New 0-5) and Retention (Established 16+) avg prev purchases per category
    entry_df = cf[cf["purchase_history_tier"] == "New (0-5)"].rename(
        columns={"avg_prev_purchases": "entry_avg"})
    reten_df = cf[cf["purchase_history_tier"] == "Established (16+)"].rename(
        columns={"avg_prev_purchases": "retention_avg"})

    merged = entry_df[["category", "entry_avg"]].merge(
        reten_df[["category", "retention_avg"]], on="category", how="outer"
    ).fillna(0)

    # Template shows: Accessories 12.96 / 38.21, Footwear 13.26/37.40,
    #                 Clothing 13.09/37.74, Outerwear 11.82/38.76
    # Match exact order from template (Accessories, Footwear, Clothing, Outerwear)
    cat_order = ["Accessories", "Footwear", "Clothing", "Outerwear"]
    merged["category"] = pd.Categorical(merged["category"], categories=cat_order, ordered=True)
    merged = merged.sort_values("category")

    fig4 = go.Figure()

    # Entry-Point bar (red/orange in template)
    fig4.add_trace(go.Bar(
        y=merged["category"],
        x=merged["entry_avg"],
        orientation="h",
        name="Entry-Point Category",
        marker=dict(color="#e06c63", line=dict(width=0)),
        text=merged["entry_avg"].apply(lambda v: f"{v:.2f}"),
        textposition="outside",
        textfont=dict(size=10, color=BLACK),
        hovertemplate="<b>%{y}</b><br>Entry Avg Purchases: %{x:.2f}<extra></extra>",
    ))

    # Retention bar (purple/blue in template)
    fig4.add_trace(go.Bar(
        y=merged["category"],
        x=merged["retention_avg"],
        orientation="h",
        name="Retention Category",
        marker=dict(color="#6c63e0", line=dict(width=0)),
        text=merged["retention_avg"].apply(lambda v: f"{v:.2f}"),
        textposition="outside",
        textfont=dict(size=10, color=BLACK),
        hovertemplate="<b>%{y}</b><br>Retention Avg Purchases: %{x:.2f}<extra></extra>",
    ))

    fig4.update_layout(
        barmode="overlay",
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        height=300,
        margin=dict(l=0, r=50, t=10, b=30),
        xaxis=dict(
            title="Average of Previous Purchases",
            title_font=dict(size=11, color=DGRAY),
            tickfont=dict(size=10, color=DGRAY),
            showgrid=True,
            gridcolor=BORDER,
            gridwidth=0.5,
            zeroline=False,
            range=[0, 44],
            tickvals=[0, 10, 20, 30, 40],
        ),
        yaxis=dict(
            title="Category",
            title_font=dict(size=11, color=DGRAY),
            tickfont=dict(size=11, color=BLACK),
            showgrid=False,
        ),
        legend=dict(
            title="Category Role",
            title_font=dict(size=10, color=BLACK),
            font=dict(size=10, color=BLACK),
            orientation="h",
            x=0, y=1.12,
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Category role table (compact — matches template bottom-right inset)
    cs = data["cat_sum"].copy()
    cs_display = cs[["category", "category_role"]].copy()
    cs_display.columns = ["Category", "Category Role"]
    st.dataframe(cs_display, hide_index=True, use_container_width=True)

# ── Full Segment Summary Table ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
with st.expander("Full Segment Summary Table", expanded=False):
    ss = data["seg_sum"].copy()
    # Apply slicer
    if sel_season != "All" or sel_gender != "All":
        ss = filtered.groupby("final_segment", observed=True).agg(
            customer_count         =("customer_id", "count"),
            revenue_share_pct      =("total_spend_est", "sum"),
            avg_purchase_amount    =("purchase_amount", "mean"),
            avg_total_spend_est    =("total_spend_est", "mean"),
            avg_promo_dependency   =("promo_dependency_score", "mean"),
            avg_retention_proxy    =("retention_proxy_score", "mean"),
            avg_review_rating      =("review_rating", "mean"),
            pct_discount_applied   =("discount_applied_flag", "mean"),
        ).reset_index()
        total_rev = ss["revenue_share_pct"].sum()
        ss["revenue_share_pct"] = (ss["revenue_share_pct"] / total_rev * 100).round(1)

    st.dataframe(
        ss[["final_segment", "customer_count", "revenue_share_pct",
            "avg_purchase_amount", "avg_total_spend_est",
            "avg_promo_dependency", "avg_retention_proxy",
            "avg_review_rating"]].rename(columns={
            "final_segment"       : "Segment",
            "customer_count"      : "Customers",
            "revenue_share_pct"   : "Revenue %",
            "avg_purchase_amount" : "Avg Order Value",
            "avg_total_spend_est" : "Avg LTV Est",
            "avg_promo_dependency": "Promo Score",
            "avg_retention_proxy" : "Retention Signal",
            "avg_review_rating"   : "Avg Rating",
        }).round(2),
        hide_index=True, use_container_width=True,
    )

with st.expander("Ideal Customer Profile", expanded=False):
    icp = data["icp"]
    st.dataframe(
        icp[["Attribute", "Value", "Business_Implication"]].rename(
            columns={"Business_Implication": "Business Implication"}
        ),
        hide_index=True, use_container_width=True,
    )

st.markdown(
    '<div style="color:#a0aec0;font-size:10px;margin-top:8px;">'
    'Dashboard powered by data/dashboard/*.csv &nbsp;|&nbsp; '
    'Run <code>python main_pipeline.py</code> to refresh'
    '</div>',
    unsafe_allow_html=True
)
