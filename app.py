import streamlit as st
from PIL import Image
import base64
import io
from openai import OpenAI
from datetime import datetime

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Image Analyzer", page_icon="🖼️", layout="centered")

# -------------------------
# CUSTOM CSS
# -------------------------
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .sub-title {
            text-align: center;
            color: #A0A0A0;
            margin-bottom: 30px;
        }
        .card {
            padding: 20px;
            border-radius: 12px;
            background-color: #111827;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .timestamp {
            font-size: 13px;
            color: #9CA3AF;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.markdown("<div class='main-title'>🖼️ AI Image Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Upload images • Get AI insights • Download reports</div>", unsafe_allow_html=True)

# -------------------------
# SESSION STATE
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------
# OPENAI CLIENT
# -------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------
# UPLOAD SECTION
# -------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# IMAGE PROCESSING
# -------------------------
if uploaded_file is not None:

    image = Image.open(uploaded_file)

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

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(f"### 📁 {item['filename']}")
    st.markdown(f"<div class='timestamp'>Analyzed at: {item['timestamp']}</div>", unsafe_allow_html=True)

    st.image(item["image"], use_container_width=True)
    st.markdown(item["analysis"])

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

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# CLEAR HISTORY
# -------------------------
if st.session_state.history:
    if st.button("🗑 Clear History"):
        st.session_state.history = []
        st.rerun()