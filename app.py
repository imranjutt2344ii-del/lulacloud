```python
import time
import streamlit as st
from google import genai
from google.genai import types
from google.api_core.exceptions import ResourceExhausted

# (Insert your API key setup and other logic here)

if st.button("Generate Video 🚀", use_container_width=True, type="primary"):
    if not prompt.strip() and not uploaded_image:
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
                    negative_prompt=negative_prompt,
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
                st.error(f"Generation error: {e}")
```
