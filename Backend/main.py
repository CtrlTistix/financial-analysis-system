from app.export_routes import router as export_router
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
from typing import Dict
import io
import os
from dotenv import load_dotenv
from datetime import datetime
import uvicorn

load_dotenv()

from app.services.analysis_service import AnalysisService
from app.services.export_service import ExportService
from app.model import User, Session, AuditLog, UserRole, ActionType
# Importar sistema de autenticación
from app.database import init_db, get_db
from app.auth_routes import router as auth_router
from app.user_routes import router as user_router
from app.dependencies import get_current_active_user
from app.model import User
from app.export_routes import router as export_router, set_last_analysis
from app.reports_routes import router as reports_router, set_last_analysis as set_reports_analysis

app = FastAPI(title="Financial Analysis API")
app.include_router(export_router)
app.include_router(reports_router)
# CORS actualizado para incluir tu dominio de Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://financial-analysis-system-two.vercel.app",
        "https://financial-analysis-system-475u3dd67-ctrltistixs-projects.vercel.app",  # Añadir URL de preview
        "https://*.vercel.app",  # Permitir todos los subdominios de Vercel
        "https://financial-analysis-system-qhnz.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Inicializar base de datos al inicio
@app.on_event("startup")
async def startup_event():
    """Inicializar base de datos al arrancar"""
    print("🚀 Iniciando Financial Analysis API...")
    init_db()
    print("✅ Base de datos inicializada")

OPENAI_AVAILABLE = False
client = None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
        from app.models import Base
        from app.database import engine
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas de base de datos verificadas/creadas")
except Exception as e:
        print(f"⚠️ Error creando tablas: {e}")
    
print("✅ Base de datos inicializada")

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

# ============ INCLUIR ROUTERS DE AUTENTICACIÓN ============
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(export_router)
# ============ ENDPOINTS PÚBLICOS ============

@app.get("/")
def read_root():
    return {
        "message": "🚀 Financial Analysis API is running!", 
        "status": "success",
        "openai_status": "available" if OPENAI_AVAILABLE else "fallback_mode",
        "version": "2.1",
        "authentication": "enabled",
        "password_reset": "enabled",
        "features": [
            "Indicadores de Liquidez",
            "Indicadores de Rentabilidad",
            "Indicadores de Endeudamiento",
            "Indicadores de Rotación",
            "Análisis de Quiebra (Z-Score)",
            "Análisis Horizontal",
            "Análisis Vertical",
            "Exportación a Excel",
            "ChatBot con IA",
            "Sistema de Autenticación",
            "Gestión de Usuarios",
            "Restablecimiento de Contraseña"
        ]
    }

@app.get("/test-data")
def get_test_data():
    """Endpoint de prueba con datos mock para el frontend - PÚBLICO"""
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

@app.get("/analysis/{analysis_type}")
def get_analysis(analysis_type: str):
    """Obtener análisis horizontal o vertical - PÚBLICO"""
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

# ============ ENDPOINTS PROTEGIDOS (REQUIEREN AUTENTICACIÓN) ============

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint para subir archivos Excel y analizarlos - REQUIERE AUTENTICACIÓN"""
    global last_analysis
    
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel")
        
        contents = await file.read()
        try:
            df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        except Exception as excel_err:
            raise HTTPException(
                status_code=400,
                detail=f"Error al leer el archivo Excel: {str(excel_err)}. Asegúrate de que sea un archivo .xlsx válido."
            )
        
        print(f"\n{'='*60}")
        print(f"📄 Archivo recibido: {file.filename}")
        print(f"👤 Usuario: {current_user.username} ({current_user.role})")
        print(f"📊 Dimensiones del DataFrame: {df.shape}")
        print(f"📋 Primeras columnas: {df.columns.tolist()[:5]}")
        print(f"{'='*60}\n")
        
        analysis_result = analysis_service.analyze_financial_data(df)
        
        if not analysis_result or not analysis_result.get('available_years'):
            raise HTTPException(
                status_code=400, 
                detail="No se pudieron extraer datos del archivo. Verifica que el formato sea correcto."
            )
        
        analysis_result["filename"] = file.filename
        analysis_result["upload_date"] = datetime.now().isoformat()
        analysis_result["uploaded_by"] = current_user.username
        analysis_result["message"] = "Análisis financiero completado exitosamente"
        
        last_analysis = analysis_result
        set_last_analysis(analysis_result)
        set_reports_analysis(analysis_result)

        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ ERROR en upload: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@app.get("/export/excel")
async def export_to_excel(
    current_user: User = Depends(get_current_active_user)
):
    """Exportar análisis a Excel - REQUIERE AUTENTICACIÓN"""
    global last_analysis
    
    if not last_analysis:
        raise HTTPException(status_code=400, detail="No hay datos para exportar. Primero carga un archivo.")
    
    try:
        print(f"📊 Exportando análisis para usuario: {current_user.username}")
        
        excel_file = export_service.create_excel_report(last_analysis)
        
        filename = f"analisis_financiero_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando Excel: {str(e)}")

@app.post("/chat")
async def chat_with_ai(
    message: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint para chat con IA - REQUIERE AUTENTICACIÓN"""
    try:
        user_message = message.get("message", "").lower()
        financial_data = message.get("financial_data", {})
        
        if not user_message:
            raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

        print(f"💬 Chat request from user: {current_user.username}")

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
                    {
                        "role": "system", 
                        "content": "Eres un asistente especializado en análisis financiero. Responde SIEMPRE en máximo 25 palabras de forma concisa, clara y directa."
                    },
                    {"role": "user", "content": f"{context}\n\nPregunta: {user_message}"}
                ],
                max_tokens=50,
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
                "liquidez": "Tu liquidez es adecuada si la razón corriente está entre 1.5-2.0. Valores menores indican riesgo.",
                "rentabilidad": "ROE mide rentabilidad sobre capital; ROA sobre activos totales. Mayores valores son mejores.",
                "endeudamiento": "Endeudamiento sobre 60% se considera alto. Indica mayor riesgo financiero.",
                "rotacion": "Mayor rotación indica mejor gestión operativa. Mide eficiencia en uso de activos.",
                "quiebra": "Z-Score >2.99 es seguro, 1.81-2.99 es zona gris, <1.81 es peligro.",
                "z-score": "Z-Score combina múltiples ratios. Es confiable para evaluar salud financiera.",
                "exportar": "Usa el botón de exportación para descargar el análisis completo en Excel.",
                "horizontal": "Análisis horizontal compara estados financieros entre períodos, muestra variaciones.",
                "vertical": "Análisis vertical muestra estructura porcentual sobre el total para comparar.",
                "hola": "Hola! Soy tu asistente financiero. ¿Qué deseas saber?",
            }

            response = "Puedo ayudarte con conceptos financieros. ¿Preguntas sobre indicadores?"
            
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

# Punto de entrada para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )