from __future__ import annotations

import math
from datetime import date
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# -----------------------------------------------------------------------------
# Page setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PV Studio | التصميم الذكي للأنظمة الشمسية",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Styling: Arabic RTL layout, responsive cards, calm technical visual identity
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;600;700;800&display=swap');

    :root {
        --pv-ink: #12263A;
        --pv-muted: #64748B;
        --pv-green: #087F5B;
        --pv-green-dark: #075B45;
        --pv-lime: #D9F99D;
        --pv-gold: #F4B942;
        --pv-border: #E2E8F0;
        --pv-card: rgba(255,255,255,0.94);
        --pv-bg: #F4F7FB;
    }

    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Tajawal', 'Segoe UI', Tahoma, Arial, sans-serif;
    }
    .stApp {
        background: radial-gradient(circle at 8% 0%, #E7F6EF 0, transparent 25%), var(--pv-bg);
        color: var(--pv-ink);
        direction: rtl;
    }
    [data-testid="stSidebar"] {
        direction: rtl;
        border-left: 1px solid var(--pv-border);
        border-right: 0;
        background: #FBFDFC;
    }
    [data-testid="stSidebar"] * { text-align: right; }
    .block-container { padding-top: 1.3rem; padding-bottom: 3rem; max-width: 1500px; }
    h1, h2, h3, h4 { color: var(--pv-ink); font-weight: 800 !important; }
    p, li, label, small, .stMarkdown { line-height: 1.75; }
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--pv-border);
        padding: 0.85rem 1rem;
        border-radius: 16px;
        box-shadow: 0 5px 20px rgba(18, 38, 58, 0.035);
        direction: rtl;
        text-align: right;
    }
    [data-testid="stMetricLabel"] { justify-content: flex-start; color: var(--pv-muted); }
    [data-testid="stMetricValue"] { color: var(--pv-green-dark); font-weight: 800; }
    [data-testid="stTabs"] button { font-family: inherit; font-weight: 700; }
    [data-testid="stTabs"] [aria-selected="true"] { color: var(--pv-green) !important; }
    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.7);
        border: 1px solid var(--pv-border);
        border-radius: 12px;
    }
    div[data-testid="stAlert"] { direction: rtl; text-align: right; border-radius: 12px; }
    div[data-testid="stDataFrame"] { direction: rtl; }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 1.7rem 1.8rem;
        margin-bottom: 1.15rem;
        border-radius: 24px;
        background: linear-gradient(125deg, #064E3B 0%, #087F5B 58%, #109B72 100%);
        color: #FFFFFF;
        box-shadow: 0 16px 35px rgba(7, 91, 69, 0.17);
    }
    .hero:after {
        content: '☀';
        position: absolute;
        left: 2.4rem;
        top: -2.7rem;
        font-size: 11rem;
        color: rgba(255,255,255,0.09);
        line-height: 1;
    }
    .hero-kicker {
        color: #D9F99D;
        font-size: 0.83rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        margin-bottom: 0.45rem;
    }
    .hero h1 { color: white !important; font-size: clamp(1.55rem, 3vw, 2.25rem); margin: 0 0 0.5rem 0; }
    .hero p { color: #E8FFF5; font-size: 1.02rem; max-width: 900px; margin: 0; }
    .hero-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
    .hero-chip {
        display: inline-block; padding: 0.32rem 0.72rem; border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.25); background: rgba(255,255,255,0.10);
        color: white; font-size: 0.82rem; font-weight: 700;
    }
    .section-kicker { color: var(--pv-green); font-size: 0.82rem; font-weight: 800; margin-bottom: -0.3rem; }
    .panel-card {
        background: var(--pv-card); border: 1px solid var(--pv-border); border-radius: 18px;
        padding: 1rem 1.1rem; box-shadow: 0 6px 18px rgba(18,38,58,0.035); margin-bottom: 0.75rem;
    }
    .panel-card h4 { margin: 0 0 0.4rem 0; font-size: 1rem; }
    .panel-card p { color: var(--pv-muted); margin: 0; font-size: 0.93rem; }
    .tiny-note { color: var(--pv-muted); font-size: 0.84rem; }
    .status-pill { display: inline-block; border-radius: 999px; padding: 0.25rem 0.65rem; background: #ECFDF5; color: #047857; font-weight: 800; font-size: 0.8rem; }
    .divider { height: 1px; background: var(--pv-border); margin: 1rem 0; }
    @media (max-width: 700px) {
        .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
        .hero { padding: 1.25rem; }
        .hero:after { left: -0.4rem; font-size: 7rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Constants and simple calculation functions
# -----------------------------------------------------------------------------
CITY_PSH: dict[str, float] = {
    "بريدة / القصيم": 6.00,
    "حائل": 5.85,
    "الرياض": 6.10,
    "جدة / مكة المكرمة": 6.25,
    "الدمام / الشرقية": 5.95,
    "أبها / الجنوب": 6.40,
    "تبوك": 6.00,
}

# Defaults based on the Saudi Electricity Service Guide tariff table.
# The industrial tariff is not universal; it must be confirmed for the actual customer.
TARIFF_DEFAULTS: dict[str, dict[str, float]] = {
    "سكني (منزل / فيلا)": {"low": 0.18, "high": 0.30},
    "تجاري": {"low": 0.20, "high": 0.30},
    "زراعي": {"low": 0.16, "high": 0.20},
    "صناعي (تعرفة مخصصة)": {"low": 0.18, "high": 0.18},
}

SYSTEM_OPTIONS = [
    "مربوط بالشبكة (On-Grid)",
    "هجين مع تخزين بطاريات (Hybrid)",
    "منفصل عن الشبكة (Off-Grid)",
]

PV_COST_DEFAULTS = {
    "مربوط بالشبكة (On-Grid)": 3800.0,
    "هجين مع تخزين بطاريات (Hybrid)": 4300.0,
    "منفصل عن الشبكة (Off-Grid)": 5000.0,
}
BATTERY_COST_DEFAULTS = {
    "مربوط بالشبكة (On-Grid)": 0.0,
    "هجين مع تخزين بطاريات (Hybrid)": 1300.0,
    "منفصل عن الشبكة (Off-Grid)": 1500.0,
}
SELF_USE_DEFAULTS = {
    "مربوط بالشبكة (On-Grid)": 45,
    "هجين مع تخزين بطاريات (Hybrid)": 80,
    "منفصل عن الشبكة (Off-Grid)": 95,
}


def energy_bill_monthly(
    kwh: float,
    low_rate: float,
    high_rate: float,
    tier_limit: float,
    vat_rate: float,
) -> float:
    """Estimate monthly energy charges using a two-tier tariff plus optional VAT.

    Excludes fixed meter/service fees and any non-energy bill items.
    """
    usage = max(float(kwh), 0.0)
    first_tier = min(usage, tier_limit) * low_rate
    second_tier = max(usage - tier_limit, 0.0) * high_rate
    return (first_tier + second_tier) * (1.0 + vat_rate)


def estimate_first_year_bill_savings(
    monthly_load_kwh: float,
    annual_pv_kwh: float,
    system_type: str,
    self_consumption_pct: float,
    export_rate: float,
    low_rate: float,
    high_rate: float,
    tier_limit: float,
    vat_rate: float,
) -> dict[str, float]:
    """Estimate bill savings using equal-average-month assumptions.

    This is a simplified financial proxy, not an hourly energy-flow simulation.
    """
    baseline_monthly_bill = energy_bill_monthly(
        monthly_load_kwh, low_rate, high_rate, tier_limit, vat_rate
    )
    baseline_annual_bill = baseline_monthly_bill * 12.0
    if system_type == "منفصل عن الشبكة (Off-Grid)":
        # Assumes the off-grid design actually meets the load; unserved energy and
        # generator fuel are not modelled by this simplified estimator.
        return {
            "baseline_annual_bill": baseline_annual_bill,
            "post_solar_annual_bill": 0.0,
            "annual_savings": baseline_annual_bill,
            "self_used_kwh": min(annual_pv_kwh, monthly_load_kwh * 12.0),
            "exported_kwh": 0.0,
            "export_credit": 0.0,
        }

    average_month_pv = max(annual_pv_kwh, 0.0) / 12.0
    direct_share = max(0.0, min(self_consumption_pct / 100.0, 1.0))
    self_used_per_month = min(monthly_load_kwh, average_month_pv * direct_share)
    grid_import_per_month = max(monthly_load_kwh - self_used_per_month, 0.0)
    exported_per_month = max(average_month_pv - self_used_per_month, 0.0)

    post_solar_monthly_bill = energy_bill_monthly(
        grid_import_per_month, low_rate, high_rate, tier_limit, vat_rate
    )
    annual_grid_bill_after_solar = post_solar_monthly_bill * 12.0
    annual_exported_kwh = exported_per_month * 12.0
    export_credit = annual_exported_kwh * max(export_rate, 0.0)
    # Export credits are capped at the estimated remaining bill in this simple model.
    post_solar_annual_bill = max(0.0, annual_grid_bill_after_solar - export_credit)
    annual_savings = max(0.0, baseline_annual_bill - post_solar_annual_bill)

    return {
        "baseline_annual_bill": baseline_annual_bill,
        "post_solar_annual_bill": post_solar_annual_bill,
        "annual_savings": annual_savings,
        "self_used_kwh": self_used_per_month * 12.0,
        "exported_kwh": annual_exported_kwh,
        "export_credit": min(export_credit, annual_grid_bill_after_solar),
    }


def calculate_cashflow(
    *,
    capex: float,
    annual_savings_year1: float,
    annual_generation_kwh: float,
    lifetime_years: int,
    degradation_rate: float,
    tariff_escalation: float,
    annual_om_rate: float,
    inverter_replacement_year: int,
    inverter_replacement_fraction: float,
    battery_capex: float,
    battery_replacement_year: int,
    battery_replacement_fraction: float,
    scenario_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Create annual cash flows and cumulative net cash flows for one scenario."""
    rows: list[dict[str, float | int]] = [
        {
            "السنة": 0,
            "إنتاج الطاقة (kWh)": 0.0,
            "التوفير (ريال)": 0.0,
            "الصيانة والتشغيل (ريال)": 0.0,
            "الاستبدال (ريال)": 0.0,
            "صافي التدفق النقدي (ريال)": -capex,
            "التدفق التراكمي (ريال)": -capex,
        }
    ]
    cumulative = -capex
    annual_om = capex * max(annual_om_rate, 0.0)

    for year in range(1, lifetime_years + 1):
        years_elapsed = year - 1
        generation = annual_generation_kwh * ((1.0 - degradation_rate) ** years_elapsed)
        savings = (
            annual_savings_year1
            * scenario_multiplier
            * ((1.0 - degradation_rate) ** years_elapsed)
            * ((1.0 + tariff_escalation) ** years_elapsed)
        )
        replacement = 0.0
        if inverter_replacement_year > 0 and year == inverter_replacement_year:
            replacement += capex * max(inverter_replacement_fraction, 0.0)
        if battery_capex > 0 and battery_replacement_year > 0 and year == battery_replacement_year:
            replacement += battery_capex * max(battery_replacement_fraction, 0.0)

        net_cashflow = savings - annual_om - replacement
        cumulative += net_cashflow
        rows.append(
            {
                "السنة": year,
                "إنتاج الطاقة (kWh)": generation,
                "التوفير (ريال)": savings,
                "الصيانة والتشغيل (ريال)": annual_om,
                "الاستبدال (ريال)": replacement,
                "صافي التدفق النقدي (ريال)": net_cashflow,
                "التدفق التراكمي (ريال)": cumulative,
            }
        )

    df = pd.DataFrame(rows)
    return {"dataframe": df, "cumulative": df["التدفق التراكمي (ريال)"].tolist()}


def payback_period(cumulative: list[float]) -> float | None:
    """Interpolate the first year in which cumulative net cash flow becomes >= 0."""
    for year in range(1, len(cumulative)):
        previous_value = float(cumulative[year - 1])
        current_value = float(cumulative[year])
        if current_value >= 0 and previous_value < 0:
            increase = current_value - previous_value
            if increase <= 0:
                return float(year)
            return (year - 1) + abs(previous_value) / increase
        if previous_value >= 0:
            return float(year - 1)
    return None


def net_present_value(cashflows: list[float], discount_rate: float) -> float:
    return sum(float(cf) / ((1.0 + discount_rate) ** year) for year, cf in enumerate(cashflows))


def levelized_cost_of_energy(
    capex: float,
    cashflow_df: pd.DataFrame,
    discount_rate: float,
) -> float:
    """Discounted lifecycle cost per discounted kWh of generation."""
    lifecycle_cost = capex
    discounted_generation = 0.0
    for _, row in cashflow_df.iterrows():
        year = int(row["السنة"])
        if year == 0:
            continue
        discount_factor = (1.0 + discount_rate) ** year
        lifecycle_cost += (
            float(row["الصيانة والتشغيل (ريال)"])
            + float(row["الاستبدال (ريال)"])
        ) / discount_factor
        discounted_generation += float(row["إنتاج الطاقة (kWh)"]) / discount_factor
    return lifecycle_cost / discounted_generation if discounted_generation > 0 else 0.0


def sar(value: float, decimals: int = 0) -> str:
    return f"{value:,.{decimals}f} ريال"


def make_cumulative_chart(scenarios: dict[str, dict[str, Any]]) -> go.Figure:
    fig = go.Figure()
    lines = [
        ("السيناريو الأساسي", scenarios["base"]["cumulative"], "#087F5B", 3),
        ("السيناريو المتفائل", scenarios["optimistic"]["cumulative"], "#D97706", 2),
        ("السيناريو المتحفظ", scenarios["conservative"]["cumulative"], "#64748B", 2),
    ]
    for name, values, color, width in lines:
        fig.add_trace(
            go.Scatter(
                x=list(range(len(values))),
                y=values,
                mode="lines",
                name=name,
                line={"color": color, "width": width},
                hovertemplate="السنة %{x}<br>%{y:,.0f} ريال<extra>%{fullData.name}</extra>",
            )
        )
    fig.add_hline(y=0, line_dash="dash", line_color="#94A3B8", line_width=1)
    fig.update_layout(
        template="plotly_white",
        height=390,
        margin={"l": 16, "r": 16, "t": 20, "b": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.0)",
        font={"family": "Tajawal, Segoe UI, Arial", "size": 13, "color": "#12263A"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        xaxis={"title": "عمر المشروع (سنة)", "gridcolor": "#E2E8F0", "zeroline": False},
        yaxis={"title": "التدفق النقدي التراكمي (ريال)", "gridcolor": "#E2E8F0", "zeroline": False, "tickformat": ",.0f"},
    )
    return fig


def make_generation_chart(annual_demand: float, annual_generation: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["الاستهلاك السنوي", "الإنتاج الشمسي المتوقع"],
            y=[annual_demand, annual_generation],
            marker_color=["#64748B", "#087F5B"],
            text=[f"{annual_demand:,.0f}", f"{annual_generation:,.0f}"],
            textposition="outside",
            hovertemplate="%{x}<br>%{y:,.0f} kWh<extra></extra>",
        )
    )
    fig.update_layout(
        template="plotly_white",
        height=320,
        showlegend=False,
        margin={"l": 15, "r": 15, "t": 15, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.0)",
        font={"family": "Tajawal, Segoe UI, Arial", "size": 13, "color": "#12263A"},
        yaxis={"title": "الطاقة (kWh/سنة)", "gridcolor": "#E2E8F0", "tickformat": ",.0f"},
        xaxis={"title": ""},
    )
    return fig


# -----------------------------------------------------------------------------
# Sidebar: project, engineering and economic inputs
# -----------------------------------------------------------------------------
st.sidebar.markdown("## ⚙️ إعدادات التصميم")
st.sidebar.caption("عدّل المدخلات لمقارنة أكثر من سيناريو. النتائج تقديرية وتعتمد على جودة البيانات.")

facility_type = st.sidebar.selectbox(
    "نوع المنشأة",
    ["سكني (منزل / فيلا)", "تجاري", "زراعي", "صناعي (تعرفة مخصصة)"],
    index=0,
)
city = st.sidebar.selectbox("المدينة / الموقع", list(CITY_PSH.keys()), index=0)
psh = st.sidebar.number_input(
    "ساعات الذروة الشمسية المكافئة (ساعة/يوم)",
    min_value=3.0,
    max_value=8.0,
    value=float(CITY_PSH[city]),
    step=0.05,
    format="%.2f",
    key=f"psh_{city}",
    help="قيمة أولية قابلة للتعديل. استخدم بيانات الموقع الفعلي عند إعداد التصميم النهائي.",
)

system_type = st.sidebar.selectbox("هيكلية النظام", SYSTEM_OPTIONS, index=0)
monthly_default = 2500 if facility_type == "سكني (منزل / فيلا)" else 8000
monthly_kwh = st.sidebar.number_input(
    "متوسط الاستهلاك الشهري (kWh)",
    min_value=100.0,
    max_value=2_000_000.0,
    value=float(monthly_default),
    step=100.0,
    key=f"monthly_kwh_{facility_type}",
    help="أدخل متوسط الاستهلاك الشهري على مدار سنة كاملة، وليس أعلى فاتورة فقط.",
)
available_area = st.sidebar.number_input(
    "مساحة السطح الصالحة للتركيب (m²)",
    min_value=10.0,
    max_value=100_000.0,
    value=200.0,
    step=10.0,
)

with st.sidebar.expander("🛠️ المعاملات الهندسية", expanded=True):
    panel_watt = st.selectbox("قدرة اللوح الشمسي (W)", [450, 500, 550, 580, 600, 620, 650, 700], index=4)
    panel_area = st.number_input("مساحة اللوح الواحد (m²)", min_value=1.0, max_value=4.0, value=2.60, step=0.05)
    inverter_eff = st.slider("كفاءة العاكس (%)", 90, 99, 97, 1) / 100.0
    other_losses = st.slider(
        "الفواقد الأخرى: حرارة وغبار وكابلات (%)", 5, 35, 18, 1
    ) / 100.0
    dc_ac_ratio = st.slider(
        "نسبة قدرة الألواح DC إلى العاكس AC", 1.00, 1.40, 1.20, 0.05,
        help="تقدير أولي لقياس العاكس؛ لا يغني عن حساب تيارات البدء والذروة للأحمال.",
    )
    roof_spacing_pct = st.slider(
        "هامش المساحة للممرات والتباعد (%)", 10, 40, 20, 5
    )
    coverage_pct = st.slider(
        "هدف التغطية السنوية من الطاقة المطلوبة (%)", 50, 130, 100, 5,
        key=f"coverage_{system_type}",
    )
    offgrid_margin_pct = 0
    if system_type == "منفصل عن الشبكة (Off-Grid)":
        offgrid_margin_pct = st.slider(
            "هامش تصميم إضافي للنظام المستقل (%)", 10, 50, 25, 5
        )
    performance_ratio = inverter_eff * (1.0 - other_losses)

battery_dod = 0.80
battery_efficiency = 0.92
battery_nominal_kwh = 0.0
battery_load_share_pct = 0
autonomy_days = 0.0
if system_type != "مربوط بالشبكة (On-Grid)":
    with st.sidebar.expander("🔋 إعدادات التخزين", expanded=True):
        battery_load_share_pct = st.slider(
            "نسبة الاستهلاك اليومي المراد تغطيتها بالبطارية (%)",
            20,
            100,
            60 if system_type == "هجين مع تخزين بطاريات (Hybrid)" else 100,
            5,
            key=f"battery_share_{system_type}",
        )
        autonomy_days = st.slider(
            "مدة الاستقلالية المستهدفة (يوم)",
            0.25,
            3.0,
            0.50 if system_type == "هجين مع تخزين بطاريات (Hybrid)" else 1.0,
            0.25,
            key=f"autonomy_{system_type}",
        )
        battery_dod = st.slider("عمق التفريغ المسموح للبطارية DOD (%)", 50, 95, 80, 5) / 100.0
        battery_efficiency = st.slider("كفاءة دورة البطارية (%)", 80, 98, 92, 1) / 100.0

with st.sidebar.expander("💵 التعرفة والتكاليف والتمويل", expanded=False):
    st.markdown("**تعرفة الطاقة**")
    tariff_defaults = TARIFF_DEFAULTS[facility_type]
    tariff_low = st.number_input(
        "التعرفة الأساسية (ريال/kWh)",
        min_value=0.0,
        max_value=2.0,
        value=float(tariff_defaults["low"]),
        step=0.01,
        format="%.2f",
        key=f"tariff_low_{facility_type}",
    )
    tariff_high = st.number_input(
        "تعرفة الشريحة الأعلى (ريال/kWh)",
        min_value=0.0,
        max_value=2.0,
        value=float(tariff_defaults["high"]),
        step=0.01,
        format="%.2f",
        key=f"tariff_high_{facility_type}",
    )
    tier_limit = st.number_input(
        "حد الشريحة الأولى (kWh/شهر)",
        min_value=100.0,
        max_value=100_000.0,
        value=6000.0,
        step=500.0,
    )
    vat_pct = st.slider("ضريبة القيمة المضافة على فاتورة الطاقة (%)", 0, 20, 15, 1)
    export_rate = st.number_input(
        "قيمة تعويض الطاقة المصدّرة (ريال/kWh)",
        min_value=0.0,
        max_value=2.0,
        value=0.0,
        step=0.01,
        format="%.2f",
        help="القيمة الافتراضية صفر للتحفظ. غيّرها فقط عند معرفة تعرفة التصدير الواردة في اتفاقية الربط.",
    )

    st.markdown("**تكاليف المشروع**")
    pv_cost_per_kw = st.number_input(
        "تكلفة النظام المركب دون البطاريات (ريال/kWp)",
        min_value=500.0,
        max_value=20_000.0,
        value=float(PV_COST_DEFAULTS[system_type]),
        step=100.0,
        key=f"pv_cost_{system_type}",
        help="افتراض ميزانية أولي يشمل الألواح والعاكس/معدات النظام والتركيب؛ استبدله بعرض سعر محلي.",
    )
    battery_cost_per_kwh = 0.0
    if system_type != "مربوط بالشبكة (On-Grid)":
        battery_cost_per_kwh = st.number_input(
            "تكلفة البطارية الاسمية (ريال/kWh)",
            min_value=100.0,
            max_value=10_000.0,
            value=float(BATTERY_COST_DEFAULTS[system_type]),
            step=50.0,
            key=f"battery_cost_{system_type}",
        )
    annual_om_pct = st.slider("الصيانة والتشغيل (% من CapEx سنويًا)", 0.0, 4.0, 1.0, 0.25) / 100.0
    project_lifetime = st.slider("العمر التحليلي للمشروع (سنة)", 10, 30, 25, 1)
    degradation_rate = st.slider("تدهور إنتاج الألواح (% سنويًا)", 0.1, 1.5, 0.5, 0.1) / 100.0
    discount_rate = st.slider("معدل الخصم المالي (%)", 0.0, 15.0, 5.0, 0.5) / 100.0
    optimistic_escalation = st.slider("ارتفاع التعرفة في السيناريو المتفائل (% سنويًا)", 0.0, 8.0, 3.0, 0.5) / 100.0

    st.markdown("**الاستبدال المحتمل للمعدات**")
    inverter_replacement_year = st.number_input(
        "سنة استبدال العاكس (0 = تعطيل)", min_value=0, max_value=30, value=12, step=1
    )
    inverter_replacement_pct = st.slider("تكلفة العاكس كنسبة من CapEx (%)", 0, 25, 8, 1) / 100.0
    battery_replacement_year = 0
    battery_replacement_pct = 0.0
    if system_type != "مربوط بالشبكة (On-Grid)":
        battery_replacement_year = st.number_input(
            "سنة استبدال البطارية (0 = تعطيل)", min_value=0, max_value=30, value=12, step=1
        )
        battery_replacement_pct = st.slider(
            "تكلفة الاستبدال كنسبة من تكلفة البطارية الأصلية (%)", 0, 100, 70, 5
        ) / 100.0


# -----------------------------------------------------------------------------
# Engineering sizing
# -----------------------------------------------------------------------------
annual_demand_kwh = monthly_kwh * 12.0
daily_demand_kwh = monthly_kwh / 30.0
annual_target_kwp = (
    annual_demand_kwh / (365.0 * psh * performance_ratio)
) * (coverage_pct / 100.0)
if system_type == "منفصل عن الشبكة (Off-Grid)":
    annual_target_kwp *= 1.0 + offgrid_margin_pct / 100.0

num_panels = max(1, math.ceil((annual_target_kwp * 1000.0) / panel_watt))
installed_kwp = num_panels * panel_watt / 1000.0
recommended_inverter_kw = installed_kwp / dc_ac_ratio
panel_surface_area = num_panels * panel_area
recommended_roof_area = panel_surface_area * (1.0 + roof_spacing_pct / 100.0)
annual_generation_kwh = installed_kwp * psh * 365.0 * performance_ratio
estimated_coverage_pct = (annual_generation_kwh / annual_demand_kwh * 100.0) if annual_demand_kwh > 0 else 0.0

if system_type != "مربوط بالشبكة (On-Grid)":
    battery_daily_deliverable_kwh = daily_demand_kwh * (battery_load_share_pct / 100.0) * autonomy_days
    battery_nominal_kwh = battery_daily_deliverable_kwh / max(battery_dod * battery_efficiency, 0.01)
else:
    battery_nominal_kwh = 0.0

pv_capex = installed_kwp * pv_cost_per_kw
battery_capex = battery_nominal_kwh * battery_cost_per_kwh
total_capex = pv_capex + battery_capex

# -----------------------------------------------------------------------------
# Economic analysis
# -----------------------------------------------------------------------------
vat_rate = vat_pct / 100.0
bill_results = estimate_first_year_bill_savings(
    monthly_load_kwh=monthly_kwh,
    annual_pv_kwh=annual_generation_kwh,
    system_type=system_type,
    self_consumption_pct=SELF_USE_DEFAULTS[system_type],
    export_rate=export_rate,
    low_rate=tariff_low,
    high_rate=tariff_high,
    tier_limit=tier_limit,
    vat_rate=vat_rate,
)

# Make self-consumption share editable in the sidebar for each system architecture.
# This control is separate from tariff/cost settings so its effect remains visible.
with st.sidebar.expander("⚡ نسبة الاستهلاك الذاتي من الإنتاج", expanded=True):
    self_consumption_pct = st.slider(
        "كمية الإنتاج الشمسي المستخدمة مباشرةً داخل المنشأة (%)",
        10,
        100,
        SELF_USE_DEFAULTS[system_type],
        5,
        key=f"self_consumption_{system_type}",
        help="تزداد عادةً مع الأحمال النهارية والبطاريات. هذا تقدير مبسط وليس تحليلًا ساعيًّا.",
    )

bill_results = estimate_first_year_bill_savings(
    monthly_load_kwh=monthly_kwh,
    annual_pv_kwh=annual_generation_kwh,
    system_type=system_type,
    self_consumption_pct=self_consumption_pct,
    export_rate=export_rate,
    low_rate=tariff_low,
    high_rate=tariff_high,
    tier_limit=tier_limit,
    vat_rate=vat_rate,
)
annual_savings_year1 = bill_results["annual_savings"]

common_scenario_args = {
    "capex": total_capex,
    "annual_savings_year1": annual_savings_year1,
    "annual_generation_kwh": annual_generation_kwh,
    "lifetime_years": project_lifetime,
    "degradation_rate": degradation_rate,
    "annual_om_rate": annual_om_pct,
    "inverter_replacement_year": int(inverter_replacement_year),
    "inverter_replacement_fraction": inverter_replacement_pct,
    "battery_capex": battery_capex,
    "battery_replacement_year": int(battery_replacement_year),
    "battery_replacement_fraction": battery_replacement_pct,
}

conservative_args = dict(common_scenario_args)
conservative_args["degradation_rate"] = min(degradation_rate * 1.3, 0.05)

scenarios = {
    "base": calculate_cashflow(**common_scenario_args, tariff_escalation=0.0),
    "optimistic": calculate_cashflow(
        **common_scenario_args, tariff_escalation=optimistic_escalation
    ),
    "conservative": calculate_cashflow(
        **conservative_args,
        tariff_escalation=0.0,
        scenario_multiplier=0.95,
    ),
}

base_df = scenarios["base"]["dataframe"]
base_cashflows = base_df["صافي التدفق النقدي (ريال)"].tolist()
base_cumulative = scenarios["base"]["cumulative"]
optimistic_cumulative = scenarios["optimistic"]["cumulative"]
conservative_cumulative = scenarios["conservative"]["cumulative"]
base_payback = payback_period(base_cumulative)
optimistic_payback = payback_period(optimistic_cumulative)
conservative_payback = payback_period(conservative_cumulative)
npv = net_present_value(base_cashflows, discount_rate)
lcoe = levelized_cost_of_energy(total_capex, base_df, discount_rate)
end_net_cashflow = float(base_cumulative[-1])
roi_pct = (end_net_cashflow / total_capex * 100.0) if total_capex > 0 else 0.0

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-kicker">PV STUDIO · RENEWABLE ENERGY ENGINEERING</div>
      <h1>المنصة الهندسية والاقتصادية لتصميم الأنظمة الكهروضوئية</h1>
      <p>أداة أولية لتحجيم الألواح والعاكس والبطاريات، وتقدير الإنتاج والتكلفة وجدوى المشروع اعتمادًا على مدخلات قابلة للتعديل.</p>
      <div class="hero-chips">
        <span class="hero-chip">📐 التحجيم الهندسي</span>
        <span class="hero-chip">💰 التحليل الاقتصادي</span>
        <span class="hero-chip">📈 السيناريوهات</span>
        <span class="hero-chip">🇸🇦 افتراضات للسعودية</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"تاريخ إعداد التقدير: {date.today().isoformat()} · نتائج نموذج أولي وليست عرض سعر أو اعتمادًا هندسيًا نهائيًا.")

# Top-line KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("قدرة الألواح المركبة", f"{installed_kwp:,.2f} kWp", f"{num_panels} لوح × {panel_watt} W")
kpi2.metric("الإنتاج السنوي المتوقع", f"{annual_generation_kwh:,.0f} kWh", f"تغطية طاقية نظرية {estimated_coverage_pct:.0f}%")
kpi3.metric("التكلفة الاستثمارية التقديرية", sar(total_capex), "تشمل البطاريات إن وُجدت")
kpi4.metric("التوفير الاقتصادي في السنة الأولى", sar(annual_savings_year1), "يشمل رصيد التصدير وفق المدخلات")

# -----------------------------------------------------------------------------
# Main tabs
# -----------------------------------------------------------------------------
tab_design, tab_economics, tab_scenarios, tab_report = st.tabs(
    ["📐 التصميم الهندسي", "💰 الجدوى الاقتصادية", "📈 مقارنة السيناريوهات", "📋 التقرير والمراجع"]
)

with tab_design:
    st.markdown("<div class='section-kicker'>ENGINEERING SUMMARY</div>", unsafe_allow_html=True)
    st.subheader("مخرجات التحجيم الهندسي")

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("قدرة النظام DC", f"{installed_kwp:.2f} kWp")
    d2.metric("قدرة العاكس AC المبدئية", f"{recommended_inverter_kw:.2f} kW")
    d3.metric("المساحة الموصى بها", f"{recommended_roof_area:,.1f} m²")
    if system_type == "مربوط بالشبكة (On-Grid)":
        d4.metric("سعة البطاريات", "لا يوجد")
    else:
        d4.metric("سعة البطاريات الاسمية", f"{battery_nominal_kwh:,.1f} kWh")

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown("#### الاستهلاك مقابل الإنتاج السنوي")
        st.plotly_chart(
            make_generation_chart(annual_demand_kwh, annual_generation_kwh),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with right:
        st.markdown("#### مواصفات المصفوفة المقترحة")
        st.markdown(
            f"""
            <div class="panel-card"><h4>☀️ الألواح الشمسية</h4>
            <p><b>{num_panels}</b> لوحًا بقدرة <b>{panel_watt} W</b> للوح، بإجمالي مركب <b>{installed_kwp:.2f} kWp</b>.</p></div>
            <div class="panel-card"><h4>🔌 العاكس</h4>
            <p>قدرة AC تقديرية <b>{recommended_inverter_kw:.2f} kW</b> على أساس نسبة DC/AC = <b>{dc_ac_ratio:.2f}</b>.</p></div>
            <div class="panel-card"><h4>📏 المساحة</h4>
            <p>مساحة الألواح الصافية <b>{panel_surface_area:.1f} m²</b>، والمساحة التخطيطية مع الممرات <b>{recommended_roof_area:.1f} m²</b>.</p></div>
            <div class="panel-card"><h4>⚙️ معامل الأداء المستخدم</h4>
            <p><b>{performance_ratio:.1%}</b> بعد احتساب كفاءة العاكس والفواقد الأخرى المدخلة.</p></div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### فحص مساحة السطح")
    if recommended_roof_area > available_area:
        st.error(
            f"المساحة المدخلة ({available_area:,.1f} m²) أقل من المساحة التخطيطية المقدرة ({recommended_roof_area:,.1f} m²). "
            "قد يلزم رفع المساحة المتاحة، أو إعادة توزيع الألواح، أو مراجعة قدرة اللوح وتخطيط السطح."
        )
    else:
        spare_area = available_area - recommended_roof_area
        st.success(
            f"المساحة المدخلة مناسبة مبدئيًا؛ المتبقي بعد تخصيص المساحة التخطيطية نحو {spare_area:,.1f} m². "
            "يجب تأكيد الظلال، اتجاه الألواح، ممرات الصيانة، والأحمال الإنشائية ميدانيًا."
        )

    if system_type == "منفصل عن الشبكة (Off-Grid)":
        st.warning(
            "تنبيه للنظام المستقل: قدرة العاكس يجب أن تُراجع وفق أقصى حمل متزامن وتيارات بدء المكيفات والمضخات، "
            "كما ينبغي تنفيذ محاكاة زمنية للطاقة والبطاريات ومصدر احتياطي قبل التصميم النهائي."
        )
    elif system_type == "هجين مع تخزين بطاريات (Hybrid)":
        st.info(
            "في النظام الهجين، حُسبت البطارية لتغطية النسبة ومدة الاستقلالية المدخلتين فقط؛ "
            "وليس بالضرورة أن تغطي كامل أحمال المنزل أثناء انقطاع طويل."
        )

with tab_economics:
    st.markdown("<div class='section-kicker'>FINANCIAL MODEL</div>", unsafe_allow_html=True)
    st.subheader("المؤشرات الاقتصادية للمشروع")

    e1, e2, e3, e4, e5 = st.columns(5)
    e1.metric("التكلفة الرأسمالية", sar(total_capex))
    e2.metric("فترة الاسترداد", f"{base_payback:.1f} سنة" if base_payback is not None else f"أكثر من {project_lifetime} سنة")
    e3.metric("صافي القيمة الحالية NPV", sar(npv))
    e4.metric("تكلفة الطاقة LCOE", f"{lcoe:.3f} ريال/kWh")
    e5.metric("صافي العائد خلال العمر", sar(end_net_cashflow), f"ROI تقديري {roi_pct:.1f}%")

    st.markdown("#### توزيع التكلفة الاستثمارية")
    cost1, cost2, cost3 = st.columns(3)
    cost1.metric("النظام الشمسي دون التخزين", sar(pv_capex))
    cost2.metric("بنك البطاريات", sar(battery_capex))
    cost3.metric("تكاليف الصيانة السنوية المقدرة", sar(total_capex * annual_om_pct))

    bill1, bill2, bill3 = st.columns(3)
    bill1.metric("الفاتورة السنوية قبل النظام", sar(bill_results["baseline_annual_bill"]))
    bill2.metric("الفاتورة السنوية بعد النظام", sar(bill_results["post_solar_annual_bill"]))
    bill3.metric("الطاقة المصدّرة المقدرة", f"{bill_results['exported_kwh']:,.0f} kWh/سنة")

    st.markdown("#### التدفق النقدي التراكمي على مدى عمر المشروع")
    st.plotly_chart(
        make_cumulative_chart(scenarios),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    st.caption(
        "يخصم النموذج تكاليف الصيانة والاستبدال التي أدخلتها. لا يشمل التمويل البنكي، أو قيمة متبقية للمعدات، "
        "أو الرسوم الثابتة للعداد، أو تكلفة مولد وقود للنظام المستقل."
    )

with tab_scenarios:
    st.markdown("<div class='section-kicker'>SCENARIO ANALYSIS</div>", unsafe_allow_html=True)
    st.subheader("مقارنة الافتراضات المستقبلية")
    ten_year_index = min(10, project_lifetime)

    def scenario_summary(label: str, scenario_key: str, payback: float | None, scenario_df: pd.DataFrame) -> dict[str, Any]:
        cumulative_values = scenarios[scenario_key]["cumulative"]
        end_value = float(cumulative_values[-1])
        value_after_10 = float(cumulative_values[ten_year_index])
        return {
            "السيناريو": label,
            "فترة الاسترداد": f"{payback:.1f} سنة" if payback is not None else f"أكثر من {project_lifetime} سنة",
            f"التدفق التراكمي عند السنة {ten_year_index}": sar(value_after_10),
            "صافي التدفق التراكمي بنهاية العمر": sar(end_value),
            "صافي القيمة الحالية NPV": sar(
                net_present_value(scenario_df["صافي التدفق النقدي (ريال)"].tolist(), discount_rate)
            ),
        }

    scenario_table = pd.DataFrame(
        [
            scenario_summary("المتحفظ", "conservative", conservative_payback, scenarios["conservative"]["dataframe"]),
            scenario_summary("الأساسي", "base", base_payback, scenarios["base"]["dataframe"]),
            scenario_summary("المتفائل", "optimistic", optimistic_payback, scenarios["optimistic"]["dataframe"]),
        ]
    )
    st.dataframe(scenario_table, use_container_width=True, hide_index=True)

    st.markdown("#### كيف تختلف السيناريوهات؟")
    st.markdown(
        """
        <div class="panel-card"><h4>🟢 السيناريو الأساسي</h4>
        <p>لا يفترض ارتفاعًا سنويًا في تعرفة الكهرباء، ويستخدم معدل تدهور الألواح المدخل.</p></div>
        <div class="panel-card"><h4>🟠 السيناريو المتفائل</h4>
        <p>يفترض ارتفاع تعرفة الكهرباء سنويًا بالنسبة المحددة في الشريط الجانبي، ما قد يرفع قيمة الطاقة التي يوفرها النظام.</p></div>
        <div class="panel-card"><h4>⚪ السيناريو المتحفظ</h4>
        <p>يخفض منفعة السنة الأولى بنسبة 5% ويفترض تدهورًا أسرع للألواح بنسبة 30% مقارنة بالإعداد الأساسي.</p></div>
        """,
        unsafe_allow_html=True,
    )

with tab_report:
    st.markdown("<div class='section-kicker'>PROJECT REPORT</div>", unsafe_allow_html=True)
    st.subheader("ملخص التقرير الفني والاقتصادي")
    battery_description = (
        f"بطارية اسمية {battery_nominal_kwh:.1f} kWh، تغطية {battery_load_share_pct}% من استهلاك اليوم لمدة {autonomy_days:.2f} يوم"
        if system_type != "مربوط بالشبكة (On-Grid)"
        else "لا توجد بطاريات في هذا السيناريو"
    )

    report_markdown = f"""# تقرير أولي لتصميم نظام كهروضوئي

- **تاريخ التقدير:** {date.today().isoformat()}
- **المنشأة:** {facility_type}
- **الموقع:** {city}
- **هيكلية النظام:** {system_type}

## 1. مدخلات التصميم
- متوسط الاستهلاك الشهري: {monthly_kwh:,.0f} kWh
- الاستهلاك السنوي: {annual_demand_kwh:,.0f} kWh
- ساعات الذروة الشمسية المكافئة المفترضة: {psh:.2f} ساعة/يوم
- كفاءة العاكس: {inverter_eff:.1%}
- الفواقد الأخرى: {other_losses:.1%}
- معامل الأداء المستخدم: {performance_ratio:.1%}
- هدف التغطية: {coverage_pct}%

## 2. النتائج الهندسية
- قدرة الألواح المركبة: {installed_kwp:.2f} kWp
- عدد الألواح: {num_panels} لوحًا بقدرة {panel_watt} W
- مساحة الألواح الصافية: {panel_surface_area:.1f} m²
- مساحة السطح التخطيطية مع الممرات: {recommended_roof_area:.1f} m²
- قدرة العاكس AC التقديرية: {recommended_inverter_kw:.2f} kW
- إنتاج السنة الأولى المتوقع: {annual_generation_kwh:,.0f} kWh
- نسبة الإنتاج السنوي إلى الاستهلاك السنوي: {estimated_coverage_pct:.1f}%
- التخزين: {battery_description}

## 3. النتائج الاقتصادية
- تكلفة النظام دون البطاريات: {pv_capex:,.0f} ريال
- تكلفة البطاريات: {battery_capex:,.0f} ريال
- إجمالي التكلفة الرأسمالية: {total_capex:,.0f} ريال
- الفاتورة السنوية التقديرية قبل النظام: {bill_results['baseline_annual_bill']:,.0f} ريال
- الفاتورة السنوية التقديرية بعد النظام: {bill_results['post_solar_annual_bill']:,.0f} ريال
- المنفعة الاقتصادية للسنة الأولى: {annual_savings_year1:,.0f} ريال
- فترة الاسترداد الأساسية: {f'{base_payback:.1f} سنة' if base_payback is not None else f'أكثر من {project_lifetime} سنة'}
- صافي القيمة الحالية NPV: {npv:,.0f} ريال
- تكلفة الطاقة المستوية LCOE: {lcoe:.3f} ريال/kWh
- صافي التدفق التراكمي بنهاية العمر: {end_net_cashflow:,.0f} ريال

## 4. حدود النموذج
هذه أداة تقدير أولي تعتمد على متوسط استهلاك وإنتاج شهريين، وليست محاكاة ساعية أو دراسة موقع تفصيلية. لا تحسب الظلال الفعلية، أو تباين الإشعاع على مدار أشهر السنة، أو أحمال الذروة وتيارات بدء المحركات، أو عدم تلبية الأحمال، أو أعطال المعدات. كما أن تعرفة تصدير الفائض وتكاليف التنفيذ الفعلية يجب التحقق منها من مزود الخدمة والمقاول. لا يُعتمد التصميم للتنفيذ قبل مراجعة مهندس مختص والاشتراطات المحلية.
"""

    st.markdown(
        f"""
        <div class="panel-card">
          <h4>☀️ {facility_type} · {city}</h4>
          <p>نظام {system_type} بقدرة <b>{installed_kwp:.2f} kWp</b>، إنتاج سنوي مقدر <b>{annual_generation_kwh:,.0f} kWh</b>، وتكلفة إجمالية تقديرية <b>{total_capex:,.0f} ريال</b>.</p>
          <div class="divider"></div>
          <p>فترة الاسترداد الأساسية: <b>{f'{base_payback:.1f} سنة' if base_payback is not None else f'أكثر من {project_lifetime} سنة'}</b> · LCOE: <b>{lcoe:.3f} ريال/kWh</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button(
        "⬇️ تنزيل التقرير الفني والاقتصادي (Markdown)",
        data=report_markdown.encode("utf-8-sig"),
        file_name="solar_pv_report_ar.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.download_button(
        "⬇️ تنزيل التدفقات النقدية (CSV)",
        data=base_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="solar_pv_cashflows_ar.csv",
        mime="text/csv",
        use_container_width=True,
    )

    with st.expander("📚 المراجع والافتراضات", expanded=False):
        st.markdown(
            """
            **مصادر يمكن الرجوع إليها عند تطوير النموذج:**
            - [دليل خدمات الكهرباء – الهيئة السعودية لتنظيم الكهرباء (SERA)](https://sera.gov.sa/-/media/4a51a8ff4b5a45609033cfb7fea9d644.ashx): مرجع لقيم تعرفة الكهرباء الافتراضية المستخدمة في النموذج. يجب مراجعة التعرفة الخاصة بالحساب الفعلي، خصوصًا القطاع الصناعي.
            - [دراسة الجدوى الفنية والاقتصادية لنظام كهروضوئي على سطح في السعودية – Energies (2024)](https://www.mdpi.com/1996-1073/17/10/2325): مرجع أكاديمي يتضمن افتراضًا لتكلفة نظام مربوط بالشبكة قدره نحو 3.8 ريال/Wp في حالة الدراسة؛ الرقم هنا نقطة بدء تقديرية وليس عرض سعر حاليًا.
            - [Global Solar Atlas](https://globalsolaratlas.info/) و[PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/): للتحقق من مورد الطاقة الشمسية حسب إحداثيات الموقع وميل الألواح.

            **ملاحظات:** قيم ساعات الذروة الشمسية وتكاليف الأنظمة والبطاريات في التطبيق افتراضات قابلة للتعديل. نموذج الفاتورة لا يشمل الرسوم الثابتة، ونموذج الإنتاج لا يحاكي الطقس ساعة بساعة. يجب التأكد من شروط الربط وتعويض الطاقة المصدّرة قبل بناء قرار استثماري.
            """
        )

# Footer
st.markdown(
    """
    <div style="margin-top:1.5rem; padding-top:1rem; border-top:1px solid #E2E8F0; color:#64748B; font-size:0.82rem; text-align:center;">
      PV Studio · نموذج أولي لمشروع تخرج في هندسة الطاقة المتجددة · جميع المخرجات تقديرية وتحتاج إلى تحقق هندسي وميداني.
    </div>
    """,
    unsafe_allow_html=True,
)
