import os
import io
import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Storybook Illustrator", layout="wide")

st.title("📖 AI Storybook Illustrator")
st.caption("Paste a story → auto-split into scenes → generate illustrations")

story = st.text_area(
    "Your story (use blank lines to separate scenes)",
    height=250,
    placeholder="Once upon a time...\n\nThe next day...\n\nFinally..."
)

style = st.selectbox(
    "Art style",
    ["storybook illustration", "watercolor", "manga", "sketch", "digital painting", "anime"]
)

max_scenes = st.slider("Maximum scenes", 1, 6, 3)
creativity = st.slider("Creativity level", 1.0, 12.0, 7.5, 0.5)

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = os.getenv("HF_MODEL_URL")

headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

def split_scenes(text):
    scenes = [s.strip() for s in text.split("\n\n") if s.strip()]
    return scenes[:max_scenes]

def generate_image(prompt):
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert("RGB")

if st.button("✨ Generate Illustrations"):
    if not story.strip():
        st.error("Please enter a story.")
        st.stop()

    if not HF_TOKEN:
        st.error("HF_TOKEN missing in .env file.")
        st.stop()

    scenes = split_scenes(story)

    for i, scene in enumerate(scenes, start=1):
        st.markdown(f"## Scene {i}")
        st.write(scene)

        prompt = f"{scene}. Children's story illustration, {style}, high quality."
        st.code(prompt)

        with st.spinner("Generating image..."):
            try:
                image = generate_image(prompt)
                st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"Error generating image: {e}")
                break
