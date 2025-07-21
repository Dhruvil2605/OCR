import streamlit as st
import requests
import base64
import io
import time

# Google Apps Script Web App URL
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxC29yxnH1dMYEkI_CYNR-Cgr_GiEfO7KHIT9zBH_W0Gu4h5U62vMOMKmiC5u45YIDa/exec"

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

# Session state flags
if "upload_started" not in st.session_state:
    st.session_state.upload_started = False
if "upload_disabled" not in st.session_state:
    st.session_state.upload_disabled = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# File uploader (disabled after upload starts)
file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], disabled=st.session_state.upload_disabled)

# Save uploaded file in session state
if file and not st.session_state.upload_started:
    st.session_state.uploaded_file = file
    st.success(f"✅ File selected: {file.name}")

# Upload button only appears after file is selected
def handle_upload():
    st.session_state.upload_started = True
    st.session_state.upload_disabled = True

if st.session_state.uploaded_file and not st.session_state.upload_disabled:
    st.button("📤 Upload Image", disabled=st.session_state.upload_disabled, on_click=handle_upload)

# Function to check for the PDF
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

# Start upload and processing after first click
if st.session_state.upload_started and st.session_state.uploaded_file:
    try:
        st.info("⏳ Uploading and processing file... Please wait.")
        file_bytes = st.session_state.uploaded_file.read()
        encoded = base64.b64encode(file_bytes).decode("utf-8")

        # Upload to Apps Script
        res = requests.post(SCRIPT_URL, json={
            "filename": st.session_state.uploaded_file.name,
            "file": encoded
        })

        if res.status_code == 200 and res.json().get("success"):
            st.success("✅ Uploaded successfully.")
            st.info("⏳ File is been processed please wait for some time.")

            time.sleep(180)

            # Check for PDF until available
            while True:
                if check_file():
                    break
                time.sleep(10)

        else:
            st.error(f"❌ Upload failed: {res.json().get('error')}")

    except Exception as e:
        st.error(f"❌ Upload Error: {e}")

    # Reset everything after done
    st.session_state.upload_started = False
    st.session_state.upload_disabled = False
    st.session_state.uploaded_file = None
