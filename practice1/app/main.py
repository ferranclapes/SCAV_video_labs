# main.py
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
from pathlib import Path
import uvicorn

from . import s1_functions as s1
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
    input_path = TEMP_DIR / file.filename
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
    input_path = TEMP_DIR / file.filename

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
    input_path = TEMP_DIR / file.filename
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
