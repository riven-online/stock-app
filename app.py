import streamlit as st
import pandas as pd
import io
import openpyxl

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Riven",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم CSS نيون وتثبيت الأعمدة أثناء التمرير
st.markdown("""
    <style>
    .stApp {
        background-color: #080b11 !important;
        color: #e2e8f0 !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        direction: rtl;
    }

    div[data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #0f172a !important;
        border: 2px dashed #00f2fe !important;
        border-radius: 16px !important;
        box-shadow: 0 0 18px rgba(0, 242, 254, 0.25) !important;
        padding: 15px !important;
    }

    .riven-success-banner {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 1px solid #00f2fe;
        border-radius: 14px;
        padding: 12px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.35);
    }

    .riven-banner-title {
        color: #00f2fe;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: 2px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }

    .led-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px currentColor;
    }
    .led-blue { background-color: #00f2fe; color: #00f2fe; }
    .led-red { background-color: #ff007f; color: #ff007f; }
    .led-green { background-color: #00ff88; color: #00ff88; }

    .dashboard-header {
        color: #00f2fe;
        font-size: 1.4rem;
        font-weight: 900;
        letter-spacing: 2px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .custom-card {
        background: #0f172a;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 15px;
    }
    .card-normal { border: 1px solid rgba(0, 242, 254, 0.3); }
    .card-warning { border: 1px solid rgba(255, 0, 127, 0.4); }

    .card-title { color: #cbd5e1 !important; font-size: 0.9rem; font-weight: 600; }
    .card-value-blue { color: #00f2fe !important; font-size: 1.8rem; font-weight: 800; }
    .card-value-red { color: #ff007f !important; font-size: 1.8rem; font-weight: 800; }

    div[data-testid="stDownloadButton"]>button, .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #080b11 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }

    /* تثبيت الأعمدة الأولى (من Item-Size حتى diff) عند التمرير الأفقي */
    div[data-testid="stDataFrame"] table th:nth-child(-n+7),
    div[data-testid="stDataFrame"] table td:nth-child(-n+7) {
        position: sticky !important;
        right: 0 !important;
        z-index: 2 !important;
        background-color: #0f172a !important;
        border-left: 2px solid #00f2fe !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. بنر Riven
st.markdown("""
    <div class="riven-success-banner">
        <div class="riven-banner-title">
            <span class="led-dot led-green"></span>
            Riven Engine
            <span class="led-dot led-blue"></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. رفع الملف
uploaded_file = st.file_uploader("", type=["xlsx"])

# دالة إعادة توزيع العجز لكود محدد
def auto_rebalance_row(row, branch_cols, max_allowed):
    current_total = sum(row[b] for b in branch_cols)
    if current_total <= max_allowed or current_total == 0:
        return row
    
    reduction_needed = current_total - max_allowed
    while reduction_needed > 0:
        active_branches = [b for b in branch_cols if row[b] > 0]
        if not active_branches:
            break
        for b in active_branches:
            if reduction_needed <= 0:
                break
            if row[b] > 0:
                row[b] -= 1
                reduction_needed -= 1
    return row

if uploaded_file is not None:
    try:
        # قراءة البيانات وإعداد الجلسة
        if 'df_main' not in st.session_state or st.session_state.get('uploaded_file_name') != uploaded_file.name:
            xls = pd.ExcelFile(uploaded_file)
            sheet_names = xls.sheet_names
            
            prep_sheet = sheet_names[0]
            df_prep = pd.read_excel(uploaded_file, sheet_name=prep_sheet)

            if 'ستوك' in sheet_names:
                df_stock = pd.read_excel(uploaded_file, sheet_name='ستوك')
                stock_map = df_stock.set_index(df_stock.columns[0])[df_stock.columns[1]].to_dict()
            else:
                stock_map = {}

            size_idx = df_prep.columns.get_loc('Size')
            qty_idx = df_prep.columns.get_loc('qty') if 'qty' in df_prep.columns else len(df_prep.columns)
            
            branch_cols = [c for c in df_prep.columns[size_idx + 1 : qty_idx] if c not in ['qty', 'stock', 'diff', 'دفعة اولى']]

            if 'stock' not in df_prep.columns:
                df_prep['stock'] = df_prep['Item-Size'].map(stock_map).fillna(0)
            else:
                df_prep['stock'] = df_prep['Item-Size'].map(stock_map).fillna(df_prep['stock'])

            df_prep['qty'] = df_prep[branch_cols].sum(axis=1)
            df_prep['diff'] = df_prep['stock'] - df_prep['qty']

            if 'دفعة اولى' not in df_prep.columns:
                df_prep['دفعة اولى'] = 'دفعه اولى'

            df_prep['Item-Size'] = df_prep['Item-Size'].astype(str)
            df_prep['Item'] = df_prep['Item'].astype(str)
            df_prep['Size'] = df_prep['Size'].astype(str)

            st.session_state.df_main = df_prep.copy()
            st.session_state.branch_cols = branch_cols
            st.session_state.uploaded_file_name = uploaded_file.name

        df_work = st.session_state.df_main
        branch_cols = st.session_state.branch_cols

        # DASHBOARD
        st.markdown("<div class='dashboard-header'><span class='led-dot led-blue'></span> DASHBOARD</div>", unsafe_allow_html=True)
        
        total_items = len(df_work)
        shortage_count = (df_work['diff'] < 0).sum()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
                <div class="custom-card card-normal">
                    <div class="card-title"><span class="led-dot led-blue"></span> إجمالي الأصناف والمقاسات</div>
                    <div class="card-value-blue">{total_items:,}</div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class="custom-card card-warning">
                    <div class="card-title"><span class="led-dot led-red"></span> أصناف العجز (السالب)</div>
                    <div class="card-value-red">{shortage_count:,}</div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div class="custom-card card-normal">
                    <div class="card-title"><span class="led-dot led-green"></span> عدد الفروع المشمولة</div>
                    <div class="card-value-blue">{len(branch_cols)} فرع</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # أدوات التصفية والبحث
        st.markdown("<div class='dashboard-header'><span class='led-dot led-blue'></span> عرض البيانات وإدارة التوزيع</div>", unsafe_allow_html=True)

        view_option = st.radio("خيارات عرض الجدول:", ["الشيت كامل", "العجز فقط"], horizontal=True)

        col_search, col_btn = st.columns([3, 2])
        with col_search:
            search_query = st.text_input("🔍 البحث برقم الكود (Item أو Item-Size):", "").strip()

        # تصفية الشيت بحسب الفلتر
        if view_option == "العجز فقط":
            df_filtered = df_work[df_work['diff'] < 0].copy()
        else:
            df_filtered = df_work.copy()

        # تطبيق البحث إن وجد
        if search_query:
            df_display = df_filtered[
                df_filtered['Item-Size'].str.contains(search_query, case=False, na=False) | 
                df_filtered['Item'].str.contains(search_query, case=False, na=False)
            ]
        else:
            df_display = df_filtered

        with col_btn:
            st.write(" ")
            st.write(" ")
            if st.button("⚡ تسوية الكمية للكود المبحوث عنه فقط"):
                if search_query and len(df_display) > 0:
                    shortage_rows = df_display[df_display['diff'] < 0]
                    if len(shortage_rows) > 0:
                        for idx in shortage_rows.index:
                            row = df_work.loc[idx]
                            updated_row = auto_rebalance_row(row, branch_cols, row['stock'])
                            df_work.loc[idx] = updated_row
                        
                        df_work['qty'] = df_work[branch_cols].sum(axis=1)
                        df_work['diff'] = df_work['stock'] - df_work['qty']
                        st.session_state.df_main = df_work
                        st.success(f"تمت تسوية الكمية للكود ({search_query}) بنجاح!")
                        st.rerun()
                    else:
                        st.info("الكود المبحوث عنه لا يحتوي على عجز لتسويته.")
                else:
                    st.warning("يرجى كتابة رقم الكود في خانة البحث أولاً لتنفيذ التسوية الخاصة به!")

        display_cols = ['Item-Size', 'Item', 'Size', 'stock', 'qty', 'diff'] + branch_cols + ['دفعة اولى']

        # عرض الجدول القابل للتعديل المباشر
        edited_df = st.data_editor(
            df_display[display_cols],
            key="main_editor",
            use_container_width=True,
            height=420,
            disabled=['Item-Size', 'Item', 'Size', 'stock', 'qty', 'diff']
        )

        # التحديث اللحظي للقيم والمعادلات بمجرد تعديل أرقام الفروع
        has_changed = False
        for idx in edited_df.index:
            for b in branch_cols + ['دفعة اولى']:
                if st.session_state.df_main.loc[idx, b] != edited_df.loc[idx, b]:
                    st.session_state.df_main.loc[idx, b] = edited_df.loc[idx, b]
                    has_changed = True

        if has_changed:
            st.session_state.df_main['qty'] = st.session_state.df_main[branch_cols].sum(axis=1)
            st.session_state.df_main['diff'] = st.session_state.df_main['stock'] - st.session_state.df_main['qty']
            st.rerun()

        st.markdown("---")

        # تصدير الملفات مع حفظ معادلات Excel الحقيقية
        st.markdown("<div class='dashboard-header'><span class='led-dot led-green'></span> تصدير الشيت النهائي بعد التعديلات والتجميع</div>", unsafe_allow_html=True)

        def make_excel_with_formulas(df_to_export):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_to_export.to_excel(writer, index=False, sheet_name='Reallocation_Plan')
                workbook = writer.book
                worksheet = writer.sheets['Reallocation_Plan']

                qty_col_letter = openpyxl.utils.get_column_letter(df_to_export.columns.get_loc('qty') + 1)
                stock_col_letter = openpyxl.utils.get_column_letter(df_to_export.columns.get_loc('stock') + 1)
                diff_col_letter = openpyxl.utils.get_column_letter(df_to_export.columns.get_loc('diff') + 1)
                
                first_b_letter = openpyxl.utils.get_column_letter(df_to_export.columns.get_loc(branch_cols[0]) + 1)
                last_b_letter = openpyxl.utils.get_column_letter(df_to_export.columns.get_loc(branch_cols[-1]) + 1)

                for row_idx in range(2, len(df_to_export) + 2):
                    worksheet[f'{qty_col_letter}{row_idx}'] = f"=SUM({first_b_letter}{row_idx}:{last_b_letter}{row_idx})"
                    worksheet[f'{diff_col_letter}{row_idx}'] = f"={stock_col_letter}{row_idx}-{qty_col_letter}{row_idx}"

            return output.getvalue()

        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.download_button(
                label="📥 تحميل كشف أصناف العجز فقط بعد التعديل (Excel مع المعادلات)",
                data=make_excel_with_formulas(st.session_state.df_main[st.session_state.df_main['diff'] < 0][display_cols]),
                file_name="كشف_العجز_بعد_التعديل.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with c_exp2:
            st.download_button(
                label="📥 تحميل كشف التوزيع الكامل بعد التعديل (Excel مع المعادلات)",
                data=make_excel_with_formulas(st.session_state.df_main[display_cols]),
                file_name="الخطه_النهائيه_الكامله.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")
