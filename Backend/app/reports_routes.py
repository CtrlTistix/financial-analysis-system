from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import Dict, List

from app.dependencies import get_current_active_user
from app.model import User
from app.services.export_service import ExportService
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])
export_service = ExportService()
report_service = ReportService()

# Variable global para almacenar el último análisis
_last_analysis = None

def set_last_analysis(data):
    """Actualiza el último análisis"""
    global _last_analysis
    _last_analysis = data

def get_last_analysis():
    """Obtiene el último análisis"""
    return _last_analysis


@router.get("/liquidez")
async def generate_liquidity_report(
    current_user: User = Depends(get_current_active_user)
):
    """
    📊 Reporte de Liquidez
    Análisis detallado de la capacidad de pago a corto plazo
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400,
            detail="No hay datos para generar el reporte. Carga un archivo primero."
        )
    
    try:
        excel_file = report_service.create_liquidity_report(analysis_data)
        filename = f"reporte_liquidez_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"❌ Error generando reporte de liquidez: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/rentabilidad")
async def generate_profitability_report(
    current_user: User = Depends(get_current_active_user)
):
    """
    💰 Reporte de Rentabilidad
    Análisis de márgenes, ROE, ROA y capacidad de generar utilidades
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400,
            detail="No hay datos para generar el reporte. Carga un archivo primero."
        )
    
    try:
        excel_file = report_service.create_profitability_report(analysis_data)
        filename = f"reporte_rentabilidad_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"❌ Error generando reporte de rentabilidad: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/endeudamiento")
async def generate_debt_report(
    current_user: User = Depends(get_current_active_user)
):
    """
    📉 Reporte de Endeudamiento
    Análisis de estructura de deuda y capacidad de pago
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400,
            detail="No hay datos para generar el reporte. Carga un archivo primero."
        )
    
    try:
        excel_file = report_service.create_debt_report(analysis_data)
        filename = f"reporte_endeudamiento_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"❌ Error generando reporte de endeudamiento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/eficiencia")
async def generate_efficiency_report(
    current_user: User = Depends(get_current_active_user)
):
    """
    🔄 Reporte de Eficiencia Operativa
    Análisis de rotación de inventarios, cartera y activos
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400,
            detail="No hay datos para generar el reporte. Carga un archivo primero."
        )
    
    try:
        excel_file = report_service.create_efficiency_report(analysis_data)
        filename = f"reporte_eficiencia_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"❌ Error generando reporte de eficiencia: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/riesgo")
async def generate_risk_report(
    current_user: User = Depends(get_current_active_user)
):
    """
    ⚠️ Reporte de Análisis de Riesgo
    Z-Score, probabilidad de quiebra y alertas financieras
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400,
            detail="No hay datos para generar el reporte. Carga un archivo primero."
        )
    
    try:
        excel_file = report_service.create_risk_report(analysis_data)
        filename = f"reporte_riesgo_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"❌ Error generando reporte de riesgo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/ejecutivo")
async def generate_executive_report(
    current_user: User = Depends(get_current_active_user)
):
    """
    📋 Reporte Ejecutivo
    Resumen de alto nivel para directivos y toma de decisiones
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400,
            detail="No hay datos para generar el reporte. Carga un archivo primero."
        )
    
    try:
        excel_file = report_service.create_executive_report(analysis_data)
        filename = f"reporte_ejecutivo_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"❌ Error generando reporte ejecutivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/completo")
async def generate_complete_report(
    current_user: User = Depends(get_current_active_user)
):
    """
    📊 Reporte Completo
    Análisis integral con todas las secciones y recomendaciones
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400,
            detail="No hay datos para generar el reporte. Carga un archivo primero."
        )
    
    try:
        excel_file = report_service.create_complete_report(analysis_data)
        filename = f"reporte_completo_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"❌ Error generando reporte completo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/comparativo-sectorial")
async def generate_sector_comparison_report(
    current_user: User = Depends(get_current_active_user)
):
    """
    📈 Reporte Comparativo Sectorial
    Benchmarking con promedios de la industria
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400,
            detail="No hay datos para generar el reporte. Carga un archivo primero."
        )
    
    try:
        excel_file = report_service.create_sector_comparison_report(analysis_data)
        filename = f"reporte_comparativo_sectorial_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"❌ Error generando reporte comparativo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/available")
async def get_available_reports(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener lista de reportes disponibles
    """
    return {
        "reports": [
            {
                "id": "liquidez",
                "name": "Reporte de Liquidez",
                "description": "Análisis detallado de capacidad de pago a corto plazo",
                "icon": "💧",
                "color": "#3b82f6",
                "endpoint": "/reports/liquidez",
                "sections": ["Razón Corriente", "Prueba Ácida", "Capital de Trabajo", "Tendencias"]
            },
            {
                "id": "rentabilidad",
                "name": "Reporte de Rentabilidad",
                "description": "Análisis de márgenes y retorno sobre inversión",
                "icon": "💰",
                "color": "#10b981",
                "endpoint": "/reports/rentabilidad",
                "sections": ["ROE", "ROA", "Márgenes", "Comparativos"]
            },
            {
                "id": "endeudamiento",
                "name": "Reporte de Endeudamiento",
                "description": "Estructura de deuda y capacidad de pago",
                "icon": "📉",
                "color": "#f59e0b",
                "endpoint": "/reports/endeudamiento",
                "sections": ["Nivel de Deuda", "Cobertura", "Apalancamiento"]
            },
            {
                "id": "eficiencia",
                "name": "Reporte de Eficiencia",
                "description": "Rotación de activos e indicadores operativos",
                "icon": "🔄",
                "color": "#8b5cf6",
                "endpoint": "/reports/eficiencia",
                "sections": ["Rotación Inventarios", "Ciclo Operativo", "Rotación Activos"]
            },
            {
                "id": "riesgo",
                "name": "Reporte de Riesgo",
                "description": "Z-Score y análisis de probabilidad de quiebra",
                "icon": "⚠️",
                "color": "#ef4444",
                "endpoint": "/reports/riesgo",
                "sections": ["Z-Score Altman", "Alertas", "Recomendaciones"]
            },
            {
                "id": "ejecutivo",
                "name": "Reporte Ejecutivo",
                "description": "Resumen de alto nivel para directivos",
                "icon": "📋",
                "color": "#6366f1",
                "endpoint": "/reports/ejecutivo",
                "sections": ["KPIs Clave", "Dashboard", "Conclusiones"]
            },
            {
                "id": "completo",
                "name": "Reporte Completo",
                "description": "Análisis integral con todas las secciones",
                "icon": "📊",
                "color": "#06b6d4",
                "endpoint": "/reports/completo",
                "sections": ["Todo incluido", "Gráficas", "Recomendaciones"]
            },
            {
                "id": "comparativo",
                "name": "Comparativo Sectorial",
                "description": "Benchmarking con promedios de industria",
                "icon": "📈",
                "color": "#ec4899",
                "endpoint": "/reports/comparativo-sectorial",
                "sections": ["Benchmarking", "Posicionamiento", "Oportunidades"]
            }
        ]
    }