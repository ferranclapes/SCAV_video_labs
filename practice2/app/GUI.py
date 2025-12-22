import streamlit as st
import requests

st.title("SCAV Video Transcoder")

uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov"])

codec = st.selectbox("Select codec", ["vp8", "vp9", "h265", "av1"])

if st.button("Transcode Video"):
    if uploaded_file is not None:
        st.write("Transcoding in progress...")
        response = requests.post(
            "http://localhost:8000/process/convert_into_open_codecs/",
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
            data={"codec": codec}
        )
        if response.status_code == 200:
            st.download_button("Download Transcoded Video", response.content)
        st.success("Transcoding completed!")