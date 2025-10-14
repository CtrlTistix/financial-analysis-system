from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
from typing import Dict
import io
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from app.services.analysis_service import AnalysisService
from app.services.export_service import ExportService

app = FastAPI(title="Financial Analysis API")

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

OPENAI_AVAILABLE = False
client = None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
    from openai import OpenAI
    print("✅ OpenAI importado correctamente")
    
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
export_service = ExportService()

# Variable global para almacenar el último análisis
last_analysis = None

@app.get("/")
def read_root():
    return {
        "message": "🚀 Financial Analysis API is running!", 
        "status": "success",
        "openai_status": "available" if OPENAI_AVAILABLE else "fallback_mode",
        "version": "2.0",
        "features": [
            "Indicadores de Liquidez",
            "Indicadores de Rentabilidad",
            "Indicadores de Endeudamiento",
            "Indicadores de Rotación",
            "Análisis de Quiebra (Z-Score)",
            "Análisis Horizontal",
            "Análisis Vertical",
            "Exportación a Excel",
            "ChatBot con IA"
        ]
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para subir archivos Excel y analizarlos"""
    global last_analysis
    
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel")
        
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        print(f"\n{'='*60}")
        print(f"📄 Archivo recibido: {file.filename}")
        print(f"📊 Dimensiones del DataFrame: {df.shape}")
        print(f"📋 Primeras columnas: {df.columns.tolist()[:5]}")
        print(f"{'='*60}\n")
        
        analysis_result = analysis_service.analyze_financial_data(df)
        
        # Verificar que el análisis fue exitoso
        if not analysis_result or not analysis_result.get('available_years'):
            raise HTTPException(
                status_code=400, 
                detail="No se pudieron extraer datos del archivo. Verifica que el formato sea correcto."
            )
        
        analysis_result["filename"] = file.filename
        analysis_result["upload_date"] = datetime.now().isoformat()
        analysis_result["message"] = "Análisis financiero completado exitosamente"
        
        # DEBUG: Imprimir estructura de respuesta
        print(f"\n{'='*60}")
        print("📤 ESTRUCTURA DE RESPUESTA:")
        print(f"Years disponibles: {analysis_result.get('available_years', [])}")
        
        if 'indicators' in analysis_result:
            print("\n📊 INDICADORES POR CATEGORÍA:")
            for indicator_type, indicators in analysis_result['indicators'].items():
                print(f"\n  📌 {indicator_type.upper()}:")
                for name, values in list(indicators.items())[:3]:  # Mostrar primeros 3
                    print(f"    - {name}: {values}")
        
        print(f"{'='*60}\n")
        
        # Guardar para exportación
        last_analysis = analysis_result
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ ERROR en upload: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@app.get("/analysis/{analysis_type}")
def get_analysis(analysis_type: str):
    """Obtener análisis horizontal o vertical"""
    global last_analysis
    
    if not last_analysis:
        raise HTTPException(status_code=400, detail="No hay datos disponibles. Carga un archivo primero.")
    
    if analysis_type == "horizontal":
        return {
            "type": "horizontal",
            "data": last_analysis.get("horizontal_analysis", {}),
            "available_years": last_analysis.get("available_years", [])
        }
    elif analysis_type == "vertical":
        return {
            "type": "vertical",
            "data": last_analysis.get("vertical_analysis", {}),
            "available_years": last_analysis.get("available_years", [])
        }
    else:
        raise HTTPException(status_code=400, detail="Tipo de análisis no válido. Use 'horizontal' o 'vertical'")

@app.get("/test-data")
def get_test_data():
    """Endpoint de prueba con datos mock para el frontend"""
    return {
        "available_years": [2020, 2021, 2022, 2023],
        "indicators": {
            "liquidez": {
                "razon_corriente": {"2020": 1.8, "2021": 1.9, "2022": 1.7, "2023": 1.6},
                "prueba_acida": {"2020": 1.2, "2021": 1.3, "2022": 1.1, "2023": 1.0},
                "capital_trabajo": {"2020": 40000, "2021": 50000, "2022": 45000, "2023": 35000},
                "clasificacion_liquidez": {"2020": "Sano", "2021": "Sano", "2022": "Sano", "2023": "Regular"}
            },
            "rentabilidad": {
                "roe": {"2020": 0.15, "2021": 0.18, "2022": 0.12, "2023": 0.10},
                "roa": {"2020": 0.08, "2021": 0.09, "2022": 0.07, "2023": 0.06},
                "margen_bruto": {"2020": 0.30, "2021": 0.32, "2022": 0.28, "2023": 0.25},
                "margen_neto": {"2020": 0.10, "2021": 0.12, "2022": 0.08, "2023": 0.06}
            },
            "endeudamiento": {
                "endeudamiento_total": {"2020": 0.45, "2021": 0.42, "2022": 0.48, "2023": 0.52},
                "deuda_patrimonio": {"2020": 0.82, "2021": 0.72, "2022": 0.92, "2023": 1.08},
                "cobertura_intereses": {"2020": 5.5, "2021": 6.2, "2022": 4.8, "2023": 4.2},
                "clasificacion_riesgo": {"2020": "Medio", "2021": "Medio", "2022": "Medio", "2023": "Alto"}
            },
            "rotacion": {
                "rotacion_inventarios": {"2020": 6.5, "2021": 7.2, "2022": 6.8, "2023": 6.3},
                "rotacion_cartera": {"2020": 8.3, "2021": 9.1, "2022": 8.7, "2023": 8.0},
                "rotacion_activos": {"2020": 1.2, "2021": 1.3, "2022": 1.2, "2023": 1.1},
                "dias_inventario": {"2020": 56, "2021": 51, "2022": 54, "2023": 58},
                "dias_cartera": {"2020": 44, "2021": 40, "2022": 42, "2023": 46}
            },
            "quiebra": {
                "z_score": {"2020": 3.2, "2021": 3.5, "2022": 2.8, "2023": 2.3},
                "clasificacion_z": {"2020": "Zona Segura", "2021": "Zona Segura", "2022": "Zona Gris", "2023": "Zona Gris"},
                "probabilidad_quiebra": {"2020": "Baja", "2021": "Baja", "2022": "Media", "2023": "Media"}
            }
        }
    }

@app.get("/export/excel")
async def export_to_excel():
    """Exportar análisis a Excel"""
    global last_analysis
    
    if not last_analysis:
        raise HTTPException(status_code=400, detail="No hay datos para exportar. Primero carga un archivo.")
    
    try:
        excel_file = export_service.create_excel_report(last_analysis)
        
        filename = f"analisis_financiero_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando Excel: {str(e)}")

@app.post("/chat")
async def chat_with_ai(message: dict):
    """Endpoint para chat con IA"""
    try:
        user_message = message.get("message", "").lower()
        financial_data = message.get("financial_data", {})
        
        if not user_message:
            raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

        if OPENAI_AVAILABLE and client:
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
                
                Indicadores de Endeudamiento:
                - Endeudamiento Total: {indicators.get('endeudamiento', {}).get('endeudamiento_total', {})}
                - Deuda/Patrimonio: {indicators.get('endeudamiento', {}).get('deuda_patrimonio', {})}
                
                Indicadores de Rotación:
                - Rotación de Inventarios: {indicators.get('rotacion', {}).get('rotacion_inventarios', {})}
                - Rotación de Cartera: {indicators.get('rotacion', {}).get('rotacion_cartera', {})}
                
                Análisis de Quiebra:
                - Z-Score: {indicators.get('quiebra', {}).get('z_score', {})}
                - Clasificación: {indicators.get('quiebra', {}).get('clasificacion_z', {})}
                
                Años disponibles: {available_years}
                """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado en análisis financiero. Responde de forma clara y profesional."},
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
            responses = {
                "liquidez": "Basándome en tus indicadores de liquidez, la empresa muestra capacidad para cumplir con obligaciones a corto plazo. La razón corriente ideal está entre 1.5 y 2.0.",
                "rentabilidad": "Los indicadores de rentabilidad muestran el desempeño de la empresa. ROE mide rentabilidad sobre capital, ROA sobre activos totales.",
                "endeudamiento": "Los indicadores de endeudamiento evalúan la estructura de deuda. Un endeudamiento total sobre 60% se considera alto.",
                "rotacion": "Los indicadores de rotación miden la eficiencia en el uso de activos. Mayor rotación indica mejor gestión operativa.",
                "quiebra": "El Z-Score de Altman predice probabilidad de quiebra. Mayor a 2.99 es zona segura, entre 1.81-2.99 es zona gris, menor a 1.81 es zona de peligro.",
                "z-score": "El Z-Score combina múltiples ratios financieros. Es una herramienta confiable para evaluar salud financiera empresarial.",
                "exportar": "Puedes exportar el análisis completo a Excel usando el botón de exportación. Incluye todas las hojas con indicadores y análisis.",
                "horizontal": "El análisis horizontal compara estados financieros entre períodos, mostrando variaciones absolutas y porcentuales.",
                "vertical": "El análisis vertical muestra la estructura porcentual de cada cuenta sobre el total, facilitando comparaciones.",
                "hola": "¡Hola! Soy tu asistente de análisis financiero. Puedo explicarte indicadores y analizar tus datos.",
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
            "response": "Puedo explicarte conceptos financieros básicos. ¿Tienes preguntas sobre los indicadores?",
            "status": "success",
            "source": "error_fallback"
        }