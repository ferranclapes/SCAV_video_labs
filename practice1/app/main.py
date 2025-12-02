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
@app.post("/process/resize_image/")
async def resize_image_endpoint(
    width: int = Form(-1),
    height: int = Form(-1),
    file: UploadFile = File(...)
):
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

@app.post("/process/bw_image/")
async def bw_image_endpoint(
    file: UploadFile = File(...)
):
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
