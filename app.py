import streamlit as st
from together import Together
import requests
from pathlib import Path
from PIL import Image
import time
import zipfile
import io

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="AI YouTube Visual Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>

/* =========================
   GLOBAL
========================= */

html, body, [class*="css"] {
    background-color: #0f1117;
    color: white;
}

/* APP */
.stApp {
    background-color: #0f1117;
    color: white;
}

/* MAIN CONTAINER */
.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}

/* =========================
   SIDEBAR
========================= */

section[data-testid="stSidebar"] {
    background-color: #151823;
    border-right: 1px solid #262730;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* =========================
   TITLE
========================= */

.title-text {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0px;
    color: white;
}

.subtitle-text {
    color: #9ca3af;
    margin-top: 0px;
    margin-bottom: 30px;
}

/* =========================
   TEXTAREA
========================= */

.stTextArea textarea {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 16px !important;
    border: 1px solid #374151 !important;
    min-height: 260px;
}

/* placeholder */
.stTextArea textarea::placeholder {
    color: #6b7280 !important;
}

/* =========================
   INPUT
========================= */

.stTextInput input {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid #374151 !important;
}

/* =========================
   SELECTBOX
========================= */

.stSelectbox > div > div {
    background-color: #111827 !important;
    color: white !important;
    border: 1px solid #374151 !important;
    border-radius: 12px !important;
}

/* dropdown text */
.stSelectbox div[data-baseweb="select"] * {
    color: white !important;
}

/* DROPDOWN MENU */
div[data-baseweb="popover"] {
    background-color: #111827 !important;
}

div[role="listbox"] {
    background-color: #111827 !important;
    border: 1px solid #374151 !important;
    color: white !important;
}

/* OPTION ITEM */
div[role="option"] {
    background-color: #111827 !important;
    color: white !important;
}

/* HOVER OPTION */

/* FIX DROPDOWN SELECTED TEXT */

div[data-baseweb="select"] span {
    color: white !important;
}

div[data-baseweb="menu"] {
    background-color: #111827 !important;
}

ul {
    background-color: #111827 !important;
}

/* selected item */
li[aria-selected="true"] {
    background-color: #1f2937 !important;
    color: white !important;
}

/* dropdown item text */
li {
    color: white !important;
}

/* hover dropdown item */
li:hover {
    background-color: #1f2937 !important;
    color: white !important;
}

div[role="option"]:hover {
    background-color: #1f2937 !important;
    color: white !important;
}

/* SIDEBAR COLLAPSE BUTTON */
button[kind="header"] {
    background-color: transparent !important;
    color: white !important;
}

/* =========================
   FILE UPLOADER
========================= */

section[data-testid="stFileUploader"] {
    background-color: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 16px !important;
    padding: 10px;
}

/* uploader text */
section[data-testid="stFileUploader"] * {
    color: white !important;
}

/* tombol Upload agar tidak putih */
section[data-testid="stFileUploader"] button,
[data-testid="stFileUploaderDropzone"] button,
button[data-testid="baseButton-secondary"] {
    background-color: #374151 !important;
    color: white !important;
    border: 1px solid #4b5563 !important;
    border-radius: 8px !important;
}

section[data-testid="stFileUploader"] small,
section[data-testid="stFileUploader"] span {
    color: #9ca3af !important;
}

/* =========================
   SLIDER
========================= */

[data-testid="stSlider"] {
    background-color: transparent !important;
}

[data-testid="stSlider"] > div > div > div {
    background-color: #374151 !important;
}

[data-testid="stSlider"] [role="slider"] {
    background-color: #7c3aed !important;
    border-color: #7c3aed !important;
}

[data-testid="stSlider"] p,
[data-testid="stSlider"] span {
    color: white !important;
}

/* =========================
   HEADER ATAS (area putih)
========================= */

header[data-testid="stHeader"] {
    background-color: #0f1117 !important;
    border-bottom: none !important;
}

[data-testid="stToolbar"] {
    background-color: #0f1117 !important;
}

.stApp > header {
    background-color: #0f1117 !important;
}

/* =========================
   METRIC
========================= */

[data-testid="metric-container"] {
    background-color: #171923;
    border: 1px solid #2a2d36;
    padding: 16px;
    border-radius: 16px;
}

/* metric label */
[data-testid="metric-container"] label {
    color: #9ca3af !important;
}

/* metric value */
[data-testid="metric-container"] div {
    color: white !important;
}

/* =========================
   BUTTON
========================= */

.stButton button {
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white !important;
    border: none;
    border-radius: 14px;
    padding: 14px 20px;
    font-weight: 700;
    width: 100%;
    height: 55px;
    font-size: 18px;
}

.stButton button:hover {
    opacity: 0.9;
}

/* =========================
   DOWNLOAD BUTTON
========================= */

.stDownloadButton button {
    background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 16px !important;
    font-weight: 700 !important;
    width: 100% !important;
}

.stDownloadButton button:hover {
    opacity: 0.9;
}

/* =========================
   CARD
========================= */

.card {
    background-color: #171923;
    padding: 20px;
    border-radius: 20px;
    border: 1px solid #2a2d36;
}

/* =========================
   GENERAL TEXT
========================= */

h1, h2, h3, h4, h5, h6,
p, span, label, div {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================

st.markdown(
    '<p class="title-text">🎬 AI YouTube Visual Generator</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle-text">Generate cinematic images for faceless YouTube videos</p>',
    unsafe_allow_html=True
)

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.markdown("## ⚙️ Settings")

    api_key = st.text_input(
        "Together AI API Key",
        type="password"
    )

    model = st.selectbox(
        "Model",
        [
            "black-forest-labs/FLUX.1-schnell",
            "black-forest-labs/FLUX.1-dev"
        ]
    )

    width = st.selectbox(
        "Width",
        [1024, 1280],
        index=0
    )

    height = st.selectbox(
        "Height",
        [576, 768],
        index=0
    )

    steps = st.slider(
        "Steps",
        min_value=1,
        max_value=10,
        value=4
    )

# =====================================
# MAIN UI
# =====================================

col1, col2 = st.columns([2, 1])

with col1:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    prompt_input = st.text_area(
        "🎨 Prompt Batch",
        placeholder="""
cinematic rainy street at night
lonely man sitting in dark room
futuristic cyberpunk city sunset
dramatic close-up emotional face
"""
    )

    uploaded_file = st.file_uploader(
        "Upload prompts.txt",
        type=["txt"]
    )

    generate_btn = st.button("🚀 Generate Images")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("### 📊 Project Info")

    if prompt_input:
        total_lines = len([
            x for x in prompt_input.split("\n")
            if x.strip()
        ])
    else:
        total_lines = 0

    st.metric("Total Prompts", total_lines)
    st.metric("Resolution", f"{width}x{height}")
    st.metric("Steps", steps)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================
# GENERATE
# =====================================

if generate_btn:

    if not api_key:
        st.error("Masukkan API Key Together AI")
        st.stop()

    prompts = []

    # dari textarea
    if prompt_input:
        prompts.extend(prompt_input.split("\n"))

    # dari upload txt
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        prompts.extend(content.split("\n"))

    # bersihkan prompt kosong
    prompts = [
        p.strip()
        for p in prompts
        if p.strip()
    ]

    if len(prompts) == 0:
        st.error("Prompt kosong")
        st.stop()

    # folder hasil
    BASE_DIR = Path(__file__).parent
    OUTPUT_FOLDER = BASE_DIR / "hasil"

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    # client together
    client = Together(api_key=api_key)

    st.markdown("---")
    st.markdown("## 🖼️ Generated Images")

    progress = st.progress(0)
    status = st.empty()

    image_cols = st.columns(3)
    saved_files = []

    # loop generate
    for i, prompt in enumerate(prompts, 1):

        status.info(f"Generating {i}/{len(prompts)}")

        try:

            response = client.images.generate(
                model=model,
                prompt=prompt,
                width=width,
                height=height,
                steps=steps
            )

            image_url = response.data[0].url

            img_data = requests.get(image_url).content

            filename = OUTPUT_FOLDER / f"{i:03d}.png"

            with open(filename, "wb") as f:
                f.write(img_data)
            
            st.success(f"Saved: {filename}")

            img = Image.open(filename)

            with image_cols[(i - 1) % 3]:

                st.image(img, caption=f"{i:03d}")

                saved_files.append(filename)

                with open(filename, "rb") as file:
                    st.download_button(
                        label=f"⬇ Download {i:03d}",
                        data=file,
                        file_name=f"image_{i:03d}.png",
                        mime="image/png",
                        key=f"download_{i}"
                    )

        except Exception as e:
            st.error(f"Error prompt {i}: {e}")

        progress.progress(i / len(prompts))

        time.sleep(1)

    status.success("🎉 Semua gambar selesai dibuat!")
   