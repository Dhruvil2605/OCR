import streamlit as st
import tempfile
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']

st.set_page_config(page_title="Upload to", layout="centered")
st.title("📤 Upload Image or PDF")

# Step 1: Upload file
uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "jpg", "jpeg", "png"])

# Step 2: Authenticate & Create Drive Service
@st.cache_resource
def get_drive_service():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=creds)
    return service

# Step 3: Upload to Drive
if uploaded_file:
    st.success(f"✅ File selected: {uploaded_file.name}")

    if st.button("Upload Document"):
        tmp_path = None  # Declare first to use in finally
        try:
            # Step 1: Save the uploaded file to a temporary location
            ext = uploaded_file.name.split(".")[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

        # Step 2: Authenticate Google Drive
            drive_service = get_drive_service()

        # Step 3: Upload file to a specific folder
            FOLDER_ID  = '1erJWMj7XxDLulGLOImbRVN_e0vPHMClI'
            file_metadata = {'name': uploaded_file.name, 'parents': [FOLDER_ID]}
            media = MediaFileUpload(tmp_path, resumable=True)
            uploaded_file_data = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

        # Step 4: Show success message
            st.success("🎉 File uploaded successfully!")
            st.info("🕒 Your task is under process.")

        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")

        finally:
        # ✅ Only try to remove the file if it exists
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except PermissionError:
                    st.warning("⚠️ Could not delete temp file. It may still be in use.")

            
