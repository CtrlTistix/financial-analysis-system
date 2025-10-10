from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Dict
import io

# Importar nuestro servicio de análisis
from app.services.analysis_service import AnalysisService

app = FastAPI(title="Financial Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

analysis_service = AnalysisService()

@app.get("/")
def read_root():
    return {"message": "🚀 Financial Analysis API is running!", "status": "success"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para subir archivos Excel y analizarlos"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel")
        
        # Leer el archivo Excel
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Analizar los datos financieros
        analysis_result = analysis_service.analyze_financial_data(df)
        analysis_result["filename"] = file.filename
        analysis_result["message"] = "Análisis financiero completado exitosamente"
        
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
                "prueba_acida": {"2020": 1.2, "2021": 1.3, "2022": 1.1, "2023": 1.0},
                "capital_trabajo": {"2020": 40000, "2021": 50000, "2022": 45000, "2023": 35000}
            },
            "rentabilidad": {
                "roe": {"2020": 0.15, "2021": 0.18, "2022": 0.12, "2023": 0.10},
                "roa": {"2020": 0.08, "2021": 0.09, "2022": 0.07, "2023": 0.06},
                "margen_bruto": {"2020": 0.30, "2021": 0.32, "2022": 0.28, "2023": 0.25}
            }
        }
    }