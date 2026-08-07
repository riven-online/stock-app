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

# 2. تصميم CSS نيون ذكي مع ضبط الهوامش وأنيميشن الكروت
st.markdown("""
    <style>
    /* ضبط المسافات لمنع انقطاع الجزء العلوي */
    .block-container {
        max-width: 98% !important;
        padding-top: 4rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    .stApp {
        background-color: #080b11 !important;
        color: #e2e8f0 !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        direction: rtl;
    }

    /* البنر العلوي */
    .riven-success-banner {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 2px solid #00f2fe;
        border-radius: 14px;
        padding: 12px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
    }

    .riven-banner-title {
        color: #00f2fe;
        font-size: 1.6rem;
        font-weight: 900;
        letter-spacing: 2px;
    }

    /* أنيميشن الكروت النيون */
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
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        animation: pulse-green 2.5s infinite ease-in-out;
    }

    .neon-card-red {
        background: #0f172a;
        border: 2px solid #ff007f;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        animation: pulse-red 2s infinite ease-in-out;
    }

    .card-title {
        color: #cbd5e1 !important;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .card-value-green {
        color: #00ff88 !important;
        font-size: 2.2rem;
        font-weight: 900;
        text-shadow: 0 0 12px rgba(0, 255, 136, 0.6);
    }

    .card-value-red {
        color: #ff007f !important;
        font-size: 2.2rem;
        font-weight: 900;
        text-shadow: 0 0 12px rgba(255, 0, 127, 0.6);
    }

    div[data-testid="stDownloadButton"]>button, .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #080b11 !important;
        border-radius: 10px !important;
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

# دالة البحث الذكي المتطورة
def normalize_code(text):
    if not text: return ""
    text = str(text).strip().upper()
    # استخراج الأرقام فقط للتطابق الإجباري والمرن
    digits_only = re.sub(r'\D', '', text)
    return digits_only

# استرجاع البيانات المحفوظة
if 'df_main' not in st.session_state:
    saved_df, saved_branches, saved_filename = load_from_db()
    if saved_df is not None:
        st.session_state.df_main = saved_df
        st.session_state.branch_cols = saved_branches
        st.session_state.uploaded_file_name = saved_filename

# شاشة رفع الملف
if 'df_main' not in st.session_state:
    st.info("📂 قم برفع ملف Excel لبدء العمل. سيتم حفظ التعديلات تلقائياً.")
    uploaded_file = st.file_uploader("", type=["xlsx"])
    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            df_prep = pd.read_excel(uploaded_file, sheet_name=xls.sheet_names[0])
            size_idx = df_prep.columns.get_loc('Size')
            qty_idx = df_prep.columns.get_loc('qty') if 'qty' in df_prep.columns else len(df_prep.columns)
            branch_cols = [c for c in df_prep.columns[size_idx + 1 : qty_idx] if c not in ['qty', 'stock', 'diff', 'دفعة اولى']]
            
            if 'stock' not in df_prep.columns: df_prep['stock'] = 0
            df_prep['qty'] = df_prep[branch_cols].sum(axis=1)
            df_prep['diff'] = df_prep['stock'] - df_prep['qty']
            if 'دفعة اولى' not in df_prep.columns: df_prep['دفعة اولى'] = 'دفعه اولى'
            
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

    # خانة البحث المرنة
    view_option = st.radio("خيارات العرض:", ["الشيت كامل", "العجز فقط"], horizontal=True)
    search_input = st.text_input("🔍 بحث بالأيتم أو (الأيتم + المقاس):", "", placeholder="مثال: 0192891 أو 0192891 33").strip()

    if view_option == "العجز فقط":
        df_filtered = df_work[df_work['diff'] < 0].copy()
    else:
        df_filtered = df_work.copy()

    # تنفيذ البحث المرن
    if search_input:
        search_digits = normalize_code(search_input)
        
        def match_row(row):
            item_size_digits = normalize_code(row['Item-Size'])
            item_digits = normalize_code(row['Item'])
            size_digits = normalize_code(row['Size'])
            
            # التطابق بوجود الأرقام كاملة (سواء كتبت الحرف أول الكود أم لا، بمسافة أو بدون)
            if search_digits in item_size_digits or search_digits in (item_digits + size_digits) or search_digits in item_digits:
                return True
            return False

        mask = df_filtered.apply(match_row, axis=1)
        df_display = df_filtered[mask]
    else:
        df_display = df_filtered

    display_cols = ['Item-Size', 'Item', 'Size', 'stock', 'qty', 'diff'] + branch_cols + ['دفعة اولى']

    # الجدول القابل للتعديل
    edited_df = st.data_editor(
        df_display[display_cols],
        use_container_width=True,
        height=480,
        disabled=['Item-Size', 'Item', 'Size', 'stock', 'qty', 'diff']
    )

    # حفظ التعديلات اللحظية
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

    # تصدير الملفات
    st.download_button(
        label="📥 تحميل الشيت التعديل النهائي (Excel)",
        data=io.BytesIO(df_work.to_excel(index=False).encode('utf-8')),
        file_name="Riven_Stock_Online.xlsx"
    )
