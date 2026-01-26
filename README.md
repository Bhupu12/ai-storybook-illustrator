# AI Storybook Illustrator

## Student name:
Bhupendra Thapa

## Student number:
2320192

## Project title:
AI Storybook Illustrator – AI-Powered Story Illustration Generator

## Link to project video recording:
[ADD VIDEO LINK HERE]

---

## Project Overview
AI Storybook Illustrator is a creative AI application that transforms short stories into illustrated storybooks.  
Users provide a written story, and the system automatically splits it into scenes and generates an illustration for each scene using a diffusion-based text-to-image model.

This project explores how generative AI can support creativity by helping non-artists visualise their stories.

---

## Features
- Text input for short stories
- Automatic scene detection using paragraph splitting
- AI-generated illustrations using a diffusion model
- Multiple art styles (storybook, watercolor, manga, sketch, anime)
- Interactive web interface built with Streamlit

---

## AI Approach
The system uses a pre-trained **text-to-image diffusion model** accessed via the Hugging Face Inference API.

**Pipeline:**
1. User inputs a story
2. Story is split into scenes using blank lines
3. Each scene is converted into a structured text prompt
4. A diffusion model generates an image for each scene
5. Images are displayed alongside the original text

This approach focuses on prompt engineering and creative control rather than model training.

---

## Tools & Technologies
- Python
- Streamlit
- Hugging Face Inference API
- Stable Diffusion (pre-trained model)
- Requests
- Pillow

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Bhupu12/ai-storybook-illustrator.git
cd ai-storybook-illustrator
