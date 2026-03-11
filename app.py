import streamlit as st
import whisper
import subprocess

st.set_page_config(page_title="Hindi Audio → Hinglish Sliding Captions")

st.title("Hindi Audio → Hinglish Caption Generator")

audio = st.file_uploader("Upload Hindi Audio", type=["mp3","wav","m4a"])
caption_text = st.text_area("Paste Hinglish Caption (sentences separated by .)")

# Caption style controls
font = st.selectbox(
    "Font",
    ["Arial","Impact","Poppins","Montserrat","Anton","Bebas Neue"]
)

font_size = st.slider("Font Size",40,120,70)

text_color = st.color_picker("Text Color","#FFFFFF")
border_color = st.color_picker("Border Color","#000000")

border_size = st.slider("Border Size",0,10,4)
shadow_size = st.slider("Shadow Size",0,10,2)

# convert HEX → ASS subtitle color
def hex_to_ass(hex_color):
    hex_color = hex_color.replace("#","")
    r = hex_color[0:2]
    g = hex_color[2:4]
    b = hex_color[4:6]
    return f"&H00{b}{g}{r}"

primary = hex_to_ass(text_color)
outline = hex_to_ass(border_color)

@st.cache_resource
def load_model():
    return whisper.load_model("tiny", device="cpu")

model = load_model()


def convert_audio():

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i","audio.wav",
        "-ac","1",
        "-ar","16000",
        "clean.wav"
    ])


def time_format(t):
    return f"0:00:{t:05.2f}"


def create_ass(sentences,segments):

    header=f"""
[Script Info]
ScriptType: v4.00+
PlayResX:1080
PlayResY:1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,BorderStyle,Outline,Shadow,Alignment,MarginV
Style: Default,{font},{font_size},{primary},{outline},&H00000000,1,{border_size},{shadow_size},2,50

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""

    lines=[]

    for i,s in enumerate(sentences):

        if i>=len(segments):
            break

        start=segments[i]["start"]
        end=segments[i]["end"]

        start=time_format(start)
        end=time_format(end)

        slide="\\move(-400,960,540,960,0,500)"

        text=f"{{{slide}}}{s.upper()}"

        lines.append(
            f"Dialogue:0,{start},{end},Default,,0,0,0,,{text}"
        )

    with open("captions.ass","w") as f:
        f.write(header+"\n".join(lines))


if st.button("Generate Captions"):

    if audio and caption_text:

        with open("audio.wav","wb") as f:
            f.write(audio.read())

        with st.spinner("Preparing audio..."):
            convert_audio()

        with st.spinner("Analyzing speech timing..."):

            result=model.transcribe(
                "clean.wav",
                word_timestamps=True
            )

        segments=result["segments"]

        sentences=[s.strip() for s in caption_text.split(".") if s.strip()!=""]

        create_ass(sentences,segments)

        st.success("Captions Generated!")

        with open("captions.ass","rb") as f:

            st.download_button(
                "Download Subtitle File",
                f,
                file_name="captions.ass"
            )

    else:
        st.warning("Upload audio and caption first")