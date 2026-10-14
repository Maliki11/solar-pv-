import streamlit as st
import pandas as pd
import numpy as np

# إعدادات الصفحة الاحترافية
st.set_page_config(
    page_title="منصة التصميم الذكي للأنظمة الشمسية",
    page_icon="☀️",
    layout="wide"
)

# تخصيص واجهة العنوان
st.title("☀️ المنصة الهندسية والاقتصادية لتصميم وتقييم الأنظمة الكهروضوئية")
st.markdown("---")

# --- الشريط الجانبي لإدخال المعاملات ---
st.sidebar.header("⚙️ مدخلات المشروع والبيانات التشغيلية")

facility_type = st.sidebar.selectbox(
    "نوع المنشأة المستهدفة",
    ["سكني (منزل / فيلا)", "زراعي (مزرعة وبئر)", "تجاري / صناعي"]
)

city = st.sidebar.selectbox(
    "المدينة / الموقع الجغرافي",
    ["حائل", "الرياض", "جدة / مكة المكرمة", "الدمام / الشرقية", "أبها / الجنوب", "تبوك"]
)

system_type = st.sidebar.selectbox(
    "هيكلية النظام الشمسي",
    ["مربوط بالشبكة (On-Grid)", "هجين مع تخزين بطاريات (Hybrid)", "منفصل تماماً (Off-Grid)"]
)

st.sidebar.markdown("### 📊 بيانات الاستهلاك")
monthly_kwh = st.sidebar.number_input(
    "متوسط الاستهلاك الشهري (kWh)", 
    min_value=300, 
    value=2500 if facility_type != "زراعي (منزل / فيلا)" else 8000, 
    step=200
)

available_area = st.sidebar.number_input(
    "المساحة المتاحة للتركيب (m²)", 
    min_value=30, 
    value=200, 
    step=10
)

# إعدادات متقدمة قابلة للطي في القائمة الجانبية
with st.sidebar.expander("🛠️ المعاملات الهندسية المتقدمة"):
    panel_watt = st.selectbox("قدرة اللوح الشمسي (Watt)", [550, 580, 600], index=0)
    inverter_eff = st.slider("كفاءة المحول (Inverter Efficiency %)", 90, 98, 96) / 100.0
    temp_loss_factor = st.slider("معامل الفاقد الحراري والغبار (%)", 10, 30, 18) / 100.0
    battery_dod = st.slider("عمق تفريغ البطاريات (DOD % - للأنظمة الهجينة)", 50, 95, 80) / 100.0

with st.sidebar.expander("💵 المعاملات المالية والاقتصادية"):
    project_lifetime = st.slider("عمر المشروع الافتراضي (سنوات)", 15, 30, 25)
    degradation_rate = st.slider("معدل التدهور السنوي للألواح (% سنوياً)", 0.3, 1.0, 0.5) / 100.0
    discount_rate = st.slider("معدل الخصم المالي (Discount Rate %)", 3.0, 10.0, 5.0) / 100.0

# --- قواعد البيانات الجغرافية (ساعات الذروة الشمسية لكل مدينة) ---
psh_dict = {
    "حائل": 5.85,
    "الرياض": 6.10,
    "جدة / مكة المكرمة": 6.25,
    "الدمام / الشرقية": 5.95,
    "أبها / الجنوب": 6.40,
    "تبوك": 6.00
}
peak_sun_hours = psh_dict[city]

# تعيين تعريفة الكهرباء الافتراضية حسب نوع المنشأة (ريال / kWh)
tariff_rates = {
    "سكني (منزل / فيلا)": 0.22,
    "زراعي (منزل / فيلا)": 0.25,
    "تجاري / صناعي": 0.32
}
base_tariff = tariff_rates[facility_type]

# --- الحسابات الهندسية الدقيقة ---
daily_kwh = monthly_kwh / 30.0
# حساب القدرة المطلوبة بالـ kWp مع الأخذ في الاعتبار كفاءة المحول ومعامل الفاقد
required_kw_dc = (daily_kwh / peak_sun_hours) / ((1 - temp_loss_factor) * inverter_eff)

panel_area_m2 = 2.6 if panel_watt >= 580 else 2.58
num_panels = int(np.ceil((required_kw_dc * 1000) / panel_watt))
required_area = num_panels * panel_area_m2

inverter_kw = round(required_kw_dc * 1.05, 2) # هامش أمان 5% للمحول

# سعة البطاريات (إذا كان النظام هجين أو منفصل)
daily_backup_kwh = daily_kwh * 0.6 if system_type != "مربوط بالشبكة (On-Grid)" else 0
battery_bank_kwh = round(daily_backup_kwh / battery_dod, 2) if daily_backup_kwh > 0 else 0

# --- التكاليف الرأسمالية (CapEx) ---
cost_per_kw = 2600 if system_type == "مربوط بالشبكة (On-Grid)" else (4200 if system_type == "هجين مع تخزين بطاريات (Hybrid)" else 5500)
total_system_cost = required_kw_dc * cost_per_kw

# --- التحليل الاقتصادي عبر عمر المشروع ---
annual_consumption_cost = monthly_kwh * base_tariff * 12
annual_generation_kwh = required_kw_dc * peak_sun_hours * 365 * (1 - temp_loss_factor)

# حساب التدفقات النقدية والسيناريوهات الاحتمالية على مدار عمر المشروع
years = list(range(1, project_lifetime + 1))
cash_flows_base = []
cash_flows_optimistic = [] # سيناريو ارتفاع أسعار الكهرباء بنسبة 3% سنوياً
cash_flows_conservative = [] # سيناريو تدهور أسرع

cumulative_base = -total_system_cost
cumulative_opt = -total_system_cost
cumulative_cons = -total_system_cost
base_cumulative_list = [-total_system_cost]
opt_cumulative_list = [-total_system_cost]
cons_cumulative_list = [-total_system_cost]

annual_savings_year1 = min(annual_generation_kwh * base_tariff, annual_consumption_cost * 0.90)

for y in years:
    # السيناريو الأساسي
    deg_factor = (1 - degradation_rate) ** (y - 1)
    savings_base = annual_savings_year1 * deg_factor
    cumulative_base += savings_base
    base_cumulative_list.append(cumulative_base)
    
    # السيناريو المتفائل (ارتفاع تعريفة الكهرباء 3% سنوياً)
    tariff_opt = base_tariff * ((1.03) ** (y - 1))
    savings_opt = min(annual_generation_kwh * deg_factor * tariff_opt, annual_consumption_cost * 1.03**(y-1) * 0.90)
    cumulative_opt += savings_opt
    opt_cumulative_list.append(cumulative_opt)
    
    # السيناريو المتحفظ
    deg_cons = (1 - (degradation_rate * 1.3)) ** (y - 1)
    savings_cons = annual_savings_year1 * deg_cons * 0.95
    cumulative_cons += savings_cons
    cons_cumulative_list.append(cumulative_cons)

# حساب فترة استرداد رأس المال (Payback Period) للسيناريو الأساسي
payback_period = total_system_cost / annual_savings_year1 if annual_savings_year1 > 0 else 99

# حساب LCOE (تكلفة الطاقة المستوية - ريال / kWh)
total_lifetime_generation = sum([annual_generation_kwh * ((1 - degradation_rate) ** (y - 1)) for y in years])
total_lifecycle_cost = total_system_cost + (total_system_cost * 0.15) # افتراض تكاليف صيانة وتشغيل 15% على مدار العمر
lcoe = total_lifecycle_cost / total_lifetime_generation if total_lifetime_generation > 0 else 0

# --- تنظيم العرض في تبويبات احترافية (Tabs) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📐 التصميم والتجزيء الهندسي", 
    "💰 الجدوى الاقتصادية وتحليل LCOE", 
    "📈 مقارنة السيناريوهات الاحتمالية",
    "📋 التقرير الفني الشامل"
])

with tab1:
    st.subheader("🛠️ المواصفات الفنية ومخرجات التحجيم الهندسي")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("القدرة الذروية المطلوبة", f"{required_kw_dc:.2f} kWp")
    col2.metric(label=f"عدد الألواح ({panel_watt}W)", value=f"{num_panels} لوح")
    col3.metric("قدرة المحول المقترحة", f"{inverter_kw} kW")
    if system_type != "مربوط بالشبكة (On-Grid)":
        col4.metric("سعة بنك البطاريات", f"{battery_bank_kwh:,.1f} kWh")
    else:
        col4.metric("المساحة اللازمة للألواح", f"{required_area:.1f} m²")
        
    st.markdown("---")
    
    # تقييم الملاءمة المساحية
    if required_area > available_area:
        st.error(f"⚠️ تحذير هندسي: المساحة المتاحة ({available_area} m²) أصغر من المساحة المطلوبة فعلياً للألواح ({required_area:.1f} m²). يُنصح باستخدام ألواح ذات قدرة أعلى (600W) أو تقليل حجم النظام.")
    else:
        st.success(f"✅ المساحة المتاحة ({available_area} m²) كافية تماماً وتغطي المساحة المطلوبة للألواح ({required_area:.1f} m²) بنجاح.")
        
    st.info(f"📍 معلومات الموقع: المدينة المختارة ({city}) تتميز بمتوسط ساعات ذروة شمسية سنوي يبلغ {peak_sun_hours} ساعة/يوم، مما يعزز كفاءة الإنتاجية السنوية المقدرة بحوالي {annual_generation_kwh:,.0f} kWh/سنة.")

with tab2:
    st.subheader("💵 مؤشرات الجدوى الاقتصادية والمالية")
    
    ec1, ec2, ec3, ec4 = st.columns(4)
    ec1.metric("إجمالي التكلفة الاستثمارية (CapEx)", f"{total_system_cost:,.0f} ريال")
    ec2.metric("التوفير السنوي في السنة الأولى", f"{annual_savings_year1:,.0f} ريال")
    ec3.metric("فترة استرداد رأس المال", f"{payback_period:.1f} سنة")
    ec4.metric("تكلفة الطاقة المستوية (LCOE)", f"{lcoe:.3f} ريال/kWh")
    
    st.markdown("---")
    st.markdown("### 📉 منحنى التدفق النقدي التراكمي على مدى 25 عاماً")
    
    chart_df = pd.DataFrame({
        'السنة': list(range(0, project_lifetime + 1)),
        'السيناريو الأساسي (ريال)': base_cumulative_list,
        'السيناريو المتفائل (ارتفاع الكهرباء)': opt_cumulative_list,
        'السيناريو المتحفظ': cons_cumulative_list
    }).set_index('السنة')
    
    st.line_chart(chart_df)
with tab3:
    st.subheader("📊 تحليل السيناريوهات الاحتمالية (Scenario Analysis)")
    st.write("يقارن هذا القسم أداء الاستثمار تحت تأثير متغيرات السوق المستقبلية (تغير أسعار الكهرباء، معدلات التدهور، وتكاليف الصيانة).")
    
    # جدول مقارنة السيناريوهات
    scenarios_data = {
        "مؤشر المقارنة": ["فترة الاسترداد", "صافي العائد بعد 10 سنوات", "إجمالي التوفير بنهاية المشروع"],
        "السيناريو المتحفظ (Conservative)": [f"{payback_period*1.2:.1f} سنة", f"{base_cumulative_list[10]*0.85:,.0f} ريال", f"{base_cumulative_list[-1]*0.80:,.0f} ريال"],
        "السيناريو الأساسي (Expected)": [f"{payback_period:.1f} سنة", f"{base_cumulative_list[10]:,.0f} ريال", f"{base_cumulative_list[-1]:,.0f} ريال"],
        "السيناريو المتفائل (Optimistic)": [f"{payback_period*0.85:.1f} سنة", f"{opt_cumulative_list[10]:,.0f} ريال", f"{opt_cumulative_list[-1]:,.0f} ريال"]
    }
    st.table(pd.DataFrame(scenarios_data))

with tab4:
    st.subheader("📋 ملخص التقرير الفني والاقتصادي للمشروع")
    st.markdown(f"""
    * اسم المشروع: تصميم وتطوير نظام طاقة شمسية كهروضوئية ({system_type})
    * المنشأة المستهدفة: {facility_type} في مدينة {city}.
    * الحجم الإجمالي للنظام: {required_kw_dc:.2f} kWp باستخدام عدد {num_panels} لوح شمسي من فئة {panel_watt}W.
    * القدرة التحويلية والتخزينية: محول بقدرة {inverter_kw} kW {'وبنك بطاريات بسعة ' + str(battery_bank_kwh) + ' kWh' if system_type != 'مربوط بالشبكة (On-Grid)' else 'نظام متصل مباشر بالشبكة بدون تخزين'}.
    *  الجدوى المالية: التكلفة التقديرية {total_system_cost:,.0f} ريال مع فترة استرداد رأس مال تبلغ **{payback_period:.1f} سنة** وتكلفة إنتاج للطاقة **{lcoe:.3f} ريال لكل كيلوواط ساعة**.
    """)
    
    st.success("✨ هذا التقرير مصمم خصيصاً لمشاريع تخرج هندسة الطاقة المتجددة، ويمكن اعتماده كنموذج أولي متكامل لعرضه أمام لجنة المناقشة الأكاديمية.")
