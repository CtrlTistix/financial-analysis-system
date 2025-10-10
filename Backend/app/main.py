from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
from typing import Dict

app = FastAPI(title="Financial Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "🚀 Financial Analysis API is running!", "status": "success"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para subir archivos Excel"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel")
        
        # Leer el archivo Excel
        df = pd.read_excel(file.file)
        
        # Simular análisis básico (mañana lo haremos real)
        analysis_result = {
            "filename": file.filename,
            "columns": df.columns.tolist(),
            "sample_data": df.head().to_dict(),
            "message": "Archivo procesado exitosamente - Análisis listo para implementar"
        }
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@app.get("/test-data")
def get_test_data():
    """Endpoint de prueba con datos mock para el frontend"""
    return {
        "available_years": [2020, 2021, 2022, 2023],
        "indicators": {
            "liquidez": {
                "razon_corriente": {"2020": 1.8, "2021": 1.9, "2022": 1.7, "2023": 1.6},
                "prueba_acida": {"2020": 1.2, "2021": 1.3, "2022": 1.1, "2023": 1.0}
            },
            "rentabilidad": {
                "roe": {"2020": 0.15, "2021": 0.18, "2022": 0.12, "2023": 0.10},
                "roa": {"2020": 0.08, "2021": 0.09, "2022": 0.07, "2023": 0.06}
            }
        }
    }