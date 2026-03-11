import streamlit as st
import whisper

st.set_page_config(page_title="Sliding Caption Generator")

st.title("Hindi Audio → Hinglish Sliding Captions")

audio = st.file_uploader("Upload Hindi Audio", type=["mp3","wav","m4a"])
caption_text = st.text_area("Paste Hinglish Caption")

font = st.selectbox(
    "Font",
    ["Arial","Impact","Poppins","Montserrat","Anton","Bebas Neue"]
)

font_size = st.slider("Font Size",40,120,70)

@st.cache_resource
def load_model():
    return whisper.load_model("small")

model = load_model()


def time_format(t):
    return f"0:00:{t:05.2f}"


def create_ass(sentences,segments):

    header=f"""
[Script Info]
ScriptType: v4.00+
PlayResX:1080
PlayResY:1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BorderStyle,Outline,Alignment,MarginV
Style: Default,{font},{font_size},&H00FFFFFF,&H00000000,1,4,2,50

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

        slide="\\move(-300,960,540,960,0,500)"

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

        with st.spinner("Analyzing speech timing..."):

            result=model.transcribe(
                "audio.wav",
                word_timestamps=True
            )

        segments=result["segments"]

        sentences=[s.strip() for s in caption_text.split(".") if s.strip()!=""]

        create_ass(sentences,segments)

        st.success("Captions Generated")

        with open("captions.ass","rb") as f:

            st.download_button(
                "Download ASS Subtitle",
                f,
                file_name="captions.ass"
            )

    else:
        st.warning("Upload audio and caption first")