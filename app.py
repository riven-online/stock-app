import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter
import io

def process_plan_and_stock(uploaded_file):
    # 1. قراءة كافة ورقات العمل من الملف المرفوع
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    
    plan_sheet = None
    stock_sheet = None
    
    # التعرف الذكي على الشيتات
    for sheet in sheet_names:
        sheet_lower = sheet.lower()
        if 'plan' in sheet_lower or 'reallocation' in sheet_lower:
            plan_sheet = sheet
        elif 'ستوك' in sheet_lower or 'stock' in sheet_lower:
            stock_sheet = sheet

    if not plan_sheet or not stock_sheet:
        st.error("تعذر التعرف التلقائي على شيت الخطة وشيت الاستوك. يرجى التأكد من المسميات.")
        return None

    # قراءة البيانات عبر Pandas
    df_plan = pd.read_excel(uploaded_file, sheet_name=plan_sheet)
    df_stock = pd.read_excel(uploaded_file, sheet_name=stock_sheet)

    # 2. بناء ملف Excel جديد عالي الكفاءة باستخدام OpenPyXL
    wb = openpyxl.Workbook()
    
    # إعداد ورقة الخطة
    ws_plan = wb.active
    ws_plan.title = 'Reallocation_Plan'
    ws_plan.views.sheetView[0].showGridLines = True

    # إعداد ورقة الاستوك
    ws_stock = wb.create_sheet(title='ستوك')
    ws_stock.views.sheetView[0].showGridLines = True

    # نقل بيانات الاستوك
    ws_stock.append(['Product/Barcode', 'Quantity'])
    for row in df_stock.itertuples(index=False):
        ws_stock.append([row[0], row[1]])

    # تحديد أعمدة الفروع والأعمدة الجديدة
    store_cols = df_plan.columns[3:].tolist()
    new_headers = (
        ['Item-Size', 'Item', 'Size'] 
        + store_cols 
        + ['إجمالي الخطة', 'رصيد الاستوك', 'الفرق / العجز', 'حالة التغطية', 'ملاحظات الدفعات']
    )
    ws_plan.append(new_headers)

    # تنسيق الهيدر (Header Styling)
    header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid') # أزرق داكن احترافي
    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')

    for col_num in range(1, len(new_headers) + 1):
        cell = ws_plan.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # 3. حقن الصفوف والمعادلات البرمجية
    num_rows = len(df_plan)
    for idx, row in enumerate(df_plan.itertuples(index=False), start=2):
        item_size = row[0]
        item = row[1]
        size = row[2]
        store_vals = list(row[3:])
        
        # صيغ المعادلات
        total_plan_fmt = f"=SUM(D{idx}:AM{idx})"
        stock_qty_fmt = f'=IFERROR(VLOOKUP(A{idx}, ستوك!A:B, 2, FALSE), 0)'
        variance_fmt = f'=AO{idx}-AN{idx}'
        coverage_fmt = f'=IF(AO{idx}>=AN{idx}, "مكتمل بالكامل", IF(AO{idx}>0, "تغطية جزئية", "عجز كامل"))'
        
        row_data = [item_size, item, size] + store_vals + [total_plan_fmt, stock_qty_fmt, variance_fmt, coverage_fmt, ""]
        ws_plan.append(row_data)

    # 4. إضافة قائمة اختيار الدفعات (Data Validation Dropdown)
    dv = DataValidation(type="list", formula1='"دفعة 1, دفعة 2, دفعة 3, جاري التجهيز, مؤجل, تم الشحن"', allow_blank=True)
    ws_plan.add_data_validation(dv)
    dv.add(f"AR2:AR{num_rows + 1}")

    # 5. التنسيق الشرطي (Conditional Formatting)
    yellow_fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid') # أصفر خفيف
    red_fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')    # أحمر خفيف

    # تمييز الأصناف المتاحة في الاستوك باللون الأصفر
    ws_plan.conditional_formatting.add(
        f"AO2:AO{num_rows + 1}",
        CellIsRule(operator='greaterThan', formula=['0'], stopIfTrue=False, fill=yellow_fill)
    )

    # تمييز العجز باللون الأحمر
    ws_plan.conditional_formatting.add(
        f"AP2:AP{num_rows + 1}",
        CellIsRule(operator='lessThan', formula=['0'], stopIfTrue=False, fill=red_fill)
    )

    # ضبط عرض الأعمدة تلقائياً
    for col in ws_plan.columns:
        max_len = max(len(str(cell.value or '')) for cell in col[:1])
        col_letter = get_column_letter(col[0].column)
        ws_plan.column_dimensions[col_letter].width = max(max_len + 3, 10)

    # حفظ الملف في ذاكرة مؤقتة (Buffer) للتنزيل الفوري
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

# --- واجهة المستخدم (Streamlit Interface) ---
st.title("⚡ محرك معالجة وتوليد خطط الأونلاين التلقائي")
st.write("قم برفع شيت الخطة والاستوك الموحد لتوليد الشيت المعالج التفاعلي فوراً للمدير.")

uploaded_file = st.file_uploader("رفع ملف Excel (يحتوي على ورقتي الخطة والاستوك)", type=['xlsx'])

if uploaded_file is not None:
    if st.button("🚀 معالجة وتوليد الشيت الآن"):
        with st.spinner("جاري معالجة البيانات، ربط الاستوك، وحقن المعادلات..."):
            processed_file = process_plan_and_stock(uploaded_file)
            if processed_file:
                st.success("تمت المعالجة بنجاح وبدون أي أخطاء!")
                st.download_button(
                    label="📥 تحميل شيت الخطة المطور للمدير",
                    data=processed_file,
                    file_name="Plan_Processed_Final.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
