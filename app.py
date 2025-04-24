import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import requests
import datetime

# Google Sheets setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
client = gspread.authorize(creds)

SHEET_ID = "1i5c4LXNfI8vmxGbktwDnQxD2vY2FmGCDhBKfUPagROI"
SHEET_NAME = "Sheet1"
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Sidebar input
st.sidebar.title("ثبت معامله جدید")
with st.sidebar.form("trade_form"):
    date = st.date_input("تاریخ", datetime.date.today())
    strike = st.number_input("Strike Price", value=3000.0)
    premium = st.number_input("Premium (ETH)", value=0.05)
    call_put = st.selectbox("نوع", ["Call", "Put"])
    action = st.selectbox("اکشن", ["Buy", "Sell"])
    submitted = st.form_submit_button("ثبت")
    if submitted:
        new_row = [str(date), strike, premium, call_put, action]
        sheet.append_row(new_row)
        st.success("معامله ثبت شد. صفحه را Refresh کن.")

# Deletion section
st.sidebar.title("🗑️ حذف رکورد")
if not df.empty:
    to_delete = st.sidebar.selectbox("رکوردی برای حذف انتخاب کن", df.index.astype(str))
    if st.sidebar.button("حذف رکورد"):
        sheet.delete_rows(int(to_delete)+2)
        st.sidebar.success("رکورد حذف شد. صفحه را Refresh کن.")

st.title("📈 اپ تریکر معاملات آپشن اتریوم")

# Ethereum live price
st.subheader("قیمت لحظه‌ای اتریوم")
try:
    eth_data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd").json()
    eth_price = eth_data["ethereum"]["usd"]
    st.metric("ETH / USD", f"${eth_price}")
except:
    st.error("اتصال به قیمت لحظه‌ای با مشکل مواجه شد.")

# Show data
st.subheader("لیست معاملات")
st.dataframe(df)

# Chart
st.subheader("نمودار معاملات")
if not df.empty:
    chart_df = df.copy()
    chart_df["تاریخ"] = pd.to_datetime(chart_df["تاریخ"])
    fig = px.scatter(chart_df, x="تاریخ", y="Strike Price", color="نوع",
                     size="Premium (ETH)", hover_data=["اکشن"])
    st.plotly_chart(fig, use_container_width=True)