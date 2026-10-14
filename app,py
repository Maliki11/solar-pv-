import streamlit as st
import pandas as pd
import numpy as np

# إعدادات الصفحة
st.set_page_config(
    page_title="حاسبة جدوى الأنظمة الشمسية",
    page_icon="☀️",
    layout="wide"
)

# عنوان التطبيق
st.title("☀️ حاسبة جدوى وتحجم الأنظمة الشمسية الكهروضوئية")
st.write("أداة متخصصة لحساب الاحتياجات الهندسية والجدوى الاقتصادية للتحول للطاقة الشمسية.")

st.markdown("---")

# القائمة الجانبية لإدخال البيانات
st.sidebar.header("📥 إدخال البيانات الرئيسية")

type_option = st.sidebar.selectbox(
    "نوع المنشأة",
    ["سكني (منزل / فيلا)", "زراعي (مزرعة)", "تجاري"]
)

system_type = st.sidebar.selectbox(
    "نوع النظام الشمسي",
    ["مربوط بالشبكة (On-Grid)", "هجين مع بطاريات (Hybrid)"]
)

bill_input_type = st.sidebar.radio(
    "طريقة تحديد الاستهلاك",
    ["متوسط قيمة الفاتورة الشهرية (ريال)", "متوسط الاستهلاك الشهري (كيلوواط ساعة - kWh)"]
)

if bill_input_type == "متوسط قيمة الفاتورة الشهرية (ريال)":
    monthly_cost = st.sidebar.number_input("أدخل قيمة الفاتورة الشهرية المتوسطة (ريال)", min_value=100, value=1500, step=100)
    # حساب تقريبي للاستهلاك بناءً على شريحة 0.18 ريال/ك.و.س
    monthly_kwh = monthly_cost / 0.18
else:
    monthly_kwh = st.sidebar.number_input("أدخل الاستهلاك الشهري (kWh)", min_value=500, value=8000, step=500)
    monthly_cost = monthly_kwh * 0.18

available_area = st.sidebar.number_input("المساحة المتاحة للتركيب (متر مربع m²)", min_value=10, value=150, step=10)

# ثوابت هندسية لحساب النظام
PEAK_SUN_HOURS = 5.5 # متوسط ساعات الذروة الشمسية
PANEL_WATTAGE = 550  # قدرة اللوح الواحد (واط)
PANEL_AREA = 2.58    # مساحة اللوح الواحد (متر مربع)
SYSTEM_LOSSES = 0.20 # نسبة الفاقد في النظام (20%)
COST_PER_KW_ONGRID = 3500 # تكلفة الكيلوواط المربوط بالشبكة (تقريبي بالريال)
COST_PER_KW_HYBRID = 5500 # تكلفة الكيلوواط للهجين شامل البطاريات

# --- الحسابات الهندسية ---
daily_kwh = monthly_kwh / 30.0
required_kw_dc = (daily_kwh / PEAK_SUN_HOURS) / (1 - SYSTEM_LOSSES)

# عدد الألواح والمساحة المطلوبة
num_panels = int(np.ceil((required_kw_dc * 1000) / PANEL_WATTAGE))
required_area = num_panels * PANEL_AREA

# قدرة المحول (Inverter Size)
inverter_kw = round(required_kw_dc * 0.9, 2)

# سعة البطارية (إذا كان النظام هجين)
battery_kwh = round(daily_kwh * 0.5, 2) if system_type == "هجين مع بطاريات (Hybrid)" else 0

# --- الحسابات الاقتصادية ---
cost_per_kw = COST_PER_KW_HYBRID if system_type == "هجين مع بطاريات (Hybrid)" else COST_PER_KW_ONGRID
total_system_cost = required_kw_dc * cost_per_kw

annual_savings = monthly_cost * 12 * 0.85 # افتراض توفير 85% من الفاتورة
payback_period = total_system_cost / annual_savings if annual_savings > 0 else 0

# --- عرض النتائج ---
st.subheader("📊 النتائج والتوصيات الهندسية")

col1, col2, col3, col4 = st.columns(4)

col1.metric(label="قدرة النظام المطلوبة", value=f"{required_kw_dc:.2f} kWp")
col2.metric(label="عدد الألواح (550W)", value=f"{num_panels} لوح")
col3.metric(label="قدرة المحول (Inverter)", value=f"{inverter_kw} kW")
if system_type == "هجين مع بطاريات (Hybrid)":
    col4.metric(label="سعة البطاريات المقترحة", value=f"{battery_kwh} kWh")
else:
    col4.metric(label="المساحة المطلوبة", value=f"{required_area:.1f} m²")

st.markdown("---")

st.subheader("💰 التحليل الاقتصادي وجدوى الاستثمار")

ec1, ec2, ec3 = st.columns(3)

ec1.metric(label="التكلفة التقديرية للنظام", value=f"{total_system_cost:,.0f} ريال")
ec2.metric(label="التوفير السنوي المتوقع", value=f"{annual_savings:,.0f} ريال")
ec3.metric(label="فترة استرداد رأس المال", value=f"{payback_period:.1f} سنة")

# التحقق من ملاءمة المساحة
st.markdown("### ⚠️ تقييم ملائمة الموقع:")
if required_area > available_area:
    st.error(f"المساحة المتاحة ({available_area} m²) غير كافية! المساحة المطلوبة الفعلية هي ({required_area:.1f} m²). ننصح بتخفيض حجم النظام أو توفير مساحة إضافية.")
else:
    st.success(f"المساحة المتاحة ({available_area} m²) كافية تماماً لتغطية الألواح الشمسية المطلوبة ({required_area:.1f} m²).")

# رسم بياني توضيحي لاسترداد رأس المال عبر السنوات
st.markdown("### 📈 مسار استرداد الاستثمار عبر 10 سنوات")
years = list(range(0, 11))
cumulative_savings = [-total_system_cost + (annual_savings * y) for y in years]
chart_data = pd.DataFrame({
    'السنة': years,
    'صافي التدفق المالي (ريال)': cumulative_savings
})

st.line_chart(chart_data.set_index('السنة'))
