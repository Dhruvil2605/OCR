import streamlit as st
import requests
import base64
import io
import pandas as pd
import time

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwHpGYeL_jMR45vvor9l3mXYawzE3BhF8vrNtIWvMeMtqSzMhhSN-pOquxyFVTHvcrnfA/exec"

st.title("📤 Upload → ⏳ Wait → 📊 Auto Show Excel")

uploaded_file = st.file_uploader("Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    st.success(f"✅ File selected: {uploaded_file.name}")
    if st.button("Upload and Fetch Excel After 2 Minutes"):
        try:
            # Encode file to base64
            file_bytes = uploaded_file.read()
            encoded = base64.b64encode(file_bytes).decode("utf-8")

            # POST to Apps Script
            res = requests.post(SCRIPT_URL, json={
                "filename": uploaded_file.name,
                "file": encoded
            })

            if res.status_code == 200 and res.json().get("success"):
                st.success("✅ Uploaded to Google Drive")
                st.info("⏳ Waiting 2 minutes for Excel to appear...")
                time.sleep(120)

                # GET from Apps Script
                fetch = requests.get(SCRIPT_URL)
                result = fetch.json()

                if result.get("success"):
                    st.info(f"📄 Excel: {result['filename']}")
                    file_bytes = base64.b64decode(result["file"])
                    df = pd.read_excel(io.BytesIO(file_bytes))
                    st.success("✅ Excel fetched successfully!")
                    st.dataframe(df)
                else:
                    st.warning("⚠️ No Excel file found.")

            else:
                st.error(f"❌ Upload failed: {res.json().get('error')}")

        except Exception as e:
            st.error(f"❌ Error: {e}")
