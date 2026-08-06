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

# 2. تصميم النيون المتقدم وتنسيق الأنيميشن الـ 3D
st.markdown("""
    <style>
    /* خلفية التطبيق الداكنة */
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
        font-size: 2.1rem !important;
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.3);
        margin-bottom: 5px !important;
        text-align: center;
    }

    /* الوصف الفرعي */
    .sub-title {
        color: #94a3b8;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 25px;
    }

    /* تلوين مستطيل الرفع بالكامل للثيم الداكن والنيون */
    div[data-testid="stFileUploader"],
    div[data-testid="stFileUploader"] *,
    div[data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploaderDropzone"] *,
    section[data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"] * {
        background-color: #0f172a !important;
        background: #0f172a !important;
        color: #00f2fe !important;
    }

    div[data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"] {
        border: 2px dashed #00f2fe !important;
        border-radius: 16px !important;
        box-shadow: 0 0 18px rgba(0, 242, 254, 0.25) !important;
        transition: all 0.3s ease-in-out !important;
        padding: 20px !important;
    }

    div[data-testid="stFileUploaderDropzone"]:hover,
    section[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #ff007f !important;
        box-shadow: 0 0 25px rgba(255, 0, 127, 0.5) !important;
    }

    div[data-testid="stFileUploaderDropzone"] button,
    section[data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, #00f2fe 0%, #00b4d8 100%) !important;
        color: #080b11 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.4) !important;
    }

    /* أنيميشن نيون 3D كود وسيرفر متفاعل ومدمج بدون روابط خارجية */
    .cyber-loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 30px;
        margin-bottom: 30px;
    }

    .cyber-spinner {
        position: relative;
        width: 120px;
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .cyber-ring {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 4px solid transparent;
        border-top-color: #00f2fe;
        animation: spin3d 2s linear infinite;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.5);
    }

    .cyber-ring-2 {
        position: absolute;
        width: 80%;
        height: 80%;
        border-radius: 50%;
        border: 4px solid transparent;
        border-bottom-color: #ff007f;
        animation: spin3d-reverse 1.5s linear infinite;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.5);
    }

    .cyber-core {
        width: 45px;
        height: 45px;
        background: #0f172a;
        border: 2px solid #38bdf8;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 0 20px #00f2fe;
        animation: pulseCore 1.5s ease-in-out infinite alternate;
    }

    @keyframes spin3d {
        0% { transform: rotateX(45deg) rotateY(0deg) rotateZ(0deg); }
        100% { transform: rotateX(45deg) rotateY(360deg) rotateZ(360deg); }
    }

    @keyframes spin3d-reverse {
        0% { transform: rotateX(45deg) rotateY(360deg) rotateZ(0deg); }
        100% { transform: rotateX(45deg) rotateY(0deg) rotateZ(-360deg); }
    }

    @keyframes pulseCore {
        0% { transform: scale(0.9); box-shadow: 0 0 10px #00f2fe; }
        100% { transform: scale(1.1); box-shadow: 0 0 25px #ff007f; }
    }

    .cyber-text {
        color: #38bdf8;
        font-size: 0.95rem;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
        margin-top: 20px;
        text-align: center;
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

# 3. الواجهة الرئيسية
st.title("⚡ RIVEN | Cyber Stock Engine")
st.markdown("<div class='sub-title'>المحرك الذكي لتحليل وتطابق استوك الفروع والتحضير</div>", unsafe_allow_html=True)

# 4. رفع الملف
uploaded_file = st.file_uploader("", type=["xlsx"])

# 5. عرض الشاشة الافتتاحية المتحركة 3D
if uploaded_file is None:
    st.markdown("""
        <div class="cyber-loader-container">
            <div class="cyber-spinner">
                <div class="cyber-ring"></div>
                <div class="cyber-ring-2"></div>
                <div class="cyber-core">💻</div>
            </div>
            <div class="cyber-text">⚡ النظام بانتظار رفع شيت الإكسيل للبدء في المعالجة...</div>
        </div>
    """, unsafe_allow_html=True)

# 6. معالجة البيانات وأنيميشن التحميل عند رفع الملف
else:
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
