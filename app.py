import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import requests

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(credentials)
sheet = client.open("eth_options_tracker").sheet1

def fetch_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["ethereum"]["usd"]
    except:
        return "Error"

st.title("Ethereum Options Tracker")

# Show ETH price
eth_price = fetch_eth_price()
st.markdown(f"### Current ETH Price: ${eth_price}")

# Load existing data
@st.cache_data

def load_data():
    records = sheet.get_all_records()
    return pd.DataFrame(records)

df = load_data()

# New Record Entry
st.subheader("Add New Option Trade")
with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", datetime.date.today())
        option_type = st.selectbox("Option Type", ["Call", "Put"])
        eth_price = st.number_input("ETH Price", min_value=0.0, value=0.0)
    with col2:
        strike_price = st.number_input("Strike Price", min_value=0.0, value=0.0)
        premium = st.number_input("Premium Paid", min_value=0.0, value=0.0)
        expiration = st.date_input("Expiration Date", datetime.date.today())

    submitted = st.form_submit_button("Add Record")

    if submitted:
        new_row = [str(date), option_type, eth_price, strike_price, premium, str(expiration)]
        sheet.append_row(new_row)
        st.success("Record added successfully!")

# Delete Record
st.subheader("Delete a Record")
if not df.empty:
    df["Index"] = df.index + 1
    selected_index = st.number_input("Enter the Index of the Record to Delete", min_value=1, max_value=len(df), step=1)
    if st.button("Delete Record"):
        sheet.delete_rows(selected_index + 1)  # +1 to account for header
        st.success(f"Record {selected_index} deleted.")

# Show all records
st.subheader("All Records")
st.dataframe(df)
