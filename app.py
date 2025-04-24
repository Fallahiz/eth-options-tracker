import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ETH Options Strategy Tracker", layout="wide")
st.title("📈 Ethereum Options Strategy Tracker")

# Load or initialize data
def load_data():
    try:
        return pd.read_csv("eth_options_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "ETH_Price", "Call_Strike", "Call_Premium",
                                     "Put_Strike", "Put_Premium", "Net_Premium", "Total_Net_Income", "Status"])

# Save data to file
def save_data(df):
    df.to_csv("eth_options_data.csv", index=False)

# Load existing data
data = load_data()

# Input form
st.sidebar.header("➕ Add New Entry")
with st.sidebar.form("entry_form"):
    date = st.date_input("Date", value=datetime.today())
    eth_price = st.number_input("ETH Price", min_value=0.0, value=3000.0)
    call_strike = st.number_input("Call Strike", min_value=0.0, value=3300.0)
    call_premium = st.number_input("Call Premium", min_value=0.0, value=120.0)
    put_strike = st.number_input("Put Strike", min_value=0.0, value=2500.0)
    put_premium = st.number_input("Put Premium", min_value=0.0, value=50.0)
    status = st.selectbox("Status", ["Open", "Closed"])
    submit = st.form_submit_button("Add Entry")

    if submit:
        net_premium = call_premium - put_premium
        total_net_income = net_premium * 2  # for 2 ETH
        new_entry = {
            "Date": date,
            "ETH_Price": eth_price,
            "Call_Strike": call_strike,
            "Call_Premium": call_premium,
            "Put_Strike": put_strike,
            "Put_Premium": put_premium,
            "Net_Premium": net_premium,
            "Total_Net_Income": total_net_income,
            "Status": status
        }
        data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)
        save_data(data)
        st.success("✅ Entry added successfully!")

# Display data
st.subheader("📊 Strategy History")
st.dataframe(data.sort_values(by="Date", ascending=False), use_container_width=True)

# Summary
total_income = data["Total_Net_Income"].sum()
st.metric("Total Net Premium Income (USD)", f"${total_income:.2f}")
