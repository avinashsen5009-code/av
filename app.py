import streamlit as st
import whisper
from datetime import timedelta
import tempfile
import requests

st.title("Hindi Audio → Natural Hinglish Captions")

audio_file = st.file_uploader("Upload Hindi Audio", type=["mp3","wav","m4a"])

def format_time(seconds):
    td = timedelta(seconds=seconds)
    total = td.total_seconds()

    h = int(total // 3600)
    m = int((total % 3600) // 60)
    s = int(total % 60)
    ms = int((total - int(total)) * 1000)

    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def hindi_to_hinglish(text):

    prompt = f"""
Convert this Hindi sentence to natural Hinglish (Roman Hindi).
Keep meaning same.

Hindi:
{text}

Hinglish:
"""

    url = "https://api-inference.huggingface.co/models/google/flan-t5-large"

    response = requests.post(
        url,
        json={"inputs": prompt}
    )

    result = response.json()

    return result[0]["generated_text"]


if st.button("Generate SRT") and audio_file:

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(audio_file.read())
        audio_path = tmp.name

    st.write("Loading Whisper...")
    model = whisper.load_model("base")

    result = model.transcribe(audio_path, language="hi")

    segments = result["segments"]

    srt = ""

    for i, seg in enumerate(segments):

        start = format_time(seg["start"])
        end = format_time(seg["end"])

        hindi = seg["text"]

        hinglish = hindi_to_hinglish(hindi)

        srt += f"{i+1}\n"
        srt += f"{start} --> {end}\n"
        srt += f"{hinglish}\n\n"

    st.download_button(
        "Download SRT",
        srt,
        file_name="hinglish_captions.srt"
    )