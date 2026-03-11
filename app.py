import streamlit as st
import whisper
import subprocess
import os
from datetime import timedelta

st.title("Hindi Audio → Hinglish Caption Video Generator")

st.write("Upload audio, video and Hinglish caption text to generate animated captions.")

audio_file = st.file_uploader("Upload Hindi Audio", type=["mp3","wav"])
video_file = st.file_uploader("Upload Background Video", type=["mp4"])
text_input = st.text_area("Paste Hinglish Caption Text (line by line)")

font_name = st.selectbox(
"Select Font",
["Arial","Impact","Montserrat","Poppins","Roboto"]
)

font_size = st.slider("Font Size",20,80,48)

border_size = st.slider("Border Size",0,10,3)

font_color = st.color_picker("Font Color","#FFFFFF")

if st.button("Generate Video"):

    os.makedirs("temp",exist_ok=True)

    audio_path="temp/audio.mp3"
    video_path="temp/video.mp4"
    ass_path="temp/captions.ass"
    output_path="temp/output.mp4"

    with open(audio_path,"wb") as f:
        f.write(audio_file.read())

    with open(video_path,"wb") as f:
        f.write(video_file.read())

    st.write("Loading Whisper model...")
    model=whisper.load_model("base")

    st.write("Detecting speech timing...")
    result=model.transcribe(audio_path)

    segments=result["segments"]

    lines=text_input.split("\n")

    def format_time(seconds):
        t=timedelta(seconds=seconds)
        total=t.total_seconds()
        h=int(total//3600)
        m=int((total%3600)//60)
        s=total%60
        return f"{h}:{m:02}:{s:05.2f}"

    ass_header=f"""
[Script Info]
ScriptType: v4.00+

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H00000000,1,{border_size},0,2,10,10,40,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""

    events=""

    for i,seg in enumerate(segments):

        if i>=len(lines):
            break

        start=format_time(seg["start"])
        end=format_time(seg["end"])

        text=lines[i]

        animation=r"{\move(-400,900,540,900,0,500)}"

        events+=f"Dialogue: 0,{start},{end},Default,,0,0,0,,{animation}{text}\n"

    with open(ass_path,"w",encoding="utf8") as f:
        f.write(ass_header+events)

    st.write("Rendering video with FFmpeg...")

    command=[
        "ffmpeg",
        "-y",
        "-i",video_path,
        "-vf",f"ass={ass_path}",
        "-c:a","copy",
        output_path
    ]

    subprocess.run(command)

    st.success("Video Generated!")

    with open(output_path,"rb") as f:
        st.download_button(
            "Download Video",
            f,
            file_name="caption_video.mp4"
        )