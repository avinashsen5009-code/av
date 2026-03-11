import streamlit as st
import whisper
from datetime import timedelta
from indic_transliteration.sanscript import transliterate
from indic_transliteration import sanscript
import tempfile

st.title("Hindi Audio → Viral Hinglish Captions (SRT)")

audio_file = st.file_uploader("Upload Hindi Audio", type=["mp3","wav","m4a"])

chunk_size = st.selectbox(
    "Words per caption",
    [1,2,3]
)

model_size = st.selectbox(
    "Model",
    ["tiny","base"]
)

def format_time(seconds):
    td = timedelta(seconds=seconds)
    total = td.total_seconds()

    hours = int(total // 3600)
    minutes = int((total % 3600) // 60)
    seconds = int(total % 60)
    millis = int((total - int(total)) * 1000)

    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


if st.button("Generate Captions") and audio_file:

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(audio_file.read())
        audio_path = tmp.name

    st.write("Loading Whisper model...")
    model = whisper.load_model(model_size)

    st.write("Transcribing audio...")
    result = model.transcribe(audio_path, language="hi")

    segments = result["segments"]

    srt = ""
    index = 1

    for seg in segments:

        start = seg["start"]
        end = seg["end"]

        hindi = seg["text"].strip()

        hinglish = transliterate(
            hindi,
            sanscript.DEVANAGARI,
            sanscript.ITRANS
        )

        words = hinglish.split()

        duration = (end - start)

        chunks = [
            words[i:i+chunk_size]
            for i in range(0, len(words), chunk_size)
        ]

        step = duration / len(chunks)

        for i,chunk in enumerate(chunks):

            s = start + i*step
            e = start + (i+1)*step

            text = " ".join(chunk).upper()

            srt += f"{index}\n"
            srt += f"{format_time(s)} --> {format_time(e)}\n"
            srt += f"{text}\n\n"

            index += 1

    st.success("Captions Generated!")

    st.download_button(
        "Download SRT",
        srt,
        file_name="viral_hinglish_captions.srt",
        mime="text/plain"
    )