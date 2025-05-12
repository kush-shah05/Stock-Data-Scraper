import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import os

st.set_page_config(page_title="📈 Stock Data Scraper", layout="centered")

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Load from disk on app start (only once)
if "stock_table" not in st.session_state:
    if os.path.exists("all_stock_data.xlsx"):
        st.session_state.stock_table = pd.read_excel("all_stock_data.xlsx", index_col=0).astype("string")
    else:
        st.session_state.stock_table = pd.DataFrame()

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

# --- UI starts here ---
st.title("📊 Finviz Stock Data Scraper")

ticker = st.text_input("Enter Stock Ticker Symbol (e.g., TSLA, AAPL):", "").upper()

if ticker:
    stock_data = get_stock_data(ticker)

    if stock_data:
        st.success("✅ Data fetched successfully!")

        all_keys = list(stock_data.keys())
        selected_keys = st.multiselect("Select data fields to include:", all_keys)

        if selected_keys:
            selected_data = {key: stock_data.get(key, "") for key in selected_keys}
            df = pd.DataFrame([selected_data], index=[ticker]).astype("string")

            existing = st.session_state.stock_table

            if ticker in existing.index:
                for col in selected_data:
                    existing.loc[ticker, col] = str(selected_data[col])
            else:
                existing = pd.concat([existing, df])

            for col in df.columns:
                if col not in existing.columns:
                    existing[col] = None
                    existing.loc[ticker, col] = str(df[col].iloc[0])

            st.session_state.stock_table = existing

            # 🔥 Save to disk persistently
            st.session_state.stock_table.to_excel("all_stock_data.xlsx")

            st.success(f"✅ Data for {ticker} saved and stored locally!")

# Show and download
if not st.session_state.stock_table.empty:
    st.markdown("### 🧾 All Stored Stock Data")
    st.dataframe(st.session_state.stock_table)

    buffer = io.BytesIO()
    st.session_state.stock_table.to_excel(buffer, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="📥 Download Full Excel Sheet",
        data=buffer,
        file_name="all_stock_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
