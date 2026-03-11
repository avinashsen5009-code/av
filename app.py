import streamlit as st
import whisper
from datetime import timedelta
import tempfile

st.title("Hindi Audio → Accurate SRT Generator")

st.write("Upload Hindi audio and generate subtitle file with timestamps.")

audio_file = st.file_uploader("Upload Audio", type=["mp3","wav","m4a"])

model_size = st.selectbox(
    "Accuracy vs Speed",
    ["tiny","base","small"]
)

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total = td.total_seconds()

    hours = int(total // 3600)
    minutes = int((total % 3600) // 60)
    seconds = int(total % 60)
    milliseconds = int((total - int(total)) * 1000)

    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

if st.button("Generate SRT") and audio_file:

    st.info("Loading model...")

    model = whisper.load_model(model_size)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(audio_file.read())
        audio_path = tmp.name

    st.info("Transcribing audio...")

    result = model.transcribe(audio_path, language="hi")

    segments = result["segments"]

    srt_output = ""

    for i, seg in enumerate(segments):

        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()

        srt_output += f"{i+1}\n"
        srt_output += f"{start} --> {end}\n"
        srt_output += f"{text}\n\n"

    st.success("SRT file generated!")

    st.download_button(
        "Download SRT",
        srt_output,
        file_name="captions.srt",
        mime="text/plain"
    )