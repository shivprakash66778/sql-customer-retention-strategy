"""
app.py
Customer Value Intelligence Dashboard

Run with:
streamlit run app.py

Expected project folders:
data/dashboard/*.csv
outputs/final_metrics_summary.csv

This version is optimized for PDF export and screenshots.
It uses a white background, clean text, visible panel borders and data labels.
"""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Customer Value Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background: #ffffff !important;
            color: #111827 !important;
        }
        [data-testid="stToolbar"], #MainMenu, footer {
            visibility: hidden;
            height: 0%;
        }
        .block-container {
            padding-top: 1.0rem !important;
            padding-bottom: 0.5rem !important;
            max-width: 1260px !important;
        }
        h1 {
            text-align: center;
            color: #111827 !important;
            font-size: 30px !important;
            font-weight: 760 !important;
            margin-bottom: 0.1rem !important;
        }
        h2, h3, p, label, span, div {
            color: #111827 !important;
        }
        [data-testid="stMetric"] {
            background: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            padding: 0.55rem 0.70rem !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
        }
        [data-testid="stMetricLabel"] p {
            font-size: 12px !important;
            color: #4b5563 !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 21px !important;
            color: #111827 !important;
        }
        .subtitle {
            text-align: center;
            color: #4b5563 !important;
            font-size: 13px;
            margin-bottom: 0.75rem;
        }
        .panel-card {
            border: 2px solid #1f4e79;
            border-radius: 12px;
            padding: 12px 14px 8px 14px;
            margin: 8px 0 14px 0;
            background: #ffffff;
            box-shadow: 0 2px 6px rgba(31,78,121,0.12);
        }
        .panel-title {
            font-size: 18px;
            font-weight: 750;
            color: #1f4e79 !important;
            margin-bottom: 2px;
        }
        .panel-note {
            font-size: 12px;
            color: #6b7280 !important;
            margin-bottom: 8px;
        }
        .small-note {
            font-size: 11px;
            color: #6b7280 !important;
            text-align: center;
            margin-top: 2px;
        }
        div[data-testid="stDataFrame"] {
            background: #ffffff !important;
            color: #111827 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def clean_text(value: object) -> str:
    """Return display safe text without emojis, hyphens or long dashes."""
    text = str(value)
    text = re.sub(r"[\U00010000-\U0010ffff]", "", text)
    text = text.replace("-", " ").replace("–", " ").replace("—", " ")
    text = text.replace("|", " ")
    text = " ".join(text.split())
    return text


def short_segment_label(value: object) -> str:
    mapping = {
        "Loyal High-Value": "Loyal High Value",
        "High-Value Promo-Dependent": "Promo Dependent",
        "Organic Mid-Value": "Organic Mid Value",
        "At-Risk Dissatisfied": "At Risk",
        "Low-Repeat Bargain Hunter": "Bargain Hunter",
        "Low-Value Low-Engagement": "Low Engagement",
    }
    return clean_text(mapping.get(str(value), value))


def first_existing_path(paths: list[str]) -> Path | None:
    for path in paths:
        p = Path(path)
        if p.exists():
            return p
    return None


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    dashboard_dir = first_existing_path([
        "data/dashboard",
        "dashboard/dashboard_ready_csvs",
        "customer_value_final_submission/data/dashboard",
        "/mnt/data/customer_value_final_submission/data/dashboard",
    ])
    metrics_path = first_existing_path([
        "outputs/final_metrics_summary.csv",
        "customer_value_final_submission/outputs/final_metrics_summary.csv",
        "/mnt/data/customer_value_final_submission/outputs/final_metrics_summary.csv",
    ])

    if dashboard_dir is None:
        raise FileNotFoundError("Dashboard CSV folder was not found.")
    if metrics_path is None:
        raise FileNotFoundError("Final metrics summary file was not found.")

    return {
        "pyramid": pd.read_csv(dashboard_dir / "customer_pyramid.csv"),
        "promo_ret": pd.read_csv(dashboard_dir / "promo_dependency_retention.csv"),
        "geo": pd.read_csv(dashboard_dir / "geography_opportunity.csv"),
        "cat_funnel": pd.read_csv(dashboard_dir / "category_funnel.csv"),
        "cat_sum": pd.read_csv(dashboard_dir / "category_summary.csv"),
        "seg_sum": pd.read_csv(dashboard_dir / "segment_summary.csv"),
        "icp": pd.read_csv(dashboard_dir / "ideal_customer_profile.csv"),
        "metrics": pd.read_csv(metrics_path),
    }


try:
    data = load_data()
except FileNotFoundError as exc:
    st.error(f"Data files not found. Run python main_pipeline.py first. {exc}")
    st.stop()


def metric_value(df: pd.DataFrame, key: str) -> str:
    if "metric" not in df.columns or "value" not in df.columns:
        return "Not available"
    row = df[df["metric"] == key]
    return str(row["value"].iloc[0]) if not row.empty else "Not available"


def plot_layout(fig: go.Figure, height: int = 345) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#111827", size=11),
        margin=dict(l=20, r=18, t=20, b=35),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e5e7eb", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#e5e7eb", zeroline=False)
    return fig


metrics = data["metrics"]

st.title("Customer Value Intelligence Dashboard")
st.markdown(
    "<div class='subtitle'>Decoding Customer Value  SQL Driven Retention Strategy  Summer Projects 26</div>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Customers", metric_value(metrics, "Total Customers"))
k2.metric("Estimated Revenue", metric_value(metrics, "Total Estimated Revenue"))
k3.metric("Organic Revenue", metric_value(metrics, "Organic Revenue %"))
k4.metric("Promo Dependent Revenue", metric_value(metrics, "Promo-Dependent Revenue %"))
k5.metric("Loyal High Value", metric_value(metrics, "Loyal High-Value Customers"))
k6.metric("At Risk Dissatisfied", metric_value(metrics, "At-Risk Dissatisfied"))

left, right = st.columns(2, gap="large")

with left:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>Panel 1 Customer Value Pyramid</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-note'>Value distribution across the customer base with revenue contribution.</div>", unsafe_allow_html=True)

    pyr = data["pyramid"].copy()
    if "value_tier" in pyr.columns:
        pyr["value_tier_clean"] = pyr["value_tier"].map(clean_text)
        order = ["High", "Medium", "Low"]
        pyr = pyr.set_index("value_tier").reindex(order).reset_index()
        pyr["value_tier_clean"] = pyr["value_tier"].map(clean_text)

    fig1 = go.Figure()
    fig1.add_bar(
        name="Customers Percent",
        x=pyr["value_tier_clean"],
        y=pyr["pct_of_customers"],
        marker_color="#1f4e79",
        text=pyr["pct_of_customers"].map(lambda x: f"{x:.1f}%"),
        textposition="outside",
        cliponaxis=False,
    )
    fig1.add_bar(
        name="Revenue Percent",
        x=pyr["value_tier_clean"],
        y=pyr["pct_of_revenue"],
        marker_color="#70ad47",
        text=pyr["pct_of_revenue"].map(lambda x: f"{x:.1f}%"),
        textposition="outside",
        cliponaxis=False,
    )
    fig1.update_layout(barmode="group", yaxis_range=[0, max(pyr["pct_of_revenue"].max(), pyr["pct_of_customers"].max()) + 12])
    fig1.update_xaxes(title="Value Tier")
    fig1.update_yaxes(title="Percentage")
    st.plotly_chart(plot_layout(fig1, 330), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>Panel 2 Promo Dependency and Retention Signal</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-note'>Segment level view of discount reliance and repeat purchase signal.</div>", unsafe_allow_html=True)

    pr = data["promo_ret"].copy()
    pr["segment_label"] = pr["final_segment"].map(short_segment_label)
    fig2 = px.scatter(
        pr,
        x="avg_promo_dependency",
        y="avg_retention_proxy",
        size="customer_count",
        color="segment_label",
        text="segment_label",
        size_max=48,
        color_discrete_sequence=["#1f4e79", "#ed7d31", "#70ad47", "#c00000", "#7f7f7f", "#a5a5a5"],
        labels={
            "avg_promo_dependency": "Promo Dependency Score",
            "avg_retention_proxy": "Retention Signal Score",
            "segment_label": "Segment",
        },
    )
    fig2.update_traces(textposition="top center", textfont=dict(size=10), marker=dict(line=dict(width=1, color="#ffffff")))
    fig2.add_vline(x=50, line_dash="dot", line_color="#6b7280")
    fig2.add_hline(y=50, line_dash="dot", line_color="#6b7280")
    fig2.update_layout(showlegend=False, xaxis_range=[0, 100], yaxis_range=[0, 100])
    st.plotly_chart(plot_layout(fig2, 330), use_container_width=True, config={"displayModeBar": False})
    st.markdown("<div class='small-note'>Retention signal is a proxy because the dataset has no timestamps.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

left2, right2 = st.columns(2, gap="large")

with left2:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>Panel 3 Geographic Opportunity</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-note'>Top states ranked by spend, satisfaction, low promo reliance and high value share.</div>", unsafe_allow_html=True)

    geo = data["geo"].copy().sort_values("opportunity_score", ascending=False).head(10)
    geo["location_clean"] = geo["location"].map(clean_text)
    geo = geo.sort_values("opportunity_score", ascending=True)
    fig3 = px.bar(
        geo,
        x="opportunity_score",
        y="location_clean",
        orientation="h",
        text="opportunity_score",
        color="geo_opportunity",
        color_discrete_sequence=["#1f4e79", "#70ad47", "#ed7d31"],
        labels={"opportunity_score": "Opportunity Score", "location_clean": "State", "geo_opportunity": "Opportunity Level"},
        hover_data=["geo_customer_count", "geo_avg_spend", "geo_promo_rate", "geo_avg_rating"],
    )
    fig3.update_traces(textposition="outside", cliponaxis=False)
    fig3.update_layout(showlegend=False, xaxis_range=[0, max(geo["opportunity_score"].max() + 1, 5)])
    st.plotly_chart(plot_layout(fig3, 330), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with right2:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>Panel 4 Category Funnel</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel-note'>Categories compared by new, developing and established purchase history groups.</div>", unsafe_allow_html=True)

    cf = data["cat_funnel"].copy()
    cf["category_clean"] = cf["category"].map(clean_text)
    history_order = ["New (0-5)", "Developing (6-15)", "Established (16+)"]
    cf["history_label"] = pd.Categorical(cf["purchase_history_tier"].map(clean_text), categories=[clean_text(x) for x in history_order], ordered=True)
    fig4 = px.bar(
        cf,
        x="category_clean",
        y="customer_count",
        color="history_label",
        barmode="group",
        text="customer_count",
        color_discrete_sequence=["#9dc3e6", "#4472c4", "#1f4e79"],
        labels={"category_clean": "Category", "customer_count": "Customers", "history_label": "Purchase History"},
        hover_data=["avg_spend", "avg_promo_dep", "avg_rating"],
    )
    fig4.update_traces(textposition="outside", cliponaxis=False)
    fig4.update_yaxes(title="Number of Customers")
    st.plotly_chart(plot_layout(fig4, 330), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='small-note'>Dashboard powered by data dashboard CSV files. Run python main_pipeline.py to refresh.</div>", unsafe_allow_html=True)
