# main.py
from fastapi import FastAPI
import uvicorn

# Inicialitzem l'aplicació FastAPI
app = FastAPI()

# Definim el primer endpoint (la ruta base o "root")
@app.get("/")
def read_root():
    """Retorna un missatge de benvinguda i l'estat de l'API."""
    return {"message": "API de Processament Multimèdia (P1) en execució!",
            "status": "OK"}