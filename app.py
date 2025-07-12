import streamlit as st
import os
from PIL import Image
import uuid

# Create folders if they don't exist
os.makedirs("ULD", exist_ok=True)
os.makedirs("PLD", exist_ok=True)

st.set_page_config(page_title="Image Upload and Processing", layout="centered")

st.title("📷 Image Upload & Processing App")

# Upload section
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Generate a unique filename to avoid overwrite
    unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    upload_path = os.path.join("ULD", unique_filename)

    # Save uploaded file
    with open(upload_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"Image uploaded successfully and saved to `ULD/`")

    # View Uploaded Image
    st.subheader("📤 Uploaded Image")
    uploaded_img = Image.open(upload_path)
    st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)

    # Process Image (example: convert to grayscale)
    st.subheader("⚙️ Processed Image (Grayscale)")
    processed_img = uploaded_img.convert("L")
    processed_path = os.path.join("PLD", f"processed_{unique_filename}")
    processed_img.save(processed_path)
    st.image(processed_img, caption="Processed Grayscale Image", use_column_width=True)
    st.success(f"Processed image saved to `PLD/`")
else:
    st.info("Please upload an image file to continue.")
