import streamlit as st
import pandas as pd
import io
import time

# 1. إعدادات الصفحة الاحترافية (Custom Icon and Theme-aware Title)
st.set_page_config(
    page_title="ريـفن | نظام التحضير الذكي",
    page_icon="📦",
    layout="wide"
)

# 2. منطقة الـ CSS السحرية (Sleek, Modern, Animated Theme)
st.markdown("""
    <style>
    /* الاتجاه الأساسي للنص (RTL) */
    .main { text-align: right; direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* تنسيق العنوان الرئيسي مع أنيميشن عند التحميل */
    h1 {
        color: #333;
        font-weight: 800;
        margin-bottom: 25px;
        border-right: 5px solid #a3ead1; /* لون نعناعي ريـفن */
        padding-right: 15px;
        animation: fadeInRight 0.8s ease-out;
    }
    @keyframes fadeInRight {
        0% { opacity: 0; transform: translateX(20px); }
        100% { opacity: 1; transform: translateX(0); }
    }

    /* تنسيق الوصف الفرعي */
    .stMarkdown p { font-size: 1.1em; color: #555; }

    /* تنسيق حاوية رفع الملفات (Upload Zone) */
    div[data-testid="stFileUploadDropzone"] {
        border: 2px dashed #a3ead1;
        border-radius: 15px;
        background-color: #f9fdfc;
        transition: all 0.3s ease;
        padding: 20px;
        animation: slideUp 0.6s ease-out;
    }
    @keyframes slideUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    div[data-testid="stFileUploadDropzone"]:hover {
        border-color: #f7a072; /* لون برتقالي عند التمرير */
        background-color: #fff9f6;
        box-shadow: 0 4px 15px rgba(247, 160, 114, 0.1);
    }
    div[data-testid="stFileUploadDropzone"] div[class*="StyledFileUploadDescription"] {
        color: #f7a072 !important;
        font-weight: bold;
    }

    /* تنسيق كروت الإحصائيات (Metrics) مع أنيميشن تفاعلي */
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        color: #7f8c8d !important;
    }
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #eee;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: popIn 0.5s ease-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
        border-color: #a3ead1;
    }
    @keyframes popIn {
        0% { transform: scale(0.9); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    /* لون مخصص للأصناف التي بها عجز (برتقالي تنبيهي) */
    div[data-testid="stMetricValue"] span[class*="st-emotion-cache"] {
        color: #e67e22 !important;
    }

    /* تنسيق الأزرار (Buttons) الاحترافية */
    .stButton>button {
        background-color: #a3ead1 !important; /* لون نعناعي ريـفن */
        color: #333 !important;
        border-radius: 25px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1.1em !important;
        padding: 10px 25px !important;
        transition: background-color 0.3s ease, transform 0.2s ease;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(163, 234, 209, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(163, 234, 209, 0); }
        100% { box-shadow: 0 0 0 0 rgba(163, 234, 209, 0); }
    }
    .stButton>button:hover {
        background-color: #f7a072 !important; /* لون برتقالي عند التمرير */
        transform: scale(1.03);
        animation: none;
    }

    /* تنسيق حاوية الشيت (DataFrame) والديناميكية */
    div[data-testid="stDataFrameContainer"] {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.03);
        border: 1px solid #f0f0f0;
        animation: slideUp 0.7s ease-out;
    }

    /* تنسيق العناوين الفرعية (Subheaders) */
    h3 {
        color: #333;
        margin-top: 35px;
        font-weight: 700;
        animation: slideUp 0.6s ease-out;
    }
    
    /* شريط النجاح المخصص */
    div.stAlert[data-testid="stAlert"] {
        border-radius: 10px;
        background-color: #f3fdf9;
        color: #1e7051;
        border: 1px solid #a3ead1;
    }
    </style>
""", unsafe_allow_html=True)

# 3. محتوى الصفحة (Title and Description)
st.title("📦 ريـفن | نظام إدارة تحضير الفروع ومطابقة الاستوك الذكي")
st.write("قم برفع ملف الإكسيل الموحد (يحتوي على شيت التحضير وشيت الاستوك) للحصول على تحليل فوري، ديناميكي، ومبهر.")

# 4. حاوية رفع الملف
with st.container():
    st.markdown("### 📥 1. اختر ملف الإكسيل (.xlsx)")
    uploaded_file = st.file_uploader("", type=["xlsx"])

# أنيميشن التحميل (Loading State for professional feel)
if uploaded_file is not None:
    with st.spinner("⏳ جاري تحليل البيانات وبناء الواجهة التفاعلية..."):
        time.sleep(1.5) # Fake loading to show off animations and spinner
        try:
            # قراءة الشيتات بناءً على أسمائها في الملف
            df_prep = pd.read_excel(uploaded_file, sheet_name='Reallocation_Plan_ONL_2026-08-0')
            df_stock = pd.read_excel(uploaded_file, sheet_name='ستوك')

            # تحديد أعمدة الفروع الـ 36 تلقائياً
            size_idx = df_prep.columns.get_loc('Size')
            qty_idx = df_prep.columns.get_loc('qty')
            branch_cols = df_prep.columns[size_idx + 1 : qty_idx].tolist()

            # تحديث رصيد المخزن وإعادة حساب الفروقات
            stock_map = df_stock.set_index('Product/Barcode')['Quantity'].to_dict()
            df_prep['stock'] = df_prep['Item-Size'].map(stock_map).fillna(df_prep['stock'])
            df_prep['qty'] = df_prep[branch_cols].sum(axis=1)
            df_prep['diff'] = df_prep['stock'] - df_prep['qty']

            # إشعار نجاح التحميل
            st.success("✅ تم تحميل الملف وتحليل البيانات بنجاح!")
            
            # كروت إحصائية سريعة بتنسيق محسّن
            total_items = len(df_prep)
            shortage_items = (df_prep['diff'] < 0).sum()
            
            st.markdown("### 📊 2. لمحة سريعة")
            with st.container():
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(label="📦 إجمالي الأصناف والمقاسات", value=f"{total_items:,}")
                with c2:
                    st.metric(label="⚠️ الأصناف التي بها عجز (الرصيد لا يكفي)", value=f"{shortage_items:,}")
                with c3:
                    st.metric(label="🛍️ عدد الفروع المشاركة", value=f"{len(branch_cols)} فرع")

            st.markdown("---")

            # 5. منطقة عرض وتحميل نتائج العجز
            st.subheader("⚠️ 3. كشف أصناف العجز المكتشفة (المطلوب > المتاح)")
            df_shortage = df_prep[df_prep['diff'] < 0].copy()

            # زر تحميل شيت الفروقات والعجز فقط
            buffer_shortage = io.BytesIO()
            with pd.ExcelWriter(buffer_shortage, engine='openpyxl') as writer:
                df_shortage.to_excel(writer, index=False, sheet_name='تقرير_العجز')
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.download_button(
                    label="📥 تحميل كشف العجز (Excel)",
                    data=buffer_shortage.getvalue(),
                    file_name="تقرير_العجز_والفروقات.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # عرض شيت العجز (Dataframe with dynamic width and sleek styling)
            st.dataframe(df_shortage[['Item-Size', 'Item', 'Size', 'qty', 'stock', 'diff'] + branch_cols], use_container_width=True)

            st.markdown("---")

            # 6. تصدير الشيت النهائي
            st.subheader("✅ 4. تصدير الشيت النهائي المعتمد للتحضير")
            st.markdown("⚠️ **بعد مراجعة وتعديل الكميات المطلوب خصمها من الفروع، اضغط هنا لتنزيل كشف التحضير النهائي.**")
            
            buffer_final = io.BytesIO()
            with pd.ExcelWriter(buffer_final, engine='openpyxl') as writer:
                df_prep.to_excel(writer, index=False, sheet_name='التحضير_النهائي')

            col1_final, col2_final = st.columns([1, 4])
            with col1_final:
                st.download_button(
                    label="📥 تحميل الشيت النهائي الكامل (Excel)",
                    data=buffer_final.getvalue(),
                    file_name="الخطه_النهائيه_للكشوفات.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة البيانات أو بناء الواجهة: {e}")
            st.write("تأكد من أن أسماء الشيتات وأعمدة الـ " + 
                     "Item-Size, Product/Barcode, Quantity, Size, qty في ملف الإكسيل صحيحة ومطابقة للكود.")
