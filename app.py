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
st.write("أداة هندسية واقتصادية لحساب الاحتياجات الفعلية وفترة استرداد رأس المال للمنازل والمزارع.")

st.markdown("---")

# القائمة الجانبية لإدخال البيانات
st.sidebar.header("📥 إدخال البيانات التشغيلية")

facility_type = st.sidebar.selectbox(
    "نوع المنشأة",
    ["سكني (منزل / فيلا)", "زراعي (مزرعة)", "تجاري"]
)

system_type = st.sidebar.selectbox(
    "نوع النظام الشمسي",
    ["مربوط بالشبكة (On-Grid)", "هجين مع بطاريات (Hybrid)"]
)

# تعديل القيم الافتراضية لتكون واقعية حسب المنشأة
default_kwh = 1500 if facility_type == "سكني (منزل / فيلا)" else 8000

monthly_kwh = st.sidebar.number_input(
    "متوسط الاستهلاك الشهري (كيلوواط ساعة - kWh)", 
    min_value=200, 
    value=default_kwh, 
    step=100,
    help="يمكن معرفة هذا الرقم من إفادة الاستهلاك في فاتورة الكهرباء الشهرية."
)

available_area = st.sidebar.number_input("المساحة المتاحة للتركيب (متر مربع m²)", min_value=20, value=120, step=10)

# --- الثوابت الهندسية والاقتصادية الواقعية ---
PEAK_SUN_HOURS = 5.8       # متوسط ساعات الذروة الشمسية (مناسب لبيئة المملكة)
PANEL_WATTAGE = 550        # قدرة اللوح الواحد (واط)
PANEL_AREA = 2.6           # مساحة اللوح الواحد (متر مربع)
SYSTEM_LOSSES = 0.18       # نسبة الفاقد في النظام (18% كفاءة أسلاك ومحول وغبار)

# تكلفة الكيلوواط بالسوق المحلي (ريال سعودي شامل التركيب والمولدات)
COST_PER_KW_ONGRID = 2800  
COST_PER_KW_HYBRID = 4500  

# متوسط سعر الكيلوواط ساعة للشرائح المستهدفة (تقريبي لتبسيط الحساب المالي)
TARIFF_RATE = 0.22 if facility_type == "سكني (منزل / فيلا)" else 0.30

# --- الحسابات الهندسية الدقيقة ---
daily_kwh = monthly_kwh / 30.0
# حساب القدرة المطلوبة بالـ kWp
required_kw_dc = (daily_kwh / PEAK_SUN_HOURS) / (1 - SYSTEM_LOSSES)

# عدد الألواح والمساحة المطلوبة
num_panels = int(np.ceil((required_kw_dc * 1000) / PANEL_WATTAGE))
required_area = num_panels * PANEL_AREA

# قدرة المحول (Inverter Size) - يفضل أن تطابق قدرة الألواح أو أقل بقليل بنسبة بسيطة
inverter_kw = round(required_kw_dc, 2)

# سعة البطارية (إذا كان النظام هجين - تغطي تقريباً 40% من الاستهلاك اليومي للطوارئ)
battery_kwh = round(daily_kwh * 0.4, 2) if system_type == "هجين مع بطاريات (Hybrid)" else 0

# --- الحسابات الاقتصادية ---
monthly_bill = monthly_kwh * TARIFF_RATE
annual_bill = monthly_bill * 12

cost_per_kw = COST_PER_KW_HYBRID if system_type == "هجين مع بطاريات (Hybrid)" else COST_PER_KW_ONGRID
total_system_cost = required_kw_dc * cost_per_kw

# افتراض أن الطاقة الشمسية ستوفر 85% من إجمالي الفاتورة السنوية
annual_savings = annual_bill * 0.85
payback_period = total_system_cost / annual_savings if annual_savings > 0 else 0

# --- عرض النتائج الهندسية ---
st.subheader("📊 النتائج والتوصيات الهندسية")

col1, col2, col3, col4 = st.columns(4)

col1.metric(label="قدرة النظام المطلوبة", value=f"{required_kw_dc:.1f} kWp")
col2.metric(label="عدد الألواح (550W)", value=f"{num_panels} لوح")
col3.metric(label="قدرة المحول (Inverter)", value=f"{inverter_kw} kW")
if system_type == "هجين مع بطاريات (Hybrid)":
    col4.metric(label="سعة البطاريات المقترحة", value=f"{battery_kwh:,.1f} kWh")
else:
    col4.metric(label="المساحة المطلوبة للألواح", value=f"{required_area:.1f} m²")

st.markdown("---")

# --- عرض النتائج الاقتصادية ---
st.subheader("💰 التحليل الاقتصادي وجدوى الاستثمار")

ec1, ec2, ec3 = st.columns(3)

ec1.metric(label="التكلفة التقديرية للنظام", value=f"{total_system_cost:,.0f} ريال")
ec2.metric(label="التوفير السنوي المتوقع", value=f"{annual_savings:,.0f} ريال")
ec3.metric(label="فترة استرداد رأس المال", value=f"{payback_period:.1f} سنة")

# التحقق من ملاءمة المساحة
st.markdown("### ⚠️ تقييم ملائمة الموقع:")
if required_area > available_area:
    st.error(f"المساحة المتاحة ({available_area} m²) غير كافية! المساحة المطلوبة الفعلية هي ({required_area:.1f} m²). يرجى تقليص حجم النظام أو توفير مساحة إضافية.")
else:
    st.success(f"المساحة المتاحة ({available_area} m²) ممتازة وكافية لتغطية الألواح المطلوبة ({required_area:.1f} m²).")

# رسم بياني توضيحي لاسترداد رأس المال عبر السنوات
st.markdown("### 📈 مسار استرداد الاستثمار وصافي التدفق المالي عبر 10 سنوات")
years = list(range(0, 11))
cumulative_savings = [-total_system_cost + (annual_savings * y) for y in years]

chart_data = pd.DataFrame({
    'السنة': years,
    'صافي التدفق المالي (ريال)': cumulative_savings
})

st.line_chart(chart_data.set_index('السنة'))
