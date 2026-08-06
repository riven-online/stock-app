import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="نظام مطابقة الاستوك والتحضير",
    page_icon="📦",
    layout="wide"
)

# تنسيق الواجهة باللغة العربية
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div[data-testid="stMetricValue"] { font-size: 24px; }
    </style>
""", unsafe_allow_html=True)

st.title("📦 نظام إدارة تحضير الفروع ومطابقة الاستوك")
st.write("قم برفع ملف الإكسيل الموحد (يحتوي على شيت التحضير وشيت الاستوك).")

# 1. منطقة رفع الملف
uploaded_file = st.file_uploader("اختر ملف الإكسيل (.xlsx)", type=["xlsx"])

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

        # كروت إحصائية سريعة
        total_items = len(df_prep)
        shortage_items = (df_prep['diff'] < 0).sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الأصناف والمقاسات", f"{total_items:,}")
        c2.metric("الأصناف التي بها عجز (الرصيد لا يكفي)", f"{shortage_items:,}", delta_color="inverse")
        c3.metric("عدد الفروع المشاركة", f"{len(branch_cols)} فرع")

        st.markdown("---")

        # 2. عرض الأصناف التي بها عجز
        st.subheader("⚠️ 1. كشف أصناف العجز (المطلوب > المتاح)")
        df_shortage = df_prep[df_prep['diff'] < 0].copy()

        # زر تحميل شيت الفروقات والعجز فقط
        buffer_shortage = io.BytesIO()
        with pd.ExcelWriter(buffer_shortage, engine='openpyxl') as writer:
            df_shortage.to_excel(writer, index=False, sheet_name='تقرير_العجز')
        
        st.download_button(
            label="📥 تصدير شيت الفروقات والعجز فقط (Excel)",
            data=buffer_shortage.getvalue(),
            file_name="تقرير_العجز_والفروقات.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.dataframe(df_shortage[['Item-Size', 'Item', 'Size', 'qty', 'stock', 'diff'] + branch_cols], use_container_width=True)

        st.markdown("---")

        # 3. تصدير الشيت النهائي
        st.subheader("✅ 2. تصدير الشيت النهائي المعتمد للتحضير")
        st.info("بعد مراجعة وتعديل الكميات المطلوب خصمها من الفروع، اضغط هنا لتنزيل كشف التحضير النهائي.")
        
        buffer_final = io.BytesIO()
        with pd.ExcelWriter(buffer_final, engine='openpyxl') as writer:
            df_prep.to_excel(writer, index=False, sheet_name='التحضير_النهائي')

        st.download_button(
            label="📥 تصدير الشيت النهائي الكامل (Excel)",
            data=buffer_final.getvalue(),
            file_name="الخطه_النهائيه_للكشوفات.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة البيانات: {e}")
