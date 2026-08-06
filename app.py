import streamlit as st
import pandas as pd
import io
import time

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="RIVEN | Cyber Stock AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم النيون المتقدم وإجبار تعديل صندوق الرفع والخطوط
st.markdown("""
    <style>
    /* خلفية ليلي داكنة وشاملة */
    .stApp {
        background-color: #080b11 !important;
        color: #e2e8f0 !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        direction: rtl;
    }

    /* العنوان الرئيسي */
    h1 {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.3);
        margin-bottom: 5px !important;
        text-align: center;
    }

    /* الوصف الفرعي */
    .sub-title {
        color: #94a3b8;
        font-size: 0.95rem;
        text-align: center;
        margin-bottom: 25px;
    }

    /* إجبار مستطيل الرفع بالكامل على الثيم الداكن والنيون */
    div[data-testid="stFileUploader"], 
    div[data-testid="stFileUploadDropzone"],
    section[data-testid="stFileUploadDropzone"] {
        background-color: #0f172a !important;
        border: 1px dashed #00f2fe !important;
        border-radius: 16px !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.15) !important;
        transition: all 0.3s ease !important;
        padding: 20px !important;
    }

    div[data-testid="stFileUploadDropzone"]:hover {
        border-color: #ff007f !important;
        box-shadow: 0 0 20px rgba(255, 0, 127, 0.4) !important;
    }

    /* تحويل نصوص داخل المستطيل للون الفاتح والنيون */
    div[data-testid="stFileUploadDropzone"] span,
    div[data-testid="stFileUploadDropzone"] small,
    div[data-testid="stFileUploadDropzone"] div {
        color: #38bdf8 !important;
        font-size: 0.85rem !important;
    }

    /* تعديل زر الرفع نفسه داخل المستطيل */
    div[data-testid="stFileUploadDropzone"] button {
        background: linear-gradient(135deg, #00f2fe 0%, #00b4d8 100%) !important;
        color: #080b11 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.3) !important;
    }

    /* كروت المقاييس النيون */
    div[data-testid="stMetric"] {
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4) !important;
    }
    div[data-testid="stMetricValue"] {
        color: #00f2fe !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }

    /* أزرار التحميل */
    .stButton>button, div[data-testid="stDownloadButton"]>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #080b11 !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        font-size: 0.95rem !important;
        padding: 10px 24px !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.3) !important;
    }
    .stButton>button:hover, div[data-testid="stDownloadButton"]>button:hover {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(255, 0, 127, 0.6) !important;
    }

    /* جداول البيانات */
    div[data-testid="stDataFrame"] {
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. الواجهة الرئيسية الهادئة
st.title("⚡ RIVEN | Cyber Stock Engine")
st.markdown("<div class='sub-title'>المحرك الذكي لتحليل وتطابق استوك الفروع والتحضير</div>", unsafe_allow_html=True)

# 4. رفع الملف بدون عناوين مزعجة
uploaded_file = st.file_uploader("", type=["xlsx"])

# 5. معالجة البيانات وأنيميشن التحميل الخاص بالملابس
if uploaded_file is not None:
    fashion_icons = ["👔", "👕", "👗", "👖", "👠", "🧥", "🛍️"]
    status_text = st.empty()
    progress_bar = st.progress(0)

    for step in range(1, 101):
        time.sleep(0.015)
        progress_bar.progress(step)
        current_icon = fashion_icons[(step // 15) % len(fashion_icons)]
        
        if step < 40:
            status_text.markdown(f"### {current_icon} *جاري مطابقة منتجات الاستوك والقطع...*")
        elif step < 80:
            status_text.markdown(f"### {current_icon} *جاري توزيع الكميات على الفروع وتحديد العجز...*")
        else:
            status_text.markdown(f"### {current_icon} *تجهيز كروت البيانات والتقرير النهائي...*")

    progress_bar.empty()
    status_text.empty()

    try:
        df_prep = pd.read_excel(uploaded_file, sheet_name='Reallocation_Plan_ONL_2026-08-0')
        df_stock = pd.read_excel(uploaded_file, sheet_name='ستوك')

        size_idx = df_prep.columns.get_loc('Size')
        qty_idx = df_prep.columns.get_loc('qty')
        branch_cols = df_prep.columns[size_idx + 1 : qty_idx].tolist()

        stock_map = df_stock.set_index('Product/Barcode')['Quantity'].to_dict()
        df_prep['stock'] = df_prep['Item-Size'].map(stock_map).fillna(df_prep['stock'])
        df_prep['qty'] = df_prep[branch_cols].sum(axis=1)
        df_prep['diff'] = df_prep['stock'] - df_prep['qty']

        st.success("✨ تم تحليل شيتات الملابس والاستوك بنجاح!")

        # المقاييس الرئيسية
        total_items = len(df_prep)
        shortage_items = (df_prep['diff'] < 0).sum()

        st.markdown("### 📊 الداشبورد")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="📦 إجمالي الأصناف والمقاسات", value=f"{total_items:,}")
        with c2:
            st.metric(label="🚨 أصناف العجز", value=f"{shortage_items:,}")
        with c3:
            st.metric(label="🏬 عدد الفروع", value=f"{len(branch_cols)} فرع")

        st.markdown("---")

        # عرض العجز وتصديره
        st.markdown("### 🚨 الأصناف التي بها عجز رصيد")
        df_shortage = df_prep[df_prep['diff'] < 0].copy()

        buffer_shortage = io.BytesIO()
        with pd.ExcelWriter(buffer_shortage, engine='openpyxl') as writer:
            df_shortage.to_excel(writer, index=False, sheet_name='تقرير_العجز')

        st.download_button(
            label="📥 تحميل كشف العجز (Excel)",
            data=buffer_shortage.getvalue(),
            file_name="تقرير_العجز_والفروقات.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.dataframe(df_shortage[['Item-Size', 'Item', 'Size', 'qty', 'stock', 'diff'] + branch_cols], use_container_width=True)

        st.markdown("---")

        # الشيت النهائي
        st.markdown("### ✅ الشيت النهائي للتحضير")
        buffer_final = io.BytesIO()
        with pd.ExcelWriter(buffer_final, engine='openpyxl') as writer:
            df_prep.to_excel(writer, index=False, sheet_name='التحضير_النهائي')

        st.download_button(
            label="📥 تحميل الشيت النهائي الكامل (Excel)",
            data=buffer_final.getvalue(),
            file_name="الخطه_النهائيه_للكشوفات.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"حدث خطأ في قراءة البيانات: {e}")
