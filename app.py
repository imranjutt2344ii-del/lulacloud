import time
import streamlit as st
import os
from google import genai
from google.genai import types
from google.api_core.exceptions import ResourceExhausted

# Page configuration
st.set_page_config(page_title="AI Video Generator", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a better design
st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 AI Video Generation Platform")
st.write("Create high-quality videos using the latest Veo models.")

# Sidebar for API Configuration and Settings
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter your Google Gemini API Key", type="password")
    
    if api_key:
        # Initialize client here
        client = genai.Client(api_key=api_key)
    
    st.divider()
    aspect_ratio = st.selectbox("Aspect Ratio", options=["16:9", "9:16", "1:1", "4:3"], index=0)
    duration = st.slider("Duration (seconds)", min_value=5, max_value=15, value=8, step=1)
    resolution = st.selectbox("Resolution", options=["720p", "1080p"], index=0)

# Main content area
prompt = st.text_area("Enter your video prompt", placeholder="Describe the scene you want to generate...")
uploaded_image = st.file_uploader("Upload a reference image (optional)", type=["jpg", "png", "jpeg"])

if st.button("Generate Video 🚀", use_container_width=True, type="primary"):
    if not api_key:
        st.warning("Please enter your API Key in the sidebar to continue.")
    elif not prompt.strip() and not uploaded_image:
        st.warning("Please enter a prompt or upload a reference image.")
    else:
        with st.spinner("Processing generation request... (This takes ~1 to 2 minutes)"):
            try:
                image_input = None
                if uploaded_image:
                    image_bytes = uploaded_image.getvalue()
                    image_input = types.Image(image_bytes=image_bytes, mime_type=uploaded_image.type)
                
                config = types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    duration_seconds=duration,
                    resolution=resolution,
                    number_of_videos=1,
                )
                
                # Retry loop for handling 429 Resource Exhausted errors
                max_retries = 5
                wait_time = 10
                operation = None
                
                for attempt in range(max_retries):
                    try:
                        operation = client.models.generate_videos(
                            model="veo-3.1-generate-preview",
                            prompt=prompt if prompt.strip() else None,
                            image=image_input,
                            config=config,
                        )
                        break
                    except ResourceExhausted as e:
                        if attempt == max_retries - 1:
                            raise e
                        st.warning(f"Rate limit hit. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        wait_time *= 2
                
                # Poll until generation completes
                while operation and not operation.done:
                    time.sleep(10)
                    operation = client.operations.get(operation.name)
                
                result = operation.result
                generated_video = result.generated_videos[0]
                video_uri = generated_video.video.uri
                
                st.success("✨ Video generated successfully!")
                st.video(video_uri)
                
            except Exception as e:
                st.error(f"Generation error:{e}")
