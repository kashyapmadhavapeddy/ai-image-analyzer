import streamlit as st
from PIL import Image
import base64
import io
from openai import OpenAI
from datetime import datetime

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Image Analyzer", layout="wide")
st.title("🖼️ AI Image Analyzer with History & Download")
st.write("Upload multiple images. Scroll down to see previous analyses and download reports.")

# -------------------------
# SESSION STATE INIT
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------
# OPENAI CLIENT
# -------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------
# FILE UPLOADER
# -------------------------
uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    # Convert to RGB safely
    if image.mode != "RGB":
        image = image.convert("RGB")

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

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

        result = response.choices[0].message.content

        # Save to history
        st.session_state.history.append({
            "image": image,
            "filename": uploaded_file.name,
            "analysis": result,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

# -------------------------
# DISPLAY HISTORY
# -------------------------
for idx, item in enumerate(st.session_state.history):
    st.divider()
    st.subheader(f"📁 Image {idx + 1}: {item['filename']}")
    st.write(f"🕒 Analyzed at: {item['timestamp']}")
    st.image(item["image"], use_container_width=True)
    st.write(item["analysis"])

    # -------------------------
    # CREATE DOWNLOAD REPORT
    # -------------------------
    report_text = f"""
AI IMAGE ANALYSIS REPORT
----------------------------
Filename: {item['filename']}
Analyzed at: {item['timestamp']}

----------------------------------------
ANALYSIS RESULT:
----------------------------------------

{item['analysis']}
"""

    st.download_button(
        label="📥 Download Report",
        data=report_text,
        file_name=f"analysis_report_{idx+1}.txt",
        mime="text/plain",
        key=f"download_{idx}"
    )

# -------------------------
# CLEAR HISTORY BUTTON
# -------------------------
if st.session_state.history:
    st.divider()
    if st.button("🗑 Clear History"):
        st.session_state.history = []
        st.rerun()