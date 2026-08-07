import streamlit as st
import pandas as pd
import io
import openpyxl
import sqlite3
import os

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Riven stock online",
    page_icon="⚡",
    layout="wide", # جعل الصفحة عريضة
    initial_sidebar_state="collapsed"
)

# 2. تصميم CSS نيون وتوسيع العرض لراحة العين
st.markdown("""
    <style>
    /* جعل التطبيق يأخذ كامل عرض الشاشة */
    .block-container {
        max-width: 98% !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

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
        padding: 15px !important;
    }

    .riven-success-banner {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 1px solid #00f2fe;
        border-radius: 14px;
        padding: 10px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
    }

    .riven-banner-title {
        color: #00f2fe;
        font-size: 1.3rem;
        font-weight: 800;
        letter-spacing: 2px;
    }

    .dashboard-header {
        color: #00f2fe;
        font-size: 1.2rem;
        font-weight: 900;
        margin-bottom: 10px;
    }

    .custom-card {
        background: #0f172a;
        border-radius: 10px;
        padding: 12px;
        border: 1px solid rgba(0, 242, 254, 0.2);
    }

    .card-title { color: #cbd5e1 !important; font-size: 0.8rem; }
    .card-value { color: #00f2fe !important; font-size: 1.5rem; font-weight: 800; }

    div[data-testid="stDownloadButton"]>button, .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #080b11 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. بنر Riven stock online
st.markdown("""
    <div class="riven-success-banner">
        <div class="riven-banner-title">⚡ Riven stock online ⚡</div>
    </div>
""", unsafe_allow_html=True)

# إدارة التخزين
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

# استرجاع البيانات
if 'df_main' not in st.session_state:
    saved_df, saved_branches, saved_filename = load_from_db()
    if saved_df is not None:
        st.session_state.df_main = saved_df
        st.session_state.branch_cols = saved_branches
        st.session_state.uploaded_file_name = saved_filename

# 4. رفع الملف أو العرض
if 'df_main' not in st.session_state:
    st.info("📂 قم برفع ملف Excel. سيتم حفظ التعديلات تلقائياً.")
    uploaded_file = st.file_uploader("", type=["xlsx"])
    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            df_prep = pd.read_excel(uploaded_file, sheet_name=xls.sheet_names[0])
            # منطق معالجة البيانات الأساسي
            size_idx = df_prep.columns.get_loc('Size')
            qty_idx = df_prep.columns.get_loc('qty') if 'qty' in df_prep.columns else len(df_prep.columns)
            branch_cols = [c for c in df_prep.columns[size_idx + 1 : qty_idx] if c not in ['qty', 'stock', 'diff', 'دفعة اولى']]
            
            if 'stock' not in df_prep.columns: df_prep['stock'] = 0
            df_prep['qty'] = df_prep[branch_cols].sum(axis=1)
            df_prep['diff'] = df_prep['stock'] - df_prep['qty']
            if 'دفعة اولى' not in df_prep.columns: df_prep['دفعة اولى'] = 'دفعه اولى'
            
            st.session_state.df_main = df_prep
            st.session_state.branch_cols = branch_cols
            st.session_state.uploaded_file_name = uploaded_file.name
            save_to_db(df_prep, branch_cols, uploaded_file.name)
            st.rerun()
        except Exception as e: st.error(f"خطأ: {e}")
else:
    # الشريط العلوي
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1: st.success(f"💾 {st.session_state.get('uploaded_file_name')}")
    with col2: 
        if st.button("🗑️ حذف الكل"): clear_db()
    
    df_work = st.session_state.df_main
    branch_cols = st.session_state.branch_cols

    # إحصائيات سريعة
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='custom-card'><div class='card-title'>إجمالي الأصناف</div><div class='card-value'>{len(df_work):,}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='custom-card'><div class='card-title'>أصناف العجز</div><div class='card-value' style='color:#ff007f'>{(df_work['diff'] < 0).sum():,}</div></div>", unsafe_allow_html=True)

    st.write("")
    
    # الجدول
    display_cols = ['Item-Size', 'Item', 'Size', 'stock', 'qty', 'diff'] + branch_cols + ['دفعة اولى']
    
    edited_df = st.data_editor(
        df_work[display_cols],
        use_container_width=True,
        height=500,
        disabled=['Item-Size', 'Item', 'Size', 'stock', 'qty', 'diff']
    )

    # التحديث التلقائي
    has_changed = False
    for idx in edited_df.index:
        for b in branch_cols + ['دفعة اولى']:
            if st.session_state.df_main.loc[idx, b] != edited_df.loc[idx, b]:
                st.session_state.df_main.loc[idx, b] = edited_df.loc[idx, b]
                has_changed = True

    if has_changed:
        st.session_state.df_main['qty'] = st.session_state.df_main[branch_cols].sum(axis=1)
        st.session_state.df_main['diff'] = st.session_state.df_main['stock'] - st.session_state.df_main['qty']
        save_to_db(st.session_state.df_main, branch_cols, st.session_state.uploaded_file_name)
        st.rerun()

    # التصدير
    st.download_button("📥 تحميل الشيت النهائي (Excel)", data=io.BytesIO(df_work.to_excel(index=False).encode('utf-8')), file_name="Riven_Data.xlsx")
