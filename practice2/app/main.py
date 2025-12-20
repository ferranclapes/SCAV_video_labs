# main.py
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
from pathlib import Path
import uvicorn
import ffmpeg

from . import s1_functions as s1
from . import s2_functions as s2
from . import p2_functions as p2
# Inicialitzem l'aplicació FastAPI
app = FastAPI(title="API de la pràctica 1")
TEMP_DIR = Path("temp_uploads")

# Definim el primer endpoint (la ruta base o "root")
@app.get("/")
def read_root():
    """Retorna un missatge de benvinguda i l'estat de l'API."""
    return {"message": "API de Processament Multimèdia (P1) en execució!",
            "status": "OK",
            "IMPORTANT": "add '/docs' at the end of the URL to see the API endpoints"}



# --- ENDPOINTS FOR S1 FUNCTIONS ---
@app.post("/translate/rgb_to_yuv/")
async def rgb_to_yuv_endpoint(
    r: int = Form(0),
    g: int = Form(0),
    b: int = Form(0)
):
    try:
        translator = s1.traslator()
        y, u, v = translator.rgb_to_yuv(r, g, b)
        return {"y": y, "u": u, "v": v}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during RGB to YUV conversion: {str(e)}")

@app.post("/translate/yuv_to_rgb/")
async def yuv_to_rgb_endpoint(
    y: float = Form(0.0),
    u: float = Form(0.0),
    v: float = Form(0.0)
):
    try:
        translator = s1.traslator()
        r, g, b = translator.yuv_to_rgb(y, u, v)
        return {"r": r, "g": g, "b": b}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during YUV to RGB conversion: {str(e)}")

@app.post("/process/resize_image/")
async def resize_image_endpoint(
    width: int = Form(-1),
    height: int = Form(-1),
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)


    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")
    output_filename = f"resized_{width}x{height}_{file.filename}"
    output_path = TEMP_DIR / output_filename

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process image with s1_functions:
        s1.resize_image(str(input_path), str(output_path), width, height)

        #3 Return processed file:
        return FileResponse(path=output_path, filename=output_filename, media_type='image/jpeg')

    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during image resizing: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)
        # if output_path.exists():
        #     os.remove(output_path)

@app.post("/process/serpentine/")
async def serpentine_endpoint(
    file: UploadFile = File(...)
):

    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process image with s1_functions:
        output_pixels = s1.serpentine(str(input_path))

        #3 Return processed data:
        return {"serpentine_pixels": output_pixels.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during serpentine reading: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)

@app.post("/process/bw_image/")
async def bw_image_endpoint(
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)

    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")

    output_filename = f"bw_{file.filename}"
    output_path = TEMP_DIR / output_filename

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process image with s1_functions:
        s1.to_black_white(str(input_path), str(output_path))

        #3 Return processed file:
        return FileResponse(path=output_path, filename=output_filename, media_type='image/jpeg')

    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during image conversion to B/W: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)
        #if output_path.exists():
            #os.remove(output_path)

@app.post("/process/run_length_encoding/")
async def run_length_encoding_endpoint(
    file: UploadFile = File(...)
):
    try:
        #1 Read uploaded file content as bytes
        file_content = await file.read()
        byte_stream = list(file_content)

        #2 Process byte stream with s1_functions:
        encoded_stream = s1.run_length_encoding(byte_stream)

        #3 Return encoded data:
        return {"run_length_encoded": encoded_stream}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during Run Length Encoding: {str(e)}")


# --- ENDPOINTS FOR S2 FUNCTIONS ---

@app.post("/process/change_video_resolution/")
async def change_video_resolution_endpoint(
    width: int = Form(-1),
    height: int = Form(-1),
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)


    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")
    output_filename = f"resized_{width}x{height}_{file.filename}"
    output_path = TEMP_DIR / output_filename

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process video with s2_functions:
        s2.change_video_resolution(str(input_path), str(output_path), width, height)

        #3 Return processed file:
        return FileResponse(path=output_path, filename=output_filename, media_type='video/mp4')

    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during video resizing: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)
        # if output_path.exists():
        #     os.remove(output_path)

@app.post("/process/change_chroma_subsampling/")
async def change_chroma_subsampling_endpoint(
    subsampling: str = Form("420p"),
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)


    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")
    output_filename = f"subsampled_{subsampling}_{file.filename}"
    output_path = TEMP_DIR / output_filename

    if subsampling not in ["420p", "422p", "444p", "420p10le", "422p10le", "444p10le"]:
        raise HTTPException(status_code=400, detail="Invalid subsampling format. Supported formats: 420p, 422p, 444p, 420p10le, 422p10le, 444p10le")
    
    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process video with s2_functions:
        s2.change_chroma_subsampling(str(input_path), str(output_path), subsampling)

        #3 Return processed file:
        return FileResponse(path=output_path, filename=output_filename, media_type='video/mp4')

    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during chroma subsampling change: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)
        # if output_path.exists():
        #     os.remove(output_path)

@app.post("/info/video_info/")
async def video_info_endpoint(
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)

    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Get video info with s2_functions:
        video_info = s2.get_video_info(str(input_path))

        #3 Return video info:
        return {"video_info": video_info}

    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during video info retrieval: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)

@app.post("/process/process_bbb/")
async def process_bbb_endpoint(
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)


    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")
    output_filename = f"bbb_20s.mp4"
    output_path = TEMP_DIR / output_filename

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process video with s2_functions:
        s2.process_bbb(str(input_path), str(output_path))

        #3 Return processed file:
        return FileResponse(path=output_path, filename=output_filename, media_type='video/mp4')

    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during BBB video processing: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)
        # if output_path.exists():
        #     os.remove(output_path)


@app.post("/info/count_tracks/")
async def count_tracks_endpoint(
    file: UploadFile = File(...)
):
    
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)

    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")


    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process video with s2_functions:
        track_info = s2.count_tracks(str(input_path))
        
        #3 Return the value processed:
        return track_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during analyzing video container: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)
        # if output_path.exists():
        #     os.remove(output_path)


@app.post("/process/show_motion_vectors/")
async def show_motion_vectors_endpoint(
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)


    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")
    output_filename = f"bbb_motion_vectors.mp4"
    output_path = TEMP_DIR / output_filename

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process video with s2_functions:
        s2.visualize_motion_vectors(str(input_path), str(output_path))

        #3 Return processed file:
        return FileResponse(path=output_path, filename=output_filename, media_type='video/mp4')

    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during motion vectors video processing: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)
        # if output_path.exists():
        #     os.remove(output_path)



@app.post("/process/show_yuv_histogram/")
async def show_yuv_histogram_endpoint(
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)


    TEMP_DIR.mkdir(exist_ok = True)
    #input_path = TEMP_DIR / file.filename
    input_path = TEMP_DIR / (file.filename or "uploaded_file")
    output_filename = f"yuv_histogram.mp4"
    output_path = TEMP_DIR / output_filename

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process video with s2_functions:
        s2.show_yuv_histogram(str(input_path), str(output_path))

        #3 Return processed file:
        return FileResponse(path=output_path, filename=output_filename, media_type='video/mp4')

    
    except ffmpeg.Error as e:
        # AQUÍ ESTÀ LA MÀGIA: Retornem el missatge d'error real de FFmpeg
        # Així sabrem si és un problema de format, de filtre, o de què.
        error_message = e.stderr.decode('utf8')
        print(f"FFMPEG ERROR: {error_message}") # També ho imprimim al log
        raise HTTPException(status_code=500, detail=f"FFmpeg failed: {error_message}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during motion vectors video processing: {str(e)}")
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)
        # if output_path.exists():
        #     os.remove(output_path)



@app.post("/process/convert_into_open_codecs/")
async def convert_into_open_codecs_endpoint(
    codec: str = Form("vp8", description="Codec to convert into: vp8, vp9, h265, av1"),
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)


    TEMP_DIR.mkdir(exist_ok=True)
    input_path = TEMP_DIR / (file.filename or "uploaded_file")
    output_filename = f"converted_{codec}_{file.filename}"
    output_path = TEMP_DIR / output_filename

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process video with p2_functions:
        p2.convert_into_open_codecs(str(input_path), str(output_path), codec)

        #3 Return processed file:
        return FileResponse(path=output_path, filename=output_filename, media_type='video/mp4')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during video conversion to {codec}: {str(e)}")  
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)


@app.post("/process/encoding_ladder/")
async def encoding_ladder_endpoint(
    file: UploadFile = File(...)
):
    # Clean the temp directory
    if( TEMP_DIR.exists()):
        for temp_file in os.listdir(TEMP_DIR):
            temp_file_path = TEMP_DIR / temp_file
            if temp_file_path.is_file():
                os.remove(temp_file_path)


    TEMP_DIR.mkdir(exist_ok=True)
    input_path = TEMP_DIR / (file.filename or "uploaded_file")
    output_folder = f"{file.filename}_encoding_ladder"
    output_path = TEMP_DIR / output_folder
    output_path.mkdir(exist_ok=True)

    try:
        #1 Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        #2 Process video with p2_functions:
        zip_file = p2.encoding_ladder(str(input_path), str(output_path))

        #3 Return processed file:
        return FileResponse(path=zip_file, filename="encoding_ladder.zip", media_type='application/zip')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during encoding ladder processing: {str(e)}")  
    finally:
        # Clean up temporary files
        if input_path.exists():
            os.remove(input_path)