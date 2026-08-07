import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter
import io
import plotly.express as px

st.set_page_config(page_title="نظام معالجة وإدارة خطط الأونلاين", layout="wide")

def process_plan_and_stock(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    
    plan_sheet = None
    stock_sheet = None
    
    for sheet in sheet_names:
        sheet_lower = sheet.lower()
        if 'plan' in sheet_lower or 'reallocation' in sheet_lower:
            plan_sheet = sheet
        elif 'ستوك' in sheet_lower or 'stock' in sheet_lower:
            stock_sheet = sheet

    if not plan_sheet or not stock_sheet:
        st.error("تعذر التعرف التلقائي على شيت الخطة وشيت الاستوك.")
        return None, None, None

    df_plan = pd.read_excel(uploaded_file, sheet_name=plan_sheet)
    df_stock = pd.read_excel(uploaded_file, sheet_name=stock_sheet)

    wb = openpyxl.Workbook()
    
    # 1. ورقة الخطة
    ws_plan = wb.active
    ws_plan.title = 'Reallocation_Plan'
    ws_plan.views.sheetView[0].showGridLines = True

    # 2. ورقة الاستوك
    ws_stock = wb.create_sheet(title='ستوك')
    ws_stock.views.sheetView[0].showGridLines = True

    ws_stock.append(['Product/Barcode', 'Quantity'])
    for row in df_stock.itertuples(index=False):
        ws_stock.append([row[0], row[1]])

    store_cols = df_plan.columns[3:].tolist()
    
    # بناء الأعمدة المحدثة بالترتيب الجديد
    new_headers = (
        ['Item-Size', 'Item', 'Size'] 
        + store_cols 
        + ['إجمالي الخطة', 'رصيد الاستوك', 'تم تجهيز الخطة', 'الفرق / العجز', 'حالة التغطية', 'ملاحظات الدفعات']
    )
    ws_plan.append(new_headers)

    header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')

    for col_num in range(1, len(new_headers) + 1):
        cell = ws_plan.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    num_rows = len(df_plan)
    
    # كتابة الصفوف والمعادلات
    # AN = إجمالي الخطة | AO = رصيد الاستوك | AP = تم تجهيز الخطة | AQ = الفرق/العجز | AR = حالة التغطية | AS = ملاحظات الدفعات
    for idx, row in enumerate(df_plan.itertuples(index=False), start=2):
        item_size = row[0]
        item = row[1]
        size = row[2]
        store_vals = list(row[3:])
        
        total_plan_fmt = f"=SUM(D{idx}:AM{idx})"
        stock_qty_fmt = f'=IFERROR(VLOOKUP(A{idx}, ستوك!A:B, 2, FALSE), 0)'
        prepped_qty = 0  # افتراضي عند الإنشاء
        variance_fmt = f'=AO{idx}-AP{idx}'
        
        # معادلة حالة التغطية المحدثة
        coverage_fmt = (
            f'=IF(AQ{idx}>0, "مكتمل بالكامل + فائض مخزون", '
            f'IF(AQ{idx}=0, "مكتمل بالكامل", '
            f'IF(AO{idx}>0, "تغطية جزئية", "عجز كامل")))'
        )
        
        row_data = [item_size, item, size] + store_vals + [total_plan_fmt, stock_qty_fmt, prepped_qty, variance_fmt, coverage_fmt, ""]
        ws_plan.append(row_data)

    # قائمة الدفعات المنسدلة في العمود AS (col 45)
    dv = DataValidation(type="list", formula1='"دفعة 1, دفعة 2, دفعة 3, جاري التجهيز, مؤجل, تم الشحن"', allow_blank=True)
    ws_plan.add_data_validation(dv)
    dv.add(f"AS2:AS{num_rows + 1}")

    # التنسيق الشرطي
    yellow_fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid') # أصفر للاستوك
    red_fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')    # أحمر للعجز

    ws_plan.conditional_formatting.add(
        f"AO2:AO{num_rows + 1}",
        CellIsRule(operator='greaterThan', formula=['0'], stopIfTrue=False, fill=yellow_fill)
    )

    ws_plan.conditional_formatting.add(
        f"AQ2:AQ{num_rows + 1}",
        CellIsRule(operator='lessThan', formula=['0'], stopIfTrue=False, fill=red_fill)
    )

    for col in ws_plan.columns:
        max_len = max(len(str(cell.value or '')) for cell in col[:1])
        col_letter = get_column_letter(col[0].column)
        ws_plan.column_dimensions[col_letter].width = max(max_len + 3, 10)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output, df_plan, df_stock

# --- الواجهة البرمجية والداشبورد (Streamlit UI & Dashboard) ---

st.title("⚡ المنظومة الذكية لإدارة ومعالجة خطط الأونلاين")
st.markdown("رفع الملف الموحد | معالجة الحسابات والدفعات | داشبورد فحص وتصفية الحالات")

uploaded_file = st.file_uploader("قم برفع ملف Excel (يحتوي على الخطة والاستوك)", type=['xlsx'])

if uploaded_file is not None:
    if st.button("🚀 معالجة وبناء الخطة"):
        with st.spinner("جاري المعالجة وحقن المعادلات وتحديث الحالات..."):
            excel_out, df_plan, df_stock = process_plan_and_stock(uploaded_file)
            
            if excel_out:
                st.session_state['excel_out'] = excel_out
                st.session_state['df_plan'] = df_plan
                st.session_state['df_stock'] = df_stock
                st.success("تمت معالجة البيانات وبناء الشيت بنجاح!")

if 'excel_out' in st.session_state:
    st.divider()
    
    # 1. زر تحميل الشيت الجاهز
    st.download_button(
        label="📥 تحميل شيت الخطة المطور والإكسيل التفاعلي",
        data=st.session_state['excel_out'],
        file_name="Plan_Online_Processed_Final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.subheader("📊 داشبورد متابعة أداء الخطة والاستوك (System Overview)")
    
    df_plan = st.session_state['df_plan']
    df_stock = st.session_state['df_stock']
    
    # دمج البيانات للعرض المباشر في الداشبورد
    stock_map = dict(zip(df_stock.iloc[:, 0], df_stock.iloc[:, 1]))
    
    store_cols = df_plan.columns[3:]
    df_calc = df_plan.copy()
    df_calc['إجمالي الخطة'] = df_calc[store_cols].sum(axis=1)
    df_calc['رصيد الاستوك'] = df_calc['Item-Size'].map(stock_map).fillna(0)
    df_calc['تم تجهيز الخطة'] = 0  # بالقيمة الابتدائية
    df_calc['الفرق / العجز'] = df_calc['رصيد الاستوك'] - df_calc['تم تجهيز الخطة']

    def assign_status(row):
        diff = row['الفرق / العجز']
        stock = row['رصيد الاستوك']
        if diff > 0:
            return "مكتمل بالكامل + فائض مخزون"
        elif diff == 0:
            return "مكتمل بالكامل"
        elif stock > 0:
            return "تغطية جزئية"
        else:
            return "عجز كامل"

    df_calc['حالة التغطية'] = df_calc.apply(assign_status, axis=1)

    # عرض كروت الأرقام المجمعة (Metrics/KPIs)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي مطلوب الخطة", f"{int(df_calc['إجمالي الخطة'].sum()):,} قطعة")
    col2.metric("إجمالي الاستوك المتاح", f"{int(df_calc['رصيد الاستوك'].sum()):,} قطعة")
    col3.metric("تم تجهيزه", f"{int(df_calc['تم تجهيز الخطة'].sum()):,} قطعة")
    col4.metric("إجمالي الفائض / العجز", f"{int(df_calc['الفرق / العجز'].sum()):,} قطعة")

    # رسم بياني لتوزيع الحالات
    status_counts = df_calc['حالة التغطية'].value_counts().reset_index()
    status_counts.columns = ['حالة التغطية', 'العدد']
    
    fig = px.pie(status_counts, values='العدد', names='حالة التغطية', title="توزيع الأصناف حسب حالة التغطية", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    # 2. نظام التصفية والعرض الذكي (Smart Filter & Drill-down)
    st.subheader("🔍 عرض وتصفية الأصناف حسب الحالة")
    
    selected_status = st.selectbox(
        "اختر حالة التغطية لعرض الأصناف الخاصة بها فقط:",
        options=["الكل"] + list(df_calc['حالة التغطية'].unique())
    )

    if selected_status != "الكل":
        filtered_df = df_calc[df_calc['حالة التغطية'] == selected_status]
    else:
        filtered_df = df_calc

    st.write(f"عرض **{len(filtered_df)}** صنف متوافق مع الفلتر:")
    
    display_cols = ['Item-Size', 'Item', 'Size', 'إجمالي الخطة', 'رصيد الاستوك', 'تم تجهيز الخطة', 'الفرق / العجز', 'حالة التغطية']
    st.dataframe(filtered_df[display_cols], use_container_width=True)
