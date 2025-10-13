from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Dict
import io
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Importar nuestro servicio de análisis
from app.services.analysis_service import AnalysisService

app = FastAPI(title="Financial Analysis API")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de OpenAI con manejo robusto de errores
OPENAI_AVAILABLE = False
client = None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 🔐 Carga segura desde .env

try:
    # Intentar importar OpenAI de diferentes maneras
    try:
        from openai import OpenAI
        print("✅ OpenAI importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando OpenAI: {e}")
        # Intentar instalación alternativa
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai==1.3.4"])
        from openai import OpenAI
        print("✅ OpenAI reinstalado e importado correctamente")
    
    # Configurar cliente
    if OPENAI_API_KEY and OPENAI_API_KEY != "":
        client = OpenAI(api_key=OPENAI_API_KEY)
        OPENAI_AVAILABLE = True
        print("✅ OpenAI configurado correctamente")
    else:
        print("⚠️ API Key de OpenAI no configurada. Usando respuestas fallback.")
        
except Exception as e:
    print(f"❌ Error configurando OpenAI: {e}")
    OPENAI_AVAILABLE = False

analysis_service = AnalysisService()

@app.get("/")
def read_root():
    return {
        "message": "🚀 Financial Analysis API is running!", 
        "status": "success",
        "openai_status": "available" if OPENAI_AVAILABLE else "fallback_mode"
    }

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

@app.post("/chat")
async def chat_with_ai(message: dict):
    """Endpoint para chat con IA"""
    try:
        user_message = message.get("message", "").lower()
        financial_data = message.get("financial_data", {})
        
        if not user_message:
            raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

        # Si OpenAI está disponible, usarlo
        if OPENAI_AVAILABLE and client:
            # Construir contexto con datos financieros
            context = ""
            if financial_data and financial_data.get('indicators'):
                indicators = financial_data['indicators']
                available_years = financial_data.get('available_years', [])
                
                context = f"""
                Datos financieros actuales:
                
                Indicadores de Liquidez:
                - Razón Corriente: {indicators.get('liquidez', {}).get('razon_corriente', {})}
                - Prueba Ácida: {indicators.get('liquidez', {}).get('prueba_acida', {})}
                - Capital de Trabajo: {indicators.get('liquidez', {}).get('capital_trabajo', {})}
                
                Indicadores de Rentabilidad:
                - ROE: {indicators.get('rentabilidad', {}).get('roe', {})}
                - ROA: {indicators.get('rentabilidad', {}).get('roa', {})}
                - Margen Bruto: {indicators.get('rentabilidad', {}).get('margen_bruto', {})}
                
                Años disponibles: {available_years}
                """

            # Llamar a OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado en análisis financiero."},
                    {"role": "user", "content": f"{context}\n\nPregunta: {user_message}"}
                ],
                max_tokens=500,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content.strip()
            
            return {
                "response": ai_response,
                "status": "success",
                "source": "openai"
            }
        
        else:
            # Respuestas predefinidas como fallback
            responses = {
                "liquidez": "Basándome en tus indicadores de liquidez, la empresa muestra capacidad para cumplir con obligaciones a corto plazo. La razón corriente ideal está entre 1.5 y 2.0.",
                "rentabilidad": "Los indicadores de rentabilidad muestran el desempeño de la empresa. ROE mide rentabilidad sobre capital, ROA sobre activos totales.",
                "roe": "ROE (Return on Equity) mide la rentabilidad sobre el capital contable. Indica qué tan eficientemente se usa el capital de los accionistas.",
                "roa": "ROA (Return on Assets) mide la eficiencia en el uso de los activos totales para generar utilidades.",
                "razón corriente": "La Razón Corriente (Activo Corriente/Pasivo Corriente) mide la capacidad de pagar deudas a corto plazo.",
                "prueba ácida": "La Prueba Ácida es similar a la razón corriente pero excluye inventarios, dando una visión más conservadora.",
                "recomendación": "Recomendaciones generales: 1) Optimizar capital de trabajo, 2) Mejorar rotación de inventarios, 3) Revisar estructura de costos.",
                "hola": "¡Hola! Soy tu asistente de análisis financiero. Puedo explicarte indicadores y analizar tus datos.",
                "qué es": "Puedo explicarte conceptos financieros como ROE, ROA, liquidez, rentabilidad, y analizar tus indicadores."
            }
            
            response = "Puedo ayudarte a entender conceptos financieros. ¿Tienes alguna pregunta específica sobre tus indicadores?"
            
            for key, resp in responses.items():
                if key in user_message:
                    response = resp
                    break

            return {
                "response": response,
                "status": "success", 
                "source": "fallback"
            }

    except Exception as e:
        print(f"Error en chat: {str(e)}")
        return {
            "response": "Puedo explicarte conceptos financieros básicos. ¿Tienes preguntas sobre ROE, ROA, liquidez o rentabilidad?",
            "status": "success",
            "source": "error_fallback"
        }