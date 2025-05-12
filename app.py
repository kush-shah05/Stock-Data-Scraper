import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io

st.set_page_config(page_title="📈 Stock Data Scraper", layout="centered")

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Initialize session state
if "stock_memory" not in st.session_state:
    st.session_state.stock_memory = {}

def get_stock_data(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    data = {}
    table = soup.find("table", class_="snapshot-table2")
    if not table:
        return {}

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        for i in range(0, len(cells), 2):
            key = cells[i].text.strip()
            value = cells[i + 1].text.strip()
            data[key] = value
    return data

# --- UI ---
st.title("📊 Finviz Stock Data Scraper")

ticker = st.text_input("Enter Stock Ticker Symbol (e.g., TSLA, AAPL):", "").upper()

if ticker:
    stock_data = get_stock_data(ticker)

    if stock_data:
        st.success("✅ Data fetched successfully!")

        all_keys = list(stock_data.keys())
        selected_keys = st.multiselect("Select data fields to include:", all_keys)

        if selected_keys:
            # Update stored memory for this ticker
            for key in selected_keys:
                value = stock_data.get(key, "")
                if ticker not in st.session_state.stock_memory:
                    st.session_state.stock_memory[ticker] = {}
                st.session_state.stock_memory[ticker][key] = value

            # Display updated memory
            st.subheader(f"📋 Stored Data for {ticker}")
            for k, v in st.session_state.stock_memory[ticker].items():
                st.write(f"**{k}**: {v}")

            # Create DataFrame for download
            df = pd.DataFrame([st.session_state.stock_memory[ticker]], index=[ticker]).astype("string")

            buffer = io.BytesIO()
            df.to_excel(buffer, engine='openpyxl')
            buffer.seek(0)

            st.download_button(
                label="📥 Download Excel",
                data=buffer,
                file_name=f"{ticker}_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error("❌ Failed to fetch data. Please check the ticker.")
