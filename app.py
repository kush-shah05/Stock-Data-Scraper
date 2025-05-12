import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# --- Config ---
st.set_page_config(page_title="Stock Data Scraper", layout="centered")
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}


# --- Get stock data from Finviz ---
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


# --- Streamlit App ---
st.title("📊 Finviz Stock Data Scraper")

ticker = st.text_input("Enter Stock Ticker Symbol (e.g., TSLA, AAPL):", "").upper()

if ticker:
    stock_data = get_stock_data(ticker)

    if stock_data:
        st.success("Data fetched successfully!")

        all_keys = list(stock_data.keys())
        selected_keys = st.multiselect("Select data fields to view/save:", all_keys)

        if selected_keys:
            st.subheader(f"Selected Data for {ticker}")
            for key in selected_keys:
                st.write(f"**{key}**: {stock_data.get(key, '❌ Not found')}")

            if st.button("Save to Excel and CSV"):
                selected_data = {key: stock_data.get(key, "") for key in selected_keys}
                df = pd.DataFrame([selected_data], index=[ticker]).astype("string")

                excel_path = "stock_data.xlsx"
                csv_path = "stock_data.csv"

                if os.path.exists(excel_path):
                    existing_df = pd.read_excel(excel_path, index_col=0).astype("string")

                    if ticker in existing_df.index:
                        for col in selected_data:
                            existing_df.loc[ticker, col] = str(selected_data[col])
                    else:
                        existing_df = pd.concat([existing_df, df])

                    for col in df.columns:
                        if col not in existing_df.columns:
                            existing_df[col] = None
                            existing_df.loc[ticker, col] = str(df[col].iloc[0])

                    existing_df.to_excel(excel_path)
                    existing_df.to_csv(csv_path)
                else:
                    df.to_excel(excel_path)
                    df.to_csv(csv_path)

                st.success(f"✅ Saved to `{excel_path}` and `{csv_path}`")

    else:
        st.error("❌ Failed to fetch data. Check the ticker symbol.")
