import streamlit as st
from PIL import Image
import base64
import io
from openai import OpenAI

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Image Analyzer", layout="wide")
st.title("🖼️ AI Image Analyzer")
st.write("Upload an image and get complete AI-powered analysis.")

# -------------------------
# OPENAI CLIENT (Secure)
# -------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# -------------------------
# FILE UPLOAD
# -------------------------
uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:

    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        st.subheader("📊 Image Metadata")
        st.write(f"Filename: {uploaded_file.name}")
        st.write(f"Format: {image.format}")
        st.write(f"Mode: {image.mode}")
        st.write(f"Size: {image.size}")
        st.write(f"File Size: {uploaded_file.size / 1024:.2f} KB")

    # Convert to base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    st.subheader("🤖 AI Analysis")

    with st.spinner("Analyzing image..."):

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this image in detail:
                            1. Full description
                            2. Objects detected
                            3. Text visible
                            4. Scene explanation
                            5. Insights"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800
        )

        st.write(response.choices[0].message.content)