import streamlit as st
import pandas as pd
import io

# 1. إعدادات الصفحة المتقدمة مع أيقونة
st.set_page_config(
    page_title="نظام مطابقة الاستوك والتحضير - ريـفن",
    page_icon="📦",
    layout="wide"
)

# 2. إضافة تنسيقات CSS مخصصة للتصميم الملون والرسوم المتحركة
st.markdown("""
    <style>
    /* التنسيق الأساسي والاتجاه */
    .main { text-align: right; direction: rtl; }
    
    /* تنسيق الكروت الإحصائية (المقاييس) مع تأثير الحركة */
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 16px; color: #555; }
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #ddd;
    }

    /* تأثير النبض المتحرك للكروت عند التحميل أو التركيز */
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        50% { transform: scale(1.03); box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2); }
        100% { transform: scale(1); box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
    }
    div[data-testid="stMetric"]:hover {
        animation: pulse 1s infinite;
        border-color: #f7a072; /* لون برتقالي عند التمرير */
    }

    /* تنسيق الأزرار باللون النعناعي */
    .stButton>button {
        background-color: #a3ead1 !important; /* لون نعناعي ريـفن */
        color: #333 !important;
        border-radius: 20px !important;
        border: none !important;
        font-weight: bold !important;
        transition: transform 0.2s ease, background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #f7a072 !important; /* لون برتقالي عند التمرير */
        transform: scale(1.05);
    }
    
    /* تنسيق حاوية رفع الملف */
    div[data-testid="stFileUploadDropzone"] {
        border: 2px dashed #a3ead1;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    
    /* تنسيق العناوين */
    h1 { color: #333; margin-bottom: 20px; }
    h3 { color: #555; margin-top: 30px; }
    
    /* إضافة لون برتقالي للتنبيهات */
    div.stAlert {
        border-color: #f7a072;
        background-color: #fffaf0;
    }
    </style>
""", unsafe_allow_html=True)

# 3. العنوان الرئيسي والأيقونة
st.title("📦 نظام إدارة تحضير الفروع ومطابقة الاستوك")
st.write("قم برفع ملف الإكسيل الموحد (يحتوي على شيت التحضير وشيت الاستوك) للحصول على التحليلات.")

# 4. حاوية رفع الملف بتنسيق مخصص
with st.container():
    st.markdown("### 📥 1. اختر ملف الإكسيل (.xlsx)")
    uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file is not None:
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

        # كروت إحصائية سريعة بتنسيق محسّن
        total_items = len(df_prep)
        shortage_items = (df_prep['diff'] < 0).sum()
        
        st.markdown("### 📊 2. لمحة سريعة")
        with st.container():
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(label="📦 إجمالي الأصناف والمقاسات", value=f"{total_items:,}")
            with c2:
                # لون برتقالي للتنبيه
                st.metric(label="⚠️ الأصناف التي بها عجز (الرصيد لا يكفي)", value=f"{shortage_items:,}", delta_color="inverse")
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

        st.dataframe(df_shortage[['Item-Size', 'Item', 'Size', 'qty', 'stock', 'diff'] + branch_cols], use_container_width=True)

        st.markdown("---")

        # 6. تصدير الشيت النهائي
        st.subheader("✅ 4. تصدير الشيت النهائي المعتمد للتحضير")
        st.warning("بعد مراجعة وتعديل الكميات المطلوب خصمها من الفروع، اضغط هنا لتنزيل كشف التحضير النهائي.")
        
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
        st.error(f"حدث خطأ أثناء قراءة البيانات: {e}")
