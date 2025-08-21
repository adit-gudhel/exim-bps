import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# API Base URL
BASE_URL = "https://webapi.bps.go.id/v1/api/dataexim"

st.title("📊 BPS Foreign Trade Data (Export & Import)")

# Input fields
sumber = st.selectbox("Sumber Data", [("1", "Export"), ("2", "Import")], format_func=lambda x: x[1])[0]
periode = st.selectbox("Periode Data", [("1", "Monthly"), ("2", "Annually")], format_func=lambda x: x[1])[0]
kodehs = st.text_input("HS Code (use ; for multiple)", "26011190")
jenishs = st.selectbox("Jenis HS Code", [("1", "Two Digit"), ("2", "Full HS Code")], format_func=lambda x: x[1])[0]
tahun = st.text_input("Tahun Data", "2019")
api_key = st.text_input("API Key", type="password")


# Transformation function
def transform_api_response(raw_df, sumber):
    # Split kodehs into HSCode and ProductName
    raw_df[["HSCode", "ProductName"]] = raw_df["kodehs"].str.extract(r"\[(\d+)\]\s*(.*)")

    # Extract month number from [xx] text
    raw_df["Month"] = raw_df["bulan"].str.extract(r"\[(\d+)\]").astype(int)

    rows = []
    for _, row in raw_df.iterrows():
        base = {
            "Month": row["Month"],
            "Year": row["tahun"],
            "CommodityName": "Mineral",
            "ProductName": row["ProductName"],
            "LocationName": "Indonesia",
            "Typ": "Export" if sumber == "1" else "Import",
            "Classificat": "-",
            "HSCode": row["HSCode"],
            "Source": "BPS",
            "HSCodeReference": "HS Code Master 2022-Now",
            "Country": row["ctr"],
            "Pelabuhan": row["pod"]
        }

        # Amount row
        rows.append({
            **base,
            "Name": "Amount",
            "Value": row["value"],
            "Unit": "USD"
        })

        # Netweight row
        rows.append({
            **base,
            "Name": "Netweight",
            "Value": row["netweight"],
            "Unit": "KG"
        })

    df_final = pd.DataFrame(rows)

    # Ensure consistent column order
    column_order = [
        "Name", "Month", "Year", "CommodityName", "ProductName", "LocationName",
        "Typ", "Classificat", "Value", "Unit", "HSCode", "Source",
        "HSCodeReference", "Country", "Pelabuhan"
    ]
    df_final = df_final[column_order]

    return df_final


if st.button("Get Data"):
    params = {
        "sumber": sumber,
        "periode": periode,
        "kodehs": kodehs,
        "jenishs": jenishs,
        "tahun": tahun,
        "key": api_key
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception:
            st.error("❌ Response is not JSON. Raw response below:")
            st.text(response.text)
            st.stop()

        if "data" in data:
            raw_df = pd.DataFrame(data["data"])
            df_final = transform_api_response(raw_df, sumber)

            st.success("✅ Data retrieved successfully!")
            st.dataframe(df_final)

            # Download as Excel
            output = BytesIO()
            df_final.to_excel(output, index=False)
            output.seek(0)

            st.download_button(
                label="📥 Download as Excel",
                data=output,
                file_name="foreign_trade_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ No 'data' field found in response. Check API result.")
    else:
        st.error(f"❌ Error {response.status_code}: {response.text}")
