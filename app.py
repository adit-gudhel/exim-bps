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
kodehs = st.text_input("HS Code (use ; for multiple)", "10")
jenishs = st.selectbox("Jenis HS Code", [("1", "Two Digit"), ("2", "Full HS Code")], format_func=lambda x: x[1])[0]
tahun = st.text_input("Tahun Data", "2024")
api_key = st.text_input("API Key", type="password")

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
        data = response.json()

        if "data" in data:
            df = pd.DataFrame(data["data"])

            st.success("✅ Data retrieved successfully!")
            st.dataframe(df)

            # Download as Excel
            output = BytesIO()
            df.to_excel(output, index=False)
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
