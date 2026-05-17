import streamlit as st
from together import Together
from deep_translator import GoogleTranslator
import requests
from pathlib import Path
from PIL import Image
import time
import zipfile
import io

# =====================================
# SESSION STATE
# =====================================
if "saved_files" not in st.session_state:
    st.session_state.saved_files = []

if "generated" not in st.session_state:
    st.session_state.generated = False

if "generated_images" not in st.session_state:
    st.session_state.generated_images = []

if "generated_audios" not in st.session_state:
    st.session_state.generated_audios = []

if "saved_audios" not in st.session_state:
    st.session_state.saved_audios = []

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
/* placeholder untuk TextInput Voice ID */
input[placeholder="Masukkan Voice ID ElevenLabs"]::placeholder {
    color: #ef4444 !important;
    font-weight: 300;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================
st.markdown('<p class="title-text">🎬 AI YouTube Visual Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Generate cinematic images for faceless YouTube videos</p>', unsafe_allow_html=True)

# =====================================
# SIDEBAR
# =====================================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.sidebar.info("You use your own Together AI API key. Image generation cost depends on your Together account.")

    api_key = st.text_input("Together AI API Key", type="password")

    model = st.selectbox("Model", ["black-forest-labs/FLUX.1-schnell", "black-forest-labs/FLUX.1-dev"])
    width = st.selectbox("Width", [1024, 1280], index=0)
    height = st.selectbox("Height", [576, 768], index=0)
    steps = st.slider("Steps", min_value=1, max_value=10, value=4)

    st.markdown("## 🎤 Audio Settings")
    eleven_api = st.text_input("ElevenLabs API Key", type="password")
    voice_id = st.text_input("Voice ID", placeholder="Masukkan Voice ID ElevenLabs")
    generate_audio_btn = st.button("🎤 Generate Audio")

# =====================================
# MAIN UI
# =====================================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    prompt_input = st.text_area("🎨 Prompt Batch", placeholder="cinematic rainy street at night\nlonely man sitting in dark room\nfuturistic cyberpunk city sunset\ndramatic close-up emotional face")
    uploaded_file = st.file_uploader("Upload prompts.txt", type=["txt"])
    generate_btn = st.button("🚀 Generate Images")
    st.markdown('</div>', unsafe_allow_html=True)

    # Tambahan khusus audio
    st.markdown('<div class="card">', unsafe_allow_html=True)
    audio_text_input = st.text_area("🎤 Audio Text Batch", placeholder="Halo semua, selamat datang di channel kami...\nIni adalah narasi untuk video YouTube...")
    uploaded_audio_file = st.file_uploader("Upload audio_texts.txt", type=["txt"])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Project Info")
    total_lines = len([x for x in prompt_input.split("\n") if x.strip()]) if prompt_input else 0
    st.metric("Total Prompts", total_lines)
    st.metric("Resolution", f"{width}x{height}")
    st.metric("Steps", steps)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================
# IMAGE GENERATOR
# =====================================
if generate_btn:
    if not api_key:
        st.error("Masukkan API Key Together AI")
        st.stop()

    prompts = []
    if prompt_input:
        prompts.extend(prompt_input.split("\n"))
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        prompts.extend(content.split("\n"))
    prompts = [p.strip() for p in prompts if p.strip()]

    if len(prompts) == 0:
        st.error("Prompt kosong")
        st.stop()

    BASE_DIR = Path(__file__).parent
    OUTPUT_FOLDER = BASE_DIR / "hasil"
    AUDIO_FOLDER = BASE_DIR / "audio"
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    AUDIO_FOLDER.mkdir(exist_ok=True)

    client = Together(api_key=api_key)

    st.markdown("---")
    st.markdown("## 🖼️ Generated Images")

    progress = st.progress(0)
    status = st.empty()
    st.session_state.saved_files = []
    st.session_state.generated_images = []

    for i, prompt in enumerate(prompts, 1):
        status.info(f"Generating {i}/{len(prompts)}")
        try:
            translated_prompt = GoogleTranslator(source='auto', target='en').translate(prompt)
            st.caption(f"EN Prompt: {translated_prompt}")
            response = client.images.generate(model=model, prompt=translated_prompt, width=width, height=height, steps=steps)
            image_url = response.data[0].url
            img_data = requests.get(image_url, timeout=30).content
            filename = OUTPUT_FOLDER / f"{int(time.time())}_{i:03d}.png"
            with open(filename, "wb") as f:
                f.write(img_data)
            st.success(f"Saved: {filename}")
            img = Image.open(filename)
            st.session_state.generated_images.append({"image": img, "filename": filename, "index": i})
            st.session_state.saved_files.append(filename)
        except Exception as e:
            st.error(f"Error prompt {i}: {e}")
        progress.progress(i / len(prompts))
        time.sleep(1)

    status.success("🎉 Semua gambar selesai dibuat!")
    st.session_state.generated = True
    
    # =====================================
    # ZIP ALL DOWNLOAD
    # =====================================
    if st.session_state.generated and len(st.session_state.saved_files) > 0:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file_path in st.session_state.saved_files:
                zipf.write(file_path, arcname=Path(file_path).name)
        zip_buffer.seek(0)

        st.download_button(
            label="📦 Download All Images (ZIP)",
            data=zip_buffer,
            file_name="generated_images.zip",
            mime="application/zip",
            key="download_zip"
        )

    # =====================================
    # SHOW SAVED IMAGES AFTER RERUN
    # =====================================
    if st.session_state.generated_images:
        st.markdown("---")
        st.markdown("## 🖼️ Generated Images")

        cols = st.columns(3)
        for idx, item in enumerate(st.session_state.generated_images):
            with cols[idx % 3]:
                st.image(item["image"], caption=f'{item["index"]:03d}')
                with open(item["filename"], "rb") as file:
                    st.download_button(
                        label=f'⬇ Download {item["index"]:03d}',
                        data=file,
                        file_name=f'image_{item["index"]:03d}.png',
                        mime="image/png",
                        key=f"persistent_download_{idx}"
                    )
# =====================================
# AUDIO GENERATOR
# =====================================
if generate_audio_btn:
    if not eleven_api:
        st.error("Masukkan ElevenLabs API Key")
        st.stop()

    audio_texts = []
    if audio_text_input:
        audio_texts.extend(audio_text_input.split("\n"))
    if uploaded_audio_file:
        content = uploaded_audio_file.read().decode("utf-8")
        audio_texts.extend(content.split("\n"))
    audio_texts = [t.strip() for t in audio_texts if t.strip()]

    if len(audio_texts) == 0:
        st.error("Text audio kosong")
        st.stop()

    st.session_state.generated_audios = []
    st.session_state.saved_audios = []

    st.markdown("---")
    st.markdown("## 🔊 Generated Audio")

    progress_audio = st.progress(0)
    status_audio = st.empty()

    headers = {"xi-api-key": eleven_api, "Content-Type": "application/json"}

    for i, text in enumerate(audio_texts, 1):
        status_audio.info(f"Generating audio {i}/{len(audio_texts)}")
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            payload = {"text": text, "model_id": "eleven_multilingual_v2"}
            response = requests.post(url, json=payload, headers=headers)

            audio_filename = AUDIO_FOLDER / f"audio_{i:03d}.mp3"
            with open(audio_filename, "wb") as f:
                f.write(response.content)

            st.session_state.generated_audios.append({
                "filename": audio_filename,
                "index": i,
                "text": text
            })
            st.session_state.saved_audios.append(audio_filename)

            st.success(f"Saved Audio: {audio_filename}")
        except Exception as e:
            st.error(f"Error audio {i}: {e}")

        progress_audio.progress(i / len(audio_texts))
        time.sleep(1)

    status_audio.success("🎉 Semua audio selesai dibuat!")


# =====================================
# SHOW AUDIOS
# =====================================
if st.session_state.generated_audios:
    st.markdown("---")
    st.markdown("## 🔊 Generated Audio")

    for idx, item in enumerate(st.session_state.generated_audios):
        st.markdown(f"### Audio {item['index']:03d}")
        st.caption(item["text"])

        with open(item["filename"], "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")

            st.download_button(
                label=f"⬇ Download Audio {item['index']:03d}",
                data=audio_bytes,
                file_name=f"audio_{item['index']:03d}.mp3",
                mime="audio/mp3",
                key=f"audio_download_{idx}"
            )

# =====================================
# DOWNLOAD ALL AUDIOS ZIP
# =====================================
if len(st.session_state.saved_audios) > 0:
    zip_audio_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_audio_buffer, "w") as zipf:
        for file_path in st.session_state.saved_audios:
            zipf.write(file_path, arcname=Path(file_path).name)
    zip_audio_buffer.seek(0)

    st.download_button(
        label="📦 Download All Audios (ZIP)",
        data=zip_audio_buffer,
        file_name="generated_audios.zip",
        mime="application/zip",
        key="download_audio_zip"
    )

# =====================================
# RESET BUTTON
# =====================================
if st.session_state.generated or st.session_state.generated_audios:
    st.markdown("---")
    if st.button("🔄 Reset Project"):
        st.session_state.saved_files = []
        st.session_state.generated_images = []
        st.session_state.generated = False
        st.session_state.saved_audios = []
        st.session_state.generated_audios = []
        st.success("Project berhasil direset! Silakan mulai lagi.")
