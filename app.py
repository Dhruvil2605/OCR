import streamlit as st
import requests
import base64
import io
import time
import pandas as pd
import plotly.graph_objects as go


# ✅ CONFIGURATION
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxC29yxnH1dMYEkI_CYNR-Cgr_GiEfO7KHIT9zBH_W0Gu4h5U62vMOMKmiC5u45YIDa/exec"
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1COJSrxQDnsMYreNZOlwUv6-81I4bxEeX/export?format=csv"


# ✅ FUNCTION TO CREATE GAUGE CHART
def create_gauge(title, value, max_value, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': color},
            'bgcolor': "white",
            'steps': [{'range': [0, max_value], 'color': 'lightgray'}],
        }
    ))
    fig.update_layout(margin={'t': 50, 'b': 0, 'l': 0, 'r': 0}, height=300)
    return fig


# ✅ STREAMLIT UI CONFIG
st.set_page_config(page_title="OCR Portal", layout="centered")
st.title("📤 OCR Project")

# Hide GitHub & menu
st.markdown("""
    <style>
    [data-testid="stToolbar"] a[href^="https://github.com"],
    header [data-testid="stMarkdownContainer"] + div a {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)


# ✅ SESSION STATE
if "upload_started" not in st.session_state:
    st.session_state.upload_started = False
if "upload_disabled" not in st.session_state:
    st.session_state.upload_disabled = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None


# ✅ FILE UPLOADER
file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], disabled=st.session_state.upload_disabled)

if file and not st.session_state.upload_started:
    st.session_state.uploaded_file = file
    st.success(f"✅ File selected: {file.name}")


def handle_upload():
    st.session_state.upload_started = True
    st.session_state.upload_disabled = True


if st.session_state.uploaded_file and not st.session_state.upload_disabled:
    st.button("📤 Upload Image", disabled=st.session_state.upload_disabled, on_click=handle_upload)


# ✅ PDF CHECK FUNCTION
def check_file():
    fetch_res = requests.get(SCRIPT_URL)
    result = fetch_res.json()
    if result.get("success") and result.get("file"):
        st.success(f"✅ PDF '{result['filename']}' fetched.")
        pdf_bytes = base64.b64decode(result["file"])
        pdf_buffer = io.BytesIO(pdf_bytes)
        st.download_button(
            label="📄 Download PDF",
            data=pdf_buffer,
            file_name=result["filename"],
            mime="application/pdf",
            key=f"download-{result['filename']}-{time.time()}"
        )
        return True
    return False


# ✅ MAIN PROCESS FLOW
if st.session_state.upload_started and st.session_state.uploaded_file:
    try:
        st.info("⏳ Uploading and processing file... Please wait.")
        file_bytes = st.session_state.uploaded_file.read()
        encoded = base64.b64encode(file_bytes).decode("utf-8")

        res = requests.post(SCRIPT_URL, json={
            "filename": st.session_state.uploaded_file.name,
            "file": encoded
        })

        if res.status_code == 200 and res.json().get("success"):
            st.success("✅ Uploaded successfully.")
            st.info("⏳ File is being processed, please wait...")

            time.sleep(5)
            while True:
                if check_file():
                    break
                time.sleep(10)

            # ✅ FETCH GOOGLE SHEETS DATA (CSV FORMAT)
            df = pd.read_csv(GOOGLE_SHEET_CSV_URL, header=None)
            height_value = float(df.iloc[0, 1])     # Row 1, Column B
            discharge_value = float(df.iloc[1, 1])  # Row 2, Column B

            # ✅ DISPLAY GAUGES
            st.markdown("---")
            st.subheader("📊 Data Visualization:")

            col1, col2 = st.columns(2)

            with col1:
                height_fig = create_gauge("Height", height_value, 20, "orange")
                st.plotly_chart(height_fig)

            with col2:
                discharge_fig = create_gauge("Discharge in M3", discharge_value, 200000, "gold")
                st.plotly_chart(discharge_fig)

        else:
            st.error(f"❌ Upload failed: {res.json().get('error')}")

    except Exception as e:
        st.error(f"❌ Upload Error: {e}")

    # Reset session state
    st.session_state.upload_started = False
    st.session_state.upload_disabled = False
    st.session_state.uploaded_file = None