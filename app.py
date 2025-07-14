import streamlit as st
import requests
import base64
import io
import pandas as pd
import time
import matplotlib.pyplot as plt

# Google Apps Script Web App URL
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwHpGYeL_jMR45vvor9l3mXYawzE3BhF8vrNtIWvMeMtqSzMhhSN-pOquxyFVTHvcrnfA/exec"


# Page setupg
# st.set_page_config(page_title="OCR Project", layout="centered")
# st.title("📤 OCR Project")

st.markdown("""
    <style>
    [data-testid="stToolbar"] a[href^="https://github.com"] {
        display: none !important;
    }
    header [data-testid="stMarkdownContainer"] + div a {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)


# File upload
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

# Generate a PDF that looks like the Excel sheet
def generate_pdf_from_df(df):
    fig, ax = plt.subplots(figsize=(len(df.columns) * 1.2, len(df) * 0.5 + 1))
    ax.axis('off')

    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     cellLoc='center',
                     loc='center',
                     edges='horizontal')

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.2)

    pdf_buffer = io.BytesIO()
    plt.savefig(pdf_buffer, format='pdf', bbox_inches='tight')
    plt.close(fig)
    pdf_buffer.seek(0)
    return pdf_buffer

# Main logic
if uploaded_file:
    st.success(f"✅ File selected: {uploaded_file.name}")
    if st.button("Upload File"):
        try:
            # Encode image
            file_bytes = uploaded_file.read()
            encoded = base64.b64encode(file_bytes).decode("utf-8")

            # Upload to Apps Script
            res = requests.post(SCRIPT_URL, json={
                "filename": uploaded_file.name,
                "file": encoded
            })

            if res.status_code == 200 and res.json().get("success"):
                st.success("✅ File uploaded successfully")
                st.info("⏳ File is been processed please wait for some time.")
                time.sleep(180)
                st.info("⏳ This process will take time to generate exact template... Please wait...")
                time.sleep(120)

                # Fetch Excel
                fetch = requests.get(SCRIPT_URL)
                result = fetch.json()

                if result.get("success"):
                    st.info(f"📄 Excel: {result['filename']}")
                    file_bytes = base64.b64decode(result["file"])
                    df = pd.read_excel(io.BytesIO(file_bytes))
                    st.success("✅ Excel fetched successfully!")
                    st.dataframe(df)

                    # Create PDF that looks like Excel
                    pdf_file = generate_pdf_from_df(df)

                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_file,
                        file_name="excel_output.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.warning("⚠️ No Excel file found.")
            else:
                st.error(f"❌ Upload failed: {res.json().get('error')}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
