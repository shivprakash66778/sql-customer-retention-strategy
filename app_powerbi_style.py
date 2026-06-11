"""
app.py — Power BI-style Founder Dashboard
Run: streamlit run app.py
Requires: pip install streamlit pandas plotly

This version is optimized for clean PDF export/screenshots. It uses a light,
Power BI-like one-page layout with slicers, four dashboard panels and summary
KPIs. It reads the existing final project CSVs from data/dashboard/ and outputs/.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# Page config and visual style
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Value Intelligence: D2C Fashion Brand",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        /* Force a clean Power BI-like light canvas even if Streamlit theme is dark */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background: #ffffff !important;
            color: #222222 !important;
        }
        [data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; height: 0%; }
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 0.5rem !important;
            max-width: 1240px !important;
        }
        h1 {
            text-align: center;
            color: #222222 !important;
            font-size: 30px !important;
            font-weight: 750 !important;
            margin-bottom: 0.25rem !important;
        }
        h2, h3, p, label, span, div { color: #222222; }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 0.55rem 0.7rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        [data-testid="stMetricLabel"] p {
            font-size: 12px !important;
            color: #555555 !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 21px !important;
            color: #222222 !important;
        }
        .panel-title {
            font-size: 17px;
            font-weight: 700;
            color: #333333;
            margin-top: 0.2rem;
            margin-bottom: 0.25rem;
        }
        .small-note {
            color: #666666;
            font-size: 12px;
            margin-top: -0.3rem;
            margin-bottom: 0.25rem;
        }
        .css-1n76uvr, .css-ocqkz7 { gap: 1.4rem; }
        div[data-testid="stSelectbox"] label { font-size: 12px !important; }
        div[data-testid="stDataFrame"] { border: 1px solid #e5e7eb; border-radius: 6px; }
        @media print {
            .block-container { padding: 0.2rem 0.5rem !important; max-width: 100% !important; }
            [data-testid="stToolbar"], #MainMenu, footer, header { display: none !important; }
            section.main > div { padding-top: 0 !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data utilities
# -----------------------------------------------------------------------------
ROOT = Path(".")
DASHBOARD_DIR = ROOT / "data" / "dashboard"
OUTPUT_DIR = ROOT / "outputs"
FEATURES_PATH = ROOT / "data" / "features" / "customer_features.csv"
RAW_PATH = ROOT / "data" / "raw" / "shopping_trends.csv"


def read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    if path.exists():
        return pd.read_csv(path)
    return None


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame | None]:
    data = {
        "pyramid": read_csv_if_exists(DASHBOARD_DIR / "customer_pyramid.csv"),
        "promo_ret": read_csv_if_exists(DASHBOARD_DIR / "promo_dependency_retention.csv"),
        "geo": read_csv_if_exists(DASHBOARD_DIR / "geography_opportunity.csv"),
        "cat_funnel": read_csv_if_exists(DASHBOARD_DIR / "category_funnel.csv"),
        "cat_sum": read_csv_if_exists(DASHBOARD_DIR / "category_summary.csv"),
        "seg_sum": read_csv_if_exists(DASHBOARD_DIR / "segment_summary.csv"),
        "icp": read_csv_if_exists(DASHBOARD_DIR / "ideal_customer_profile.csv"),
        "metrics": read_csv_if_exists(OUTPUT_DIR / "final_metrics_summary.csv"),
        "features": read_csv_if_exists(FEATURES_PATH),
        "raw": read_csv_if_exists(RAW_PATH),
    }
    required = ["pyramid", "promo_ret", "geo", "cat_funnel", "seg_sum", "metrics"]
    missing = [name for name in required if data[name] is None]
    if missing:
        st.error(
            "Required dashboard CSVs are missing: " + ", ".join(missing) +
            ". Run `python main_pipeline.py` first from the project root."
        )
        st.stop()
    return data


data = load_data()


def get_metric(metrics: pd.DataFrame, key: str, fallback: str = "N/A") -> str:
    if metrics is None or "metric" not in metrics.columns or "value" not in metrics.columns:
        return fallback
    row = metrics.loc[metrics["metric"].astype(str).str.lower() == key.lower(), "value"]
    return str(row.iloc[0]) if not row.empty else fallback


def clean_colnames(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower().replace(" ", "_") for c in out.columns]
    return out


# -----------------------------------------------------------------------------
# Optional slicers from customer_features.csv
# -----------------------------------------------------------------------------
features = data.get("features")
if features is not None:
    features = clean_colnames(features)

# Header and slicers: styled to mimic the uploaded Power BI PDF
st.title("Customer Value Intelligence: D2C Fashion Brand")

filter_left, filter_right = st.columns([1, 1])
selected_season = "All"
selected_gender = "All"

with filter_left:
    if features is not None and "season" in features.columns:
        seasons = ["All"] + sorted(features["season"].dropna().astype(str).unique().tolist())
        selected_season = st.selectbox("Season", seasons, index=0)
    else:
        selected_season = st.selectbox("Season", ["All"], index=0)

with filter_right:
    if features is not None and "gender" in features.columns:
        genders = ["All"] + sorted(features["gender"].dropna().astype(str).unique().tolist())
        selected_gender = st.selectbox("Gender", genders, index=0)
    else:
        selected_gender = st.selectbox("Gender", ["All"], index=0)

# Filter raw feature-level data when possible; otherwise use dashboard summaries.
filtered_features = features.copy() if features is not None else None
if filtered_features is not None:
    if selected_season != "All" and "season" in filtered_features.columns:
        filtered_features = filtered_features[filtered_features["season"].astype(str) == selected_season]
    if selected_gender != "All" and "gender" in filtered_features.columns:
        filtered_features = filtered_features[filtered_features["gender"].astype(str) == selected_gender]

metrics = data["metrics"]

# -----------------------------------------------------------------------------
# KPI cards
# -----------------------------------------------------------------------------
kpi_cols = st.columns(6)
kpi_cols[0].metric("Total Customers", get_metric(metrics, "Total Customers"))
kpi_cols[1].metric("Est. Revenue", get_metric(metrics, "Total Estimated Revenue"))
kpi_cols[2].metric("Organic Revenue", get_metric(metrics, "Organic Revenue %"))
kpi_cols[3].metric("Promo-Dependent Rev", get_metric(metrics, "Promo-Dependent Revenue %"))
kpi_cols[4].metric("Loyal High-Value", get_metric(metrics, "Loyal High-Value Customers"))
kpi_cols[5].metric("At-Risk Dissatisfied", get_metric(metrics, "At-Risk Dissatisfied"))

# -----------------------------------------------------------------------------
# Derived plot data
# -----------------------------------------------------------------------------
SEGMENT_LABELS = {
    "Loyal High-Value": "Champion",
    "High-Value Promo-Dependent": "Promo-Hunter",
    "Organic Mid-Value": "Loyal-Mid-Value",
    "At-Risk Dissatisfied": "High-Value-At-Risk",
    "Low-Repeat Bargain Hunter": "Promo-Hunter",
    "Low-Value Low-Engagement": "Standard",
}

SEGMENT_COLORS = {
    "Standard": "#8A8A80",
    "Promo-Hunter": "#C37713",
    "Loyal-Mid-Value": "#22A07A",
    "High-Value-At-Risk": "#D95B32",
    "Champion": "#7D73D8",
}


def build_segment_summary() -> pd.DataFrame:
    """Build Power BI-like segment summary from feature-level data if available."""
    if filtered_features is not None and "final_segment" in filtered_features.columns:
        df = filtered_features.copy()
        if df.empty:
            return pd.DataFrame(columns=["customer_segment", "customer_count", "promo_dependency"])
        amount_col = "purchase_amount_usd" if "purchase_amount_usd" in df.columns else "purchase_amount"
        promo_col = "promo_dependency_score" if "promo_dependency_score" in df.columns else "promo_dependency"
        seg = df["final_segment"].map(SEGMENT_LABELS).fillna(df["final_segment"].astype(str))
        temp = df.assign(customer_segment=seg)
        summary = temp.groupby("customer_segment", as_index=False).agg(
            customer_count=("customer_segment", "size"),
            promo_dependency=(promo_col, "mean") if promo_col in temp.columns else ("customer_segment", "size"),
            avg_spend=(amount_col, "mean") if amount_col in temp.columns else ("customer_segment", "size"),
        )
        return summary

    ss = data["seg_sum"].copy()
    ss["customer_segment"] = ss["final_segment"].map(SEGMENT_LABELS).fillna(ss["final_segment"])
    return ss.groupby("customer_segment", as_index=False).agg(
        customer_count=("customer_count", "sum"),
        promo_dependency=("avg_promo_dependency", "mean"),
        avg_spend=("avg_purchase_amount", "mean"),
    )


seg_plot = build_segment_summary()
segment_order = ["Standard", "Promo-Hunter", "Loyal-Mid-Value", "High-Value-At-Risk", "Champion"]
seg_plot["segment_order"] = seg_plot["customer_segment"].apply(
    lambda x: segment_order.index(x) if x in segment_order else 999
)
seg_plot = seg_plot.sort_values(["segment_order", "customer_count"], ascending=[True, False])

# -----------------------------------------------------------------------------
# Four-panel dashboard layout
# -----------------------------------------------------------------------------
left, right = st.columns(2)

# Panel 1 ---------------------------------------------------------------------
with left:
    st.markdown('<div class="panel-title">Customer Pyramid- Value Distribution</div>', unsafe_allow_html=True)
    fig1 = px.bar(
        seg_plot.sort_values("customer_count", ascending=True),
        y="customer_segment",
        x="customer_count",
        orientation="h",
        text="customer_count",
        color="customer_segment",
        color_discrete_map=SEGMENT_COLORS,
        labels={"customer_count": "Count of Customer ID", "customer_segment": "customer_segment"},
        height=310,
    )
    fig1.update_traces(textposition="outside", cliponaxis=False)
    fig1.update_layout(
        showlegend=False,
        margin=dict(l=90, r=35, t=10, b=35),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#444", size=11),
        xaxis=dict(showgrid=True, gridcolor="#eeeeee", zeroline=False),
        yaxis=dict(title="customer_segment"),
    )
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

# Panel 2 ---------------------------------------------------------------------
with right:
    st.markdown('<div class="panel-title">Promo Dependency by Segment</div>', unsafe_allow_html=True)
    promo_plot = seg_plot.copy()
    # If the stored score is 0-100, convert to 0-1 to match Power BI-style target PDF.
    if promo_plot["promo_dependency"].max() > 1.5:
        promo_plot["promo_dependency"] = promo_plot["promo_dependency"] / 100.0
    promo_plot = promo_plot.sort_values("promo_dependency", ascending=False)
    fig2 = px.bar(
        promo_plot,
        x="customer_segment",
        y="promo_dependency",
        text=promo_plot["promo_dependency"].map(lambda x: f"{x:.2f}"),
        color="customer_segment",
        color_discrete_map=SEGMENT_COLORS,
        labels={"promo_dependency": "Average of promo_dependency", "customer_segment": "customer_segment"},
        height=310,
    )
    fig2.update_traces(textposition="outside", cliponaxis=False)
    fig2.update_layout(
        showlegend=False,
        margin=dict(l=50, r=20, t=10, b=80),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#444", size=11),
        yaxis=dict(range=[0, max(1.05, promo_plot["promo_dependency"].max() * 1.15)], showgrid=True, gridcolor="#eeeeee"),
        xaxis=dict(tickangle=-35),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

left2, right2 = st.columns(2)

# Panel 3 ---------------------------------------------------------------------
with left2:
    st.markdown('<div class="panel-title">Geographic Opportunity: Spend vs Promo Dependency</div>', unsafe_allow_html=True)
    geo = data["geo"].copy()
    if "opportunity_score" in geo.columns:
        color_col = "opportunity_score"
    elif "geo_opportunity" in geo.columns:
        color_col = "geo_opportunity"
    else:
        color_col = geo.columns[-1]

    fig3 = px.choropleth(
        geo,
        locations="location",
        locationmode="USA-states",
        color=color_col,
        scope="usa",
        color_continuous_scale=["#F4A261", "#A8D5BA", "#2A9D8F"],
        hover_name="location",
        hover_data=[c for c in ["geo_customer_count", "geo_avg_spend", "geo_promo_rate", "geo_opportunity"] if c in geo.columns],
        height=330,
    )
    fig3.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(bgcolor="white", lakecolor="#f7fbff"),
        paper_bgcolor="white",
        font=dict(color="#444", size=10),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

# Panel 4 ---------------------------------------------------------------------
with right2:
    st.markdown('<div class="panel-title">Category Funnel: Entry Point vs Retention</div>', unsafe_allow_html=True)
    cat = data["cat_funnel"].copy()

    # Build an entry vs retention view, similar to the Power BI PDF.
    if {"category", "purchase_history_tier", "customer_count"}.issubset(cat.columns):
        entry = cat[cat["purchase_history_tier"].astype(str).str.contains("New", case=False, na=False)]
        retention = cat[cat["purchase_history_tier"].astype(str).str.contains("Established", case=False, na=False)]
        entry_view = entry.groupby("category", as_index=False).agg(value=("customer_count", "sum"))
        entry_view["Category Role"] = "Entry-Point Category"
        retention_view = retention.groupby("category", as_index=False).agg(value=("customer_count", "sum"))
        retention_view["Category Role"] = "Retention Category"
        cat_view = pd.concat([entry_view, retention_view], ignore_index=True)
    else:
        cs = data["cat_sum"].copy()
        cat_view = pd.DataFrame({
            "category": cs["category"],
            "value": cs["avg_prev_purchases"],
            "Category Role": "Retention Category",
        })

    fig4 = px.bar(
        cat_view,
        y="category",
        x="value",
        color="Category Role",
        orientation="h",
        barmode="group",
        text=cat_view["value"].map(lambda x: f"{x:.0f}" if x >= 100 else f"{x:.2f}"),
        color_discrete_map={
            "Entry-Point Category": "#D95B32",
            "Retention Category": "#7D73D8",
        },
        labels={"value": "Average of Previous Purchases", "category": "Category"},
        height=330,
    )
    fig4.update_traces(textposition="outside", cliponaxis=False)
    fig4.update_layout(
        legend=dict(orientation="h", y=1.13, x=0, title="Category Role"),
        margin=dict(l=85, r=35, t=30, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#444", size=11),
        xaxis=dict(showgrid=True, gridcolor="#eeeeee"),
        yaxis=dict(title="Category"),
    )
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

# -----------------------------------------------------------------------------
# Compact supporting tables, included below the four-panel dashboard.
# -----------------------------------------------------------------------------
with st.expander("Full Segment Summary Table", expanded=False):
    ss = data["seg_sum"].copy()
    show_cols = [
        c for c in [
            "final_segment", "customer_count", "revenue_share_pct", "avg_purchase_amount",
            "avg_total_spend_est", "avg_promo_dependency", "avg_retention_proxy",
            "avg_review_rating", "pct_discount_applied", "segment_definition",
        ] if c in ss.columns
    ]
    st.dataframe(ss[show_cols], use_container_width=True, hide_index=True)

with st.expander("Ideal Customer Profile", expanded=False):
    icp = data.get("icp")
    if icp is not None:
        icp = clean_colnames(icp)
        rename_map = {
            "attribute": "Attribute",
            "value": "Value",
            "business_implication": "Business Implication",
            "business_implications": "Business Implication",
            "implication": "Business Implication",
        }
        icp_display = icp.rename(columns=rename_map)
        required = ["Attribute", "Value", "Business Implication"]
        if set(required).issubset(icp_display.columns):
            st.dataframe(icp_display[required], use_container_width=True, hide_index=True)
        else:
            st.dataframe(icp_display, use_container_width=True, hide_index=True)

st.caption("Dashboard powered by data/dashboard/*.csv | Run python main_pipeline.py to refresh")
