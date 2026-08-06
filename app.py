import streamlit as st
import pandas as pd
import io

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Riven",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. تصميم CSS متطور وتثبيت الأعمدة (Sticky Columns) بدون مكتبات خارجية
st.markdown("""
    <style>
    .stApp {
        background-color: #080b11 !important;
        color: #e2e8f0 !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        direction: rtl;
    }

    /* مستطيل الرفع نيون */
    div[data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #0f172a !important;
        border: 2px dashed #00f2fe !important;
        border-radius: 16px !important;
        box-shadow: 0 0 18px rgba(0, 242, 254, 0.25) !important;
        transition: all 0.3s ease-in-out !important;
        padding: 15px !important;
    }

    div[data-testid="stFileUploaderDropzone"] button,
    section[data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, #00f2fe 0%, #00b4d8 100%) !important;
        color: #080b11 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.5) !important;
    }

    /* بنر Riven التفاعلي */
    .riven-success-banner {
        background: linear-gradient(90deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 1px solid #00f2fe;
        border-radius: 14px;
        padding: 14px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.35);
        position: relative;
        overflow: hidden;
        animation: pulseBanner 2.5s infinite alternate;
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

    /* مؤشرات الليد */
    .led-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px currentColor;
    }
    .led-blue { background-color: #00f2fe; color: #00f2fe; animation: blink 1.2s infinite alternate; }
    .led-red { background-color: #ff007f; color: #ff007f; animation: blink 0.8s infinite alternate; }
    .led-green { background-color: #00ff88; color: #00ff88; animation: blink 1.5s infinite alternate; }

    @keyframes blink {
        0% { opacity: 0.3; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1.2); box-shadow: 0 0 15px currentColor; }
    }

    @keyframes pulseBanner {
        0% { border-color: #00f2fe; box-shadow: 0 0 15px rgba(0, 242, 254, 0.2); }
        100% { border-color: #38bdf8; box-shadow: 0 0 25px rgba(0, 242, 254, 0.6); }
    }

    /* عنوان Dashboard بالإنجليزية */
    .dashboard-header {
        color: #00f2fe;
        font-size: 1.6rem;
        font-weight: 900;
        letter-spacing: 3px;
        margin-top: 20px;
        margin-bottom: 15px;
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.4);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* تصاميم كروت الإحصائيات */
    .custom-card {
        background: #0f172a;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
        position: relative;
        transition: all 0.3s ease;
    }

    .card-normal {
        border: 1px solid rgba(0, 242, 254, 0.3);
        box-shadow: 0 4px 20px rgba(0, 242, 254, 0.12);
    }

    .card-warning {
        border: 1px solid rgba(255, 0, 127, 0.4);
        box-shadow: 0 4px 20px rgba(255, 0, 127, 0.15);
    }

    .card-title {
        color: #cbd5e1 !important;
        font-size: 0.95rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }

    .card-value-blue {
        color: #00f2fe !important;
        font-size: 2rem;
        font-weight: 800;
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.4);
    }

    .card-value-red {
        color: #ff007f !important;
        font-size: 2rem;
        font-weight: 800;
        text-shadow: 0 0 12px rgba(255, 0, 127, 0.5);
    }

    .section-title {
        color: #f8fafc;
        font-size: 1.15rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    /* أزرار التحميل */
    div[data-testid="stDownloadButton"]>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #080b11 !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        font-size: 0.95rem !important;
        padding: 8px 20px !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.3) !important;
    }

    /* خاصية تثبيت الأعمدة الأولى أثناء التمرير الأفقي للجدول */
    div[data-testid="stDataFrame"] table th:nth-child(-n+6),
    div[data-testid="stDataFrame"] table td:nth-child(-n+6) {
        position: sticky !important;
        left: 0 !important;
        z-index: 2 !important;
        background-color: #0f172a !important;
        border-right: 1px solid rgba(0, 242, 254, 0.2) !important;
    }
    div[data-testid="stDataFrame"] table th:nth-child(-n+6) {
        z-index: 3 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. كارت Riven العلوي
st.markdown("""
    <div class="riven-success-banner">
        <div class="riven-banner-title">
            <span class="led-dot led-green"></span>
            Riven
            <span class="led-dot led-blue"></span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 4. رفع الملف
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file is not None:
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

        # ضبط وإجبار أنواع البيانات لمنع أي تداخل بين الأرقام والمقاسات عند التصدير
        df_prep['Item-Size'] = df_prep['Item-Size'].astype(str)
        df_prep['Item'] = df_prep['Item'].astype(str)
        df_prep['Size'] = df_prep['Size'].astype(str)

        total_items = len(df_prep)
        shortage_items = (df_prep['diff'] < 0).sum()

        # DASHBOARD
        st.markdown("<div class='dashboard-header'><span class='led-dot led-blue'></span> DASHBOARD</div>", unsafe_allow_html=True)
        
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
                    <div class="card-title"><span class="led-dot led-red"></span> أصناف العجز</div>
                    <div class="card-value-red">{shortage_items:,}</div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div class="custom-card card-normal">
                    <div class="card-title"><span class="led-dot led-green"></span> عدد الفروع</div>
                    <div class="card-value-blue">{len(branch_cols)} فرع</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ترتيب الأعمدة لتكون الأعمدة المقتطعة في البداية
        export_cols = ['Item-Size', 'Item', 'Size', 'qty', 'stock', 'diff'] + branch_cols
        df_shortage = df_prep[df_prep['diff'] < 0][export_cols].copy()

        # الأصناف التي بها عجز
        st.markdown("<div class='section-title'><span class='led-dot led-red'></span> الأصناف التي بها عجز رصيد</div>", unsafe_allow_html=True)

        # زر تحميل كشف العجز
        buffer_shortage = io.BytesIO()
        with pd.ExcelWriter(buffer_shortage, engine='openpyxl') as writer:
            df_shortage.to_excel(writer, index=False, sheet_name='تقرير_العجز')

        st.download_button(
            label="تحميل كشف العجز (Excel)",
            data=buffer_shortage.getvalue(),
            file_name="تقرير_العجز_والفروقات.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # عرض الجدول الأصلي من Streamlit مع تطبيق التثبيت عبر CSS
        st.dataframe(df_shortage, use_container_width=True, height=420)

        st.markdown("---")

        # الشيت النهائي للتحضير
        st.markdown("<div class='section-title'><span class='led-dot led-green'></span> الشيت النهائي للتحضير</div>", unsafe_allow_html=True)
        
        buffer_final = io.BytesIO()
        with pd.ExcelWriter(buffer_final, engine='openpyxl') as writer:
            df_prep[export_cols].to_excel(writer, index=False, sheet_name='التحضير_النهائي')

        st.download_button(
            label="تحميل الشيت النهائي الكامل (Excel)",
            data=buffer_final.getvalue(),
            file_name="الخطه_النهائيه_للكشوفات.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة البيانات: {e}")
