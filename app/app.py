import os
import io
import base64
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ----------------------------
# Config
# ----------------------------
st.set_page_config(page_title="AI Storybook Illustrator", layout="wide")

st.title("📖 AI Storybook Illustrator")
st.caption("Paste a story → auto-split into scenes → generate illustrations (with character consistency)")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ----------------------------
# Inputs
# ----------------------------
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
creativity = st.slider("Creativity level (guidance)", 1.0, 12.0, 7.5, 0.5)

# Consistency controls
st.subheader("Character Consistency Controls")

main_character_name = st.text_input(
    "Main character name (used in every scene)",
    value="Buddy"
)

main_character_description = st.text_input(
    "Main character description (keep it specific!)",
    value="a small white fluffy dog with pointed ears, big black eyes, a red collar, cute friendly expression"
)

allowed_characters = st.text_input(
    "Other allowed characters (optional, comma-separated)",
    value="a lost child (boy, 8 years old), forest animals"
)

strict_mode = st.checkbox(
    "Strict character mode (reduce random extra people)",
    value=True
)

# ----------------------------
# Helpers
# ----------------------------
def split_scenes(text: str):
    scenes = [s.strip() for s in text.split("\n\n") if s.strip()]
    return scenes[:max_scenes]


def build_prompt(scene: str) -> str:
    character_anchor = (
        f"Main character: {main_character_name} — {main_character_description}. "
        f"{main_character_name} must look the same in every scene."
    )

    if strict_mode:
        cast_rule = (
            f"Only include these characters: {main_character_name}, {allowed_characters}. "
            f"No random adults, no extra people, no new main characters."
        )
    else:
        cast_rule = f"Keep {main_character_name} as the same main character in every scene."

    style_rule = (
        f"Children's story illustration, {style}, soft warm lighting, "
        f"consistent character design, high quality, clean composition."
    )

    # creativity -> mild wording guidance (OpenAI uses prompt strength internally)
    creativity_rule = f"Creativity level: {creativity}/12 (keep character consistent)."

    return f"{character_anchor} {cast_rule} Scene: {scene} {style_rule} {creativity_rule}"


def generate_image(prompt: str) -> Image.Image:
    if not client:
        raise RuntimeError("OPENAI_API_KEY missing. Add it to your .env file.")

    # Generate image via OpenAI
    resp = client.images.generate(
        model=OPENAI_IMAGE_MODEL,     # default: gpt-image-1
        prompt=prompt,
        size="1024x1024",
    )

    b64 = resp.data[0].b64_json
    img_bytes = base64.b64decode(b64)
    return Image.open(io.BytesIO(img_bytes)).convert("RGB")


# ----------------------------
# Run generation
# ----------------------------
if st.button("✨ Generate Illustrations", type="primary"):
    if not story.strip():
        st.error("Please enter a story.")
        st.stop()

    scenes = split_scenes(story)
    if not scenes:
        st.error("No scenes detected. Add blank lines between paragraphs.")
        st.stop()

    if not OPENAI_API_KEY:
        st.error("OPENAI_API_KEY is missing. Put it in .env like: OPENAI_API_KEY=sk-xxxx")
        st.stop()

    st.info(
        "Tip: For best consistency, keep the main character description specific "
        "(color, size, accessories) and keep Strict mode ON."
    )

    for i, scene in enumerate(scenes, start=1):
        st.markdown(f"## Scene {i}")
        st.write(scene)

        prompt = build_prompt(scene)
        st.code(prompt)

        with st.spinner(f"Generating image for Scene {i}..."):
            try:
                image = generate_image(prompt)
                st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"Error generating image: {e}")
                st.stop()
