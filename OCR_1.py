import streamlit as st
import requests
import base64
import io
import time

# Web App URL of Google Apps Script
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxC29yxnH1dMYEkI_CYNR-Cgr_GiEfO7KHIT9zBH_W0Gu4h5U62vMOMKmiC5u45YIDa/exec"

st.set_page_config(page_title="OCR Portal", layout="centered")
st.title("📤 OCR Project")

# Hide GitHub and menu
st.markdown("""
    <style>
    [data-testid="stToolbar"] a[href^="https://github.com"],
    header [data-testid="stMarkdownContainer"] + div a {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

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

if uploaded_file:
    st.success(f"✅ File selected: {uploaded_file.name}")
    if st.button("📤 Upload Image"):
        try:
            file_bytes = uploaded_file.read()
            encoded = base64.b64encode(file_bytes).decode("utf-8")

            res = requests.post(SCRIPT_URL, json={
                "filename": uploaded_file.name,
                "file": encoded
            })

            if res.status_code == 200 and res.json().get("success"):
                st.success("✅ File uploaded successfully")
                st.info("⏳ File is been processed please wait for some time.")
                time.sleep(180)

                try:
                    while True:
                        if check_file():
                            break
                        time.sleep(10)

                except Exception as e:
                    st.error(f"❌ Error while fetching PDF: {e}")
            else:
                st.error(f"❌ Upload failed: {res.json().get('error')}")
        except Exception as e:
            st.error(f"❌ Upload Error: {e}")

