import streamlit as st
import tempfile
import os
import io
import pandas as pd
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Google Drive API scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly'
]

st.set_page_config(page_title="Auto Fetch Excel", layout="centered")
st.title("📤 Upload → ⏳ Wait → 📊 Auto Show Excel")

# Step 1: Upload file
uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "jpg", "jpeg", "png"])

# Step 2: Authenticate & Create Drive Service
@st.cache_resource
def get_drive_service():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=creds)
    return service

drive_service = get_drive_service()

# --------------------------- Upload to Drive --------------------------- #
if uploaded_file:
    st.success(f"✅ File selected: {uploaded_file.name}")
    if st.button("Upload and Fetch Excel After 2 Minutes"):
        tmp_path = None
        try:
            ext = uploaded_file.name.split(".")[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # Upload to your target folder
            FOLDER_ID = '1erJWMj7XxDLulGLOImbRVN_e0vPHMClI'  # Replace with your upload folder ID
            file_metadata = {'name': uploaded_file.name, 'parents': [FOLDER_ID]}
            media = MediaFileUpload(tmp_path, resumable=True)
            uploaded_file_data = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            st.success("✅ File uploaded to Drive successfully!")
            st.info("⏳ Waiting 2 minutes to fetch Excel output...")

            # Wait for 2 minutes
            time.sleep(120)

            # Fetch the Excel file from another folder
            EXCEL_FOLDER_ID = "1gXpbRayNjf4UdZp1NqM47wdRF99BVi8_"  # Replace with your output folder ID
            query = f"'{EXCEL_FOLDER_ID}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
            results = drive_service.files().list(
                q=query,
                orderBy="createdTime desc",
                pageSize=1,
                fields="files(id, name)"
            ).execute()

            files = results.get("files", [])
            if not files:
                st.warning("⚠️ No Excel file found in the output folder.")
            else:
                file_id = files[0]['id']
                file_name = files[0]['name']
                st.info(f"📄 Found Excel file: {file_name}")

                # Download and display
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                while not done:
                    _, done = downloader.next_chunk()

                fh.seek(0)
                df = pd.read_excel(fh)
                st.success("✅ Excel file fetched successfully!")
                st.dataframe(df)

        except Exception as e:
            st.error(f"❌ Error: {e}")

        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except PermissionError:
                    st.warning("⚠️ Could not delete temp file.")
