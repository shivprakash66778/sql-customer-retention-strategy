"""
app.py — Interactive Customer Intelligence Dashboard
Run: streamlit run app.py
Requires: pip install streamlit pandas plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Customer Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    }

try:
    data = load_data()
except FileNotFoundError:
    st.error("Data files not found. Run `python main_pipeline.py` first.")
    st.stop()

# ── KPI helper ─────────────────────────────────────────────────────────────
def get_metric(df, key):
    row = df[df['metric'] == key]
    return row['value'].values[0] if len(row) > 0 else "N/A"

metrics = data["metrics"]

# ── Header ─────────────────────────────────────────────────────────────────
st.title("Customer Intelligence Dashboard")
st.caption("Decoding Customer Value: A SQL-Driven Retention Strategy | Summer Projects '26")

# ── KPI Row ────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Customers",           get_metric(metrics, "Total Customers"))
c2.metric("Est. Revenue",              get_metric(metrics, "Total Estimated Revenue"))
c3.metric("Organic Revenue",           get_metric(metrics, "Organic Revenue %"))
c4.metric("Promo-Dependent Rev",       get_metric(metrics, "Promo-Dependent Revenue %"))
c5.metric("Loyal High-Value",          get_metric(metrics, "Loyal High-Value Customers"))
c6.metric("At-Risk Dissatisfied",      get_metric(metrics, "At-Risk Dissatisfied"))

st.markdown("---")

# ── Four panels ────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

# ─────────────────────────────────────────────────────────────────────
# PANEL 1: Customer Value Pyramid
# ─────────────────────────────────────────────────────────────────────
with col_left:
    st.subheader("Panel 1: Customer Value Pyramid")
    st.caption("How is customer value distributed across the base?")

    pyr = data["pyramid"].copy()
    tier_order = ["High", "Medium", "Low"]
    pyr = pyr.set_index("value_tier").reindex(tier_order).reset_index()

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        name="% of Customers",
        x=pyr["value_tier"],
        y=pyr["pct_of_customers"],
        marker_color=["#1a2e4a", "#4472C4", "#D9D9D9"],
        text=pyr["pct_of_customers"].apply(lambda x: f"{x:.1f}%"),
        textposition="auto",
    ))
    fig1.add_trace(go.Bar(
        name="% of Revenue",
        x=pyr["value_tier"],
        y=pyr["pct_of_revenue"],
        marker_color=["#27AE60", "#52BE80", "#A9DFBF"],
        text=pyr["pct_of_revenue"].apply(lambda x: f"{x:.1f}%"),
        textposition="auto",
    ))
    fig1.update_layout(
        barmode="group",
        xaxis_title="Value Tier",
        yaxis_title="Percentage (%)",
        legend=dict(orientation="h", y=1.1),
        height=350,
        plot_bgcolor="#F8F9FA",
    )
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("Data table"):
        st.dataframe(pyr[["value_tier","customer_count","pct_of_customers","pct_of_revenue",
                           "avg_spend","avg_retention"]].rename(columns={
            "value_tier":"Tier","customer_count":"Customers","pct_of_customers":"% Customers",
            "pct_of_revenue":"% Revenue","avg_spend":"Avg Spend","avg_retention":"Retention Signal"}),
            hide_index=True)

# ─────────────────────────────────────────────────────────────────────
# PANEL 2: Promo Dependency vs Retention Proxy
# ─────────────────────────────────────────────────────────────────────
with col_right:
    st.subheader("🎯 Panel 2: Promo Dependency vs. Retention Signal")
    st.caption("Top-left = organic loyalists | Bottom-right = deal hunters")

    pr = data["promo_ret"].copy()

    COLORS = {
        "Loyal High-Value"           : "#1a2e4a",
        "High-Value Promo-Dependent" : "#E67E22",
        "Organic Mid-Value"          : "#27AE60",
        "At-Risk Dissatisfied"       : "#E74C3C",
        "Low-Repeat Bargain Hunter"  : "#7F8C8D",
        "Low-Value Low-Engagement"   : "#BDC3C7",
    }

    fig2 = go.Figure()
    for _, row in pr.iterrows():
        seg = row["final_segment"]
        fig2.add_trace(go.Scatter(
            x=[row["avg_promo_dependency"]],
            y=[row["avg_retention_proxy"]],
            mode="markers+text",
            name=seg,
            text=[seg.replace(" ", "<br>")],
            textposition="top center",
            marker=dict(
                size=max(10, row["customer_count"] / 30),
                color=COLORS.get(seg, "#999"),
                opacity=0.85,
                line=dict(width=1, color="white"),
            ),
        ))

    # Reference lines
    fig2.add_vline(x=50, line_dash="dash", line_color="gray", annotation_text="Promo threshold")
    fig2.add_hline(y=50, line_dash="dash", line_color="gray", annotation_text="Retention threshold")

    fig2.update_layout(
        xaxis=dict(title="Promo Dependency Score (0–100)", range=[0, 100]),
        yaxis=dict(title="Retention Proxy Score (0–100)", range=[0, 100]),
        height=380,
        showlegend=False,
        plot_bgcolor="#F8F9FA",
    )

    # Quadrant annotations
    fig2.add_annotation(x=15, y=90, text="Brand Loyalists<br>Protect ✓", showarrow=False,
                        font=dict(color="#27AE60", size=10))
    fig2.add_annotation(x=80, y=90, text="Promo-Dependent<br>Wean Off ", showarrow=False,
                        font=dict(color="#E67E22", size=10))
    fig2.add_annotation(x=15, y=10, text="Developing<br>Nurture →", showarrow=False,
                        font=dict(color="#3498DB", size=10))
    fig2.add_annotation(x=80, y=10, text="Deal Hunters<br>Deprioritize ✗", showarrow=False,
                        font=dict(color="#7F8C8D", size=10))

    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Note: Retention proxy is a composite engagement score, NOT true churn prediction (no timestamps in dataset)")

col_left2, col_right2 = st.columns(2)

# ─────────────────────────────────────────────────────────────────────
# PANEL 3: Geographic Opportunity
# ─────────────────────────────────────────────────────────────────────
with col_left2:
    st.subheader("Panel 3: Geographic Opportunity")
    st.caption("States with high spend, low promo dependency, and satisfied customers")

    geo = data["geo"].copy()

    # Chloropleth map
    opp_map = {"High Opportunity": 3, "Medium Opportunity": 2, "Low Opportunity": 1}
    geo["opp_num"] = geo["geo_opportunity"].map(opp_map)

    fig3 = px.choropleth(
        geo,
        locations="location",
        locationmode="USA-states",
        color="opportunity_score",
        color_continuous_scale=["#D5E8D4", "#82B366", "#1a6b3c"],
        scope="usa",
        hover_name="location",
        hover_data={
            "geo_customer_count": True,
            "geo_avg_spend": ":.2f",
            "geo_promo_rate": ":.3f",
            "opportunity_score": True,
            "geo_opportunity": True,
        },
        labels={
            "geo_customer_count": "Customers",
            "geo_avg_spend": "Avg Spend ($)",
            "geo_promo_rate": "Promo Rate",
            "opportunity_score": "Opportunity Score",
        },
    )
    fig3.update_layout(
        height=340,
        coloraxis_colorbar=dict(title="Score"),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("Top 10 High-Opportunity States"):
        top10 = geo.sort_values("opportunity_score", ascending=False).head(10)
        st.dataframe(top10[["location","geo_customer_count","geo_avg_spend",
                              "geo_promo_rate","opportunity_score","geo_opportunity"]].rename(columns={
            "location":"State","geo_customer_count":"Customers","geo_avg_spend":"Avg Spend",
            "geo_promo_rate":"Promo Rate","opportunity_score":"Score","geo_opportunity":"Level"}),
            hide_index=True)

# ─────────────────────────────────────────────────────────────────────
# PANEL 4: Category Funnel
# ─────────────────────────────────────────────────────────────────────
with col_right2:
    st.subheader("Panel 4: Category Funnel")
    st.caption("Which categories attract new buyers vs. retain established ones?")

    cf = data["cat_funnel"].copy()
    tier_colors = {
        "New (0-5)": "#AED6F1",
        "Developing (6-15)": "#4472C4",
        "Established (16+)": "#1a2e4a",
    }

    fig4 = px.bar(
        cf,
        x="category",
        y="customer_count",
        color="purchase_history_tier",
        barmode="group",
        color_discrete_map=tier_colors,
        labels={"category": "Category", "customer_count": "Customers",
                "purchase_history_tier": "Purchase History"},
        hover_data=["avg_spend", "avg_promo_dep", "avg_rating"],
    )
    fig4.update_layout(
        height=340,
        legend=dict(orientation="h", y=1.1, title="Purchase History"),
        plot_bgcolor="#F8F9FA",
        xaxis_title="Product Category",
        yaxis_title="Number of Customers",
    )
    st.plotly_chart(fig4, use_container_width=True)

    cs = data["cat_sum"]
    role_colors = {
        "Premium Growth Category": "🥇",
        "Retention Category": "🔄",
        "Entry Category": "🚪",
        "Discount-Led Category": "🏷️",
        "Neutral Category": "➡️",
    }
    cs["Role"] = cs["category_role"].apply(lambda x: f"{role_colors.get(x, '')} {x}")
    st.dataframe(
        cs[["category","avg_prev_purchases","avg_promo_dependency","avg_rating","Role"]].rename(columns={
            "category":"Category","avg_prev_purchases":"Avg Purchases",
            "avg_promo_dependency":"Promo Dep","avg_rating":"Avg Rating","Role":"Category Role"}),
        hide_index=True,
    )

# ── Segment detail expander ────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Full Segment Summary Table"):
    ss = data["seg_sum"].copy()
    st.dataframe(ss[[
        "final_segment","customer_count","revenue_share_pct","avg_purchase_amount",
        "avg_total_spend_est","avg_promo_dependency","avg_retention_proxy",
        "avg_review_rating","pct_discount_applied"
    ]].rename(columns={
        "final_segment":"Segment","customer_count":"Customers","revenue_share_pct":"Revenue %",
        "avg_purchase_amount":"Avg Order Value","avg_total_spend_est":"Avg LTV Est",
        "avg_promo_dependency":"Promo Score","avg_retention_proxy":"Retention Signal",
        "avg_review_rating":"Avg Rating","pct_discount_applied":"% Discount"
    }), hide_index=True)

with st.expander("👤 Ideal Customer Profile"):
    icp = data["icp"]
    # ---------------- Ideal Customer Profile ----------------
    st.subheader("👤 Ideal Customer Profile")
    
    # Standardize column names to avoid Streamlit Cloud KeyError
    icp.columns = (
        icp.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    
    # Rename expected columns if present
    rename_map = {
        "attribute": "Attribute",
        "value": "Value",
        "business_implication": "Business Implication",
        "business_implications": "Business Implication",
        "implication": "Business Implication"
    }
    
    icp_display = icp.rename(columns=rename_map)
    
    required_cols = ["Attribute", "Value", "Business Implication"]
    
    available_cols = [col for col in required_cols if col in icp_display.columns]
    
    if len(available_cols) == 3:
        st.dataframe(icp_display[required_cols], use_container_width=True)
    else:
        st.warning("Ideal Customer Profile table columns are different from expected. Showing available data instead.")
        st.write("Available columns:", list(icp_display.columns))
        st.dataframe(icp_display, use_container_width=True)

st.caption("Dashboard powered by data/dashboard/*.csv | Run python main_pipeline.py to refresh")
