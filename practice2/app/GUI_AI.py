import streamlit as st
import requests

# Títol de la teva App
st.title("🎬 SCAV Video Transcoding App")
st.write("A GUI for the P2 Monster API")

# URL de la teva API (com que la tens a Docker al port 8000)
API_URL = "http://localhost:8000"

# 1. Widget per pujar l'arxiu
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    # Mostrem informació del fitxer
    st.video(uploaded_file)
    st.write(f"Filename: {uploaded_file.name}")

    # Creem columnes per als botons (perquè quedi maco)
    col1, col2 = st.columns(2)

    # --- BOTÓ 1: EXERCICI 1 (Transcoding) ---
    with col1:
        st.header("Transcoding")
        codec = st.selectbox("Choose codec", ["vp8", "vp9", "h265", "av1"])
        
        if st.button("Convert Video"):
            with st.spinner(f"Converting to {codec}... (This might take a while)"):
                try:
                    # Preparem l'arxiu per enviar
                    # .seek(0) és important per tornar a llegir l'arxiu des del principi
                    uploaded_file.seek(0) 
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    data = {"codec": codec}
                    
                    # Cridem l'endpoint que vas fer a l'ex 1
                    response = requests.post(f"{API_URL}/process/convert_into_open_codecs/", files=files, data=data)
                    
                    if response.status_code == 200:
                        st.success("Conversion successful!")
                        # Botó per descarregar el resultat
                        st.download_button(
                            label="Download Converted Video",
                            data=response.content,
                            file_name=f"converted_{codec}_{uploaded_file.name}",
                            mime="video/mp4"
                        )
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                        
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    # --- BOTÓ 2: EXERCICI 2 (Encoding Ladder) ---
    with col2:
        st.header("Encoding Ladder")
        st.write("Generate multiple resolutions (480p, 720p...) packaged in a ZIP.")
        
        if st.button("Generate Ladder"):
            with st.spinner("Crunching pixels... Please wait."):
                try:
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    
                    # Cridem l'endpoint de l'ex 2
                    response = requests.post(f"{API_URL}/process/encoding_ladder/", files=files)
                    
                    if response.status_code == 200:
                        st.success("Ladder created!")
                        # Botó per descarregar el ZIP
                        st.download_button(
                            label="Download ZIP Pack",
                            data=response.content,
                            file_name="encoding_ladder.zip",
                            mime="application/zip"
                        )
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                        
                except Exception as e:
                    st.error(f"Connection Error: {e}")