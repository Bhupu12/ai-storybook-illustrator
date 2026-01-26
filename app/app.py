import os
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

st.set_page_config(page_title="AI Storybook Illustrator", layout="wide")

st.title("📖 AI Storybook Illustrator")
st.caption("Paste a story → auto-split into scenes → generate illustrations (with character consistency)")

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

# ✅ Consistency controls
st.subheader("Character Consistency Controls")

main_character_name = st.text_input(
    "Main character name (used in every scene)",
    value="Buddy"
)

main_character_description = st.text_input(
    "Main character description (keep it specific!)",
    value="a small white fluffy dog with pointed ears, big black eyes, a red collar, cute friendly expression"
)

# Optional: additional characters you want to allow
allowed_characters = st.text_input(
    "Other allowed characters (optional, comma-separated)",
    value="a lost child (boy, 8 years old), forest animals"
)

# If you want repeatable output: same seed = same image (for the same prompt)
seed = st.number_input(
    "Seed (same seed = more consistent results)",
    min_value=0,
    max_value=2_147_483_647,
    value=42,
    step=1
)

# If you only want the main character unless the scene clearly requires others
strict_mode = st.checkbox(
    "Strict character mode (reduce random extra people)",
    value=True
)

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = os.getenv("HF_MODEL_ID", "stabilityai/stable-diffusion-xl-base-1.0")

# ----------------------------
# Helpers
# ----------------------------
def split_scenes(text: str):
    scenes = [s.strip() for s in text.split("\n\n") if s.strip()]
    return scenes[:max_scenes]

def build_prompt(scene: str) -> str:
    """
    Prompt template designed to keep the SAME character across scenes.
    """
    # Make the model "anchor" the character identity
    character_anchor = (
        f"Main character: {main_character_name} — {main_character_description}. "
        f"{main_character_name} must look the same in every scene."
    )

    # Restrict characters
    if strict_mode:
        cast_rule = (
            f"Only include these characters: {main_character_name}, {allowed_characters}. "
            f"No random adults, no extra people, no new main characters."
        )
    else:
        cast_rule = (
            f"Keep {main_character_name} as the same main character in every scene."
        )

    # Style + quality rules
    style_rule = (
        f"Children's story illustration, {style}, soft warm lighting, "
        f"consistent character design, high quality, clean composition."
    )

    return f"{character_anchor} {cast_rule} Scene: {scene} {style_rule}"

def negative_prompt() -> str:
    """
    Negative prompt helps reduce unwanted artifacts and random characters.
    """
    if strict_mode:
        return (
            "extra people, adult man, adult woman, crowd, multiple humans, "
            "new character, text, watermark, logo, low quality, blurry, deformed, bad anatomy"
        )
    return "text, watermark, logo, low quality, blurry, deformed"

def generate_image(prompt: str) -> Image.Image:
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN missing in .env file.")

    client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

    # NOTE: Some providers/models support negative_prompt and seed; if one fails,
    # Streamlit will show the error and we can adjust.
    img = client.text_to_image(
        prompt,
        guidance_scale=float(creativity),
        seed=int(seed),
        negative_prompt=negative_prompt()
    )
    return img.convert("RGB")

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
