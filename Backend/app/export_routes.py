from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime

from app.dependencies import get_current_active_user
from app.model import User
from app.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["export"])
export_service = ExportService()

# Variable global para almacenar el último análisis
_last_analysis = None

def set_last_analysis(data):
    """Actualiza el último análisis desde main.py"""
    global _last_analysis
    _last_analysis = data

def get_last_analysis():
    """Obtiene el último análisis disponible"""
    return _last_analysis


@router.get("/excel/complete")
async def export_complete_excel(
    current_user: User = Depends(get_current_active_user)
):
    """
    Exportar análisis completo a Excel
    Incluye: Portada, Resumen, Indicadores, Análisis H/V, Datos Crudos
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400, 
            detail="No hay datos para exportar. Primero carga un archivo."
        )
    
    try:
        excel_file = export_service.create_excel_report(
            analysis_data, 
            report_type="complete"
        )
        
        filename = f"analisis_completo_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ Error en export_complete_excel: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando reporte completo: {str(e)}"
        )


@router.get("/excel/summary")
async def export_summary_excel(
    current_user: User = Depends(get_current_active_user)
):
    """
    Exportar resumen ejecutivo a Excel
    Incluye: Portada y Resumen Ejecutivo
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400, 
            detail="No hay datos para exportar. Primero carga un archivo."
        )
    
    try:
        excel_file = export_service.create_excel_report(
            analysis_data, 
            report_type="summary"
        )
        
        filename = f"resumen_ejecutivo_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ Error en export_summary_excel: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando resumen: {str(e)}"
        )


@router.get("/excel/indicators")
async def export_indicators_excel(
    current_user: User = Depends(get_current_active_user)
):
    """
    Exportar solo indicadores a Excel
    Incluye: Liquidez, Rentabilidad, Endeudamiento, Rotación, Quiebra
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400, 
            detail="No hay datos para exportar. Primero carga un archivo."
        )
    
    try:
        excel_file = export_service.create_excel_report(
            analysis_data, 
            report_type="indicators"
        )
        
        filename = f"indicadores_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ Error en export_indicators_excel: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando indicadores: {str(e)}"
        )


@router.get("/excel/analysis")
async def export_analysis_excel(
    current_user: User = Depends(get_current_active_user)
):
    """
    Exportar análisis horizontal y vertical a Excel
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400, 
            detail="No hay datos para exportar. Primero carga un archivo."
        )
    
    if not analysis_data.get('horizontal_analysis') and not analysis_data.get('vertical_analysis'):
        raise HTTPException(
            status_code=400,
            detail="No hay análisis horizontal o vertical disponible"
        )
    
    try:
        excel_file = export_service.create_excel_report(
            analysis_data, 
            report_type="analysis"
        )
        
        filename = f"analisis_h_v_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ Error en export_analysis_excel: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando análisis: {str(e)}"
        )


@router.get("/excel/comparative")
async def export_comparative_excel(
    current_user: User = Depends(get_current_active_user)
):
    """
    Exportar análisis comparativo multianual a Excel
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400, 
            detail="No hay datos para exportar. Primero carga un archivo."
        )
    
    try:
        excel_file = export_service.create_excel_report(
            analysis_data, 
            report_type="comparative"
        )
        
        filename = f"comparativo_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ Error en export_comparative_excel: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando comparativo: {str(e)}"
        )


@router.get("/csv")
async def export_to_csv(
    category: Optional[str] = Query(None, description="Categoría específica a exportar"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Exportar datos a formato CSV
    
    Args:
        category: liquidez, rentabilidad, endeudamiento, rotacion, quiebra (opcional)
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400, 
            detail="No hay datos para exportar. Primero carga un archivo."
        )
    
    try:
        csv_file = export_service.export_to_csv(analysis_data, category)
        
        category_name = category if category else "completo"
        filename = f"datos_{category_name}_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            csv_file,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ Error en export_to_csv: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando CSV: {str(e)}"
        )


@router.get("/json")
async def export_to_json(
    current_user: User = Depends(get_current_active_user)
):
    """
    Exportar datos a formato JSON
    """
    analysis_data = get_last_analysis()
    
    if not analysis_data:
        raise HTTPException(
            status_code=400, 
            detail="No hay datos para exportar. Primero carga un archivo."
        )
    
    try:
        json_data = export_service.export_to_json(analysis_data)
        
        filename = f"datos_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return StreamingResponse(
            iter([json_data]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"❌ Error en export_to_json: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando JSON: {str(e)}"
        )


@router.get("/formats")
async def get_available_formats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener formatos de exportación disponibles
    """
    return {
        "formats": [
            {
                "id": "excel_complete",
                "name": "Excel Completo",
                "description": "Reporte completo con todas las secciones",
                "endpoint": "/export/excel/complete",
                "icon": "📊"
            },
            {
                "id": "excel_summary",
                "name": "Resumen Ejecutivo",
                "description": "Portada y resumen de indicadores clave",
                "endpoint": "/export/excel/summary",
                "icon": "📋"
            },
            {
                "id": "excel_indicators",
                "name": "Indicadores",
                "description": "Solo indicadores financieros detallados",
                "endpoint": "/export/excel/indicators",
                "icon": "📈"
            },
            {
                "id": "excel_analysis",
                "name": "Análisis H/V",
                "description": "Análisis horizontal y vertical",
                "endpoint": "/export/excel/analysis",
                "icon": "📉"
            },
            {
                "id": "excel_comparative",
                "name": "Comparativo",
                "description": "Análisis comparativo multianual",
                "endpoint": "/export/excel/comparative",
                "icon": "🔄"
            },
            {
                "id": "csv",
                "name": "CSV",
                "description": "Datos en formato CSV para análisis",
                "endpoint": "/export/csv",
                "icon": "📄"
            },
            {
                "id": "json",
                "name": "JSON",
                "description": "Datos en formato JSON para APIs",
                "endpoint": "/export/json",
                "icon": "🔧"
            }
        ]
    }