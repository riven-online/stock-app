import streamlit as st
import pandas as pd
import io
import openpyxl
import sqlite3
import os
import re

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Riven stock online",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم CSS نيون وتنسيق العرض
st.markdown("""
    <style>
    .block-container {
        max-width: 98% !important;
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .stApp {
        background-color: #080b11 !important;
        color: #e2e8f0 !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        direction: rtl;
    }

    .riven-success-banner {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 2px solid #00f2fe;
        border-radius: 14px;
        padding: 10px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
    }

    .riven-banner-title {
        color: #00f2fe;
        font-size: 1.5rem;
        font-weight: 900;
        letter-spacing: 2px;
    }

    @keyframes pulse-green {
        0% { box-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
        50% { box-shadow: 0 0 25px rgba(0, 255, 136, 0.8); }
        100% { box-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
    }

    @keyframes pulse-red {
        0% { box-shadow: 0 0 10px rgba(255, 0, 127, 0.3); }
        50% { box-shadow: 0 0 25px rgba(255, 0, 127, 0.8); }
        100% { box-shadow: 0 0 10px rgba(255, 0, 127, 0.3); }
    }

    .neon-card-green {
        background: #0f172a;
        border: 2px solid #00ff88;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        animation: pulse-green 2.5s infinite ease-in-out;
    }

    .neon-card-red {
        background: #0f172a;
        border: 2px solid #ff007f;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        animation: pulse-red 2s infinite ease-in-out;
    }

    .card-title { color: #cbd5e1 !important; font-size: 0.9rem; font-weight: 700; }
    .card-value-green { color: #00ff88 !important; font-size: 2rem; font-weight: 900; }
    .card-value-red { color: #ff007f !important; font-size: 2rem; font-weight: 900; }

    div[data-testid="stDownloadButton"]>button, .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #080b11 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. بنر التطبيق
st.markdown("""
    <div class="riven-success-banner">
        <div class="riven-banner-title">⚡ Riven stock online ⚡</div>
    </div>
""", unsafe_allow_html=True)

# إدارة التخزين الدائم
DB_FILE = "riven_saved_data.db"

def save_to_db(df, branch_cols, file_name):
    conn = sqlite3.connect(DB_FILE)
    df.to_sql("data_table", conn, if_exists="replace", index=False)
    meta_df = pd.DataFrame({"file_name": [file_name], "branch_cols": [",".join(branch_cols)]})
    meta_df.to_sql("metadata", conn, if_exists="replace", index=False)
    conn.close()

def load_from_db():
    if not os.path.exists(DB_FILE): return None, None, None
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("SELECT * FROM data_table", conn)
        meta_df = pd.read_sql("SELECT * FROM metadata", conn)
        conn.close()
        return df, meta_df["branch_cols"].iloc[0].split(","), meta_df["file_name"].iloc[0]
    except: return None, None, None

def clear_db():
    if os.path.exists(DB_FILE): os.remove(DB_FILE)
    st.session_state.clear()
    st.rerun()

# استرجاع البيانات المحفوظة
if 'df_main' not in st.session_state:
    saved_df, saved_branches, saved_filename = load_from_db()
    if saved_df is not None:
        if 'دفعة اولى' in saved_df.columns:
            saved_df.rename(columns={'دفعة اولى': 'Batch'}, inplace=True)
        st.session_state.df_main = saved_df
        st.session_state.branch_cols = saved_branches
        st.session_state.uploaded_file_name = saved_filename

# شاشة رفع الملف لبدء العمل
if 'df_main' not in st.session_state:
    st.info("📂 قم برفع ملف Excel لبدء العمل. سيتم حفظ التعديلات تلقائياً ولن تضيع البيانات.")
    uploaded_file = st.file_uploader("", type=["xlsx"])
    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            df_prep = pd.read_excel(uploaded_file, sheet_name=xls.sheet_names[0])
            
            if 'دفعة اولى' in df_prep.columns:
                df_prep.rename(columns={'دفعة اولى': 'Batch'}, inplace=True)
            elif 'Batch' not in df_prep.columns:
                df_prep['Batch'] = None

            size_idx = df_prep.columns.get_loc('Size')
            qty_idx = df_prep.columns.get_loc('qty') if 'qty' in df_prep.columns else len(df_prep.columns)
            branch_cols = [c for c in df_prep.columns[size_idx + 1 : qty_idx] if c not in ['qty', 'stock', 'diff', 'Batch', 'دفعة اولى']]
            
            if 'stock' not in df_prep.columns: df_prep['stock'] = 0
            df_prep['qty'] = df_prep[branch_cols].sum(axis=1)
            df_prep['diff'] = df_prep['stock'] - df_prep['qty']
            
            df_prep['Item-Size'] = df_prep['Item-Size'].astype(str)
            df_prep['Item'] = df_prep['Item'].astype(str)
            df_prep['Size'] = df_prep['Size'].astype(str)

            st.session_state.df_main = df_prep
            st.session_state.branch_cols = branch_cols
            st.session_state.uploaded_file_name = uploaded_file.name
            save_to_db(df_prep, branch_cols, uploaded_file.name)
            st.rerun()
        except Exception as e: st.error(f"حدث خطأ أثناء تحميل الملف: {e}")

else:
    # الشريط العلوي
    col1, col2 = st.columns([5, 1])
    with col1: 
        st.success(f"💾 **الملف النشط:** {st.session_state.get('uploaded_file_name')}")
    with col2: 
        if st.button("🗑️ حذف الشيت"): clear_db()

    df_work = st.session_state.df_main
    branch_cols = st.session_state.branch_cols

    if 'Batch' not in df_work.columns:
        df_work['Batch'] = None

    # إحصائيات مع أنيميشن النيون
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class="neon-card-green">
                <div class="card-title">إجمالي الأصناف</div>
                <div class="card-value-green">{len(df_work):,}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        shortage_cnt = (df_work['diff'] < 0).sum()
        st.markdown(f"""
            <div class="neon-card-red">
                <div class="card-title">أصناف العجز</div>
                <div class="card-value-red">{shortage_cnt:,}</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    # أدوات التصفية والبحث
    view_option = st.radio("خيارات العرض:", ["الشيت كامل", "العجز فقط"], horizontal=True)
    search_input = st.text_input("🔍 بحث بالأيتم أو (الأيتم + المقاس):", "", placeholder="مثال: 0192891 للكل أو 0192891 33 لمقاس محدد").strip()

    if view_option == "العجز فقط":
        df_filtered = df_work[df_work['diff'] < 0].copy()
    else:
        df_filtered = df_work.copy()

    # دالة البحث الدقيقة (تفرق بين الايتم والايتم سايس)
    if search_input:
        parts = search_input.split()
        
        def match_precise(row):
            item_val = str(row['Item']).strip().upper()
            item_size_val = str(row['Item-Size']).strip().upper()
            size_val = str(row['Size']).strip().upper()
            
            if len(parts) >= 2:
                search_code = parts[0].upper()
                search_size = parts[1].upper()
                code_match = (search_code in item_val) or (search_code in item_size_val)
                size_match = (search_size == size_val) or (item_size_val.endswith(search_size))
                return code_match and size_match
            else:
                search_code = parts[0].upper()
                return (search_code in item_val) or (search_code in item_size_val)

        mask = df_filtered.apply(match_precise, axis=1)
        df_display = df_filtered[mask]
    else:
        df_display = df_filtered

    display_cols = ['Item-Size', 'Item', 'Size', 'stock', 'qty', 'diff'] + branch_cols + ['Batch']

    # قائمة خيارات عمود Batch (الدفعة 1 حتى 50)
    batch_options = [""] + [f"الدفعة {i}" for i in range(1, 51)]

    # إعداد تكوين القائمة المنسدلة بدون أخطاء متوافقة مع كل نسخ Streamlit
    column_config = {
        "Batch": st.column_config.SelectboxColumn(
            "Batch",
            help="اختر رقم الدفعة",
            options=batch_options,
            required=False
        )
    }

    # الجدول الذكي
    edited_df = st.data_editor(
        df_display[display_cols],
        key="editor_grid",
        use_container_width=True,
        height=480,
        column_config=column_config,
        disabled=['Item-Size', 'Item', 'Size', 'stock', 'qty', 'diff'],
        num_rows="fixed"
    )

    # حفظ التعديلات فورياً
    has_changed = False
    for idx in edited_df.index:
        for col in branch_cols + ['Batch']:
            if st.session_state.df_main.loc[idx, col] != edited_df.loc[idx, col]:
                st.session_state.df_main.loc[idx, col] = edited_df.loc[idx, col]
                has_changed = True

    if has_changed:
        st.session_state.df_main['qty'] = st.session_state.df_main[branch_cols].sum(axis=1)
        st.session_state.df_main['diff'] = st.session_state.df_main['stock'] - st.session_state.df_main['qty']
        save_to_db(st.session_state.df_main, branch_cols, st.session_state.uploaded_file_name)
        st.rerun()

    st.markdown("---")

    # تصدير البيانات مع المعادلات
    def export_excel_with_formulas(data_to_export):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data_to_export.to_excel(writer, index=False, sheet_name='Exported_Stock')
            workbook = writer.book
            worksheet = writer.sheets['Exported_Stock']

            qty_col_letter = openpyxl.utils.get_column_letter(data_to_export.columns.get_loc('qty') + 1)
            stock_col_letter = openpyxl.utils.get_column_letter(data_to_export.columns.get_loc('stock') + 1)
            diff_col_letter = openpyxl.utils.get_column_letter(data_to_export.columns.get_loc('diff') + 1)
            
            first_b_letter = openpyxl.utils.get_column_letter(data_to_export.columns.get_loc(branch_cols[0]) + 1)
            last_b_letter = openpyxl.utils.get_column_letter(data_to_export.columns.get_loc(branch_cols[-1]) + 1)

            for row_idx in range(2, len(data_to_export) + 2):
                worksheet[f'{qty_col_letter}{row_idx}'] = f"=SUM({first_b_letter}{row_idx}:{last_b_letter}{row_idx})"
                worksheet[f'{diff_col_letter}{row_idx}'] = f"={stock_col_letter}{row_idx}-{qty_col_letter}{row_idx}"

        return output.getvalue()

    # زر التحميل المفلتر
    st.markdown("### 📥 تصدير البيانات حسب الوضع والفلترة الحالية للموقع")
    
    file_label = f"Riven_{view_option}_Filtered.xlsx"

    st.download_button(
        label=f"📥 تحميل الشيت المفلتر حالياً على الموقع ({len(df_display)} صنف)",
        data=export_excel_with_formulas(df_display[display_cols]),
        file_name=file_label,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
