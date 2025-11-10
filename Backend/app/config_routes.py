"""
Rutas para gestión de configuración del sistema
Crear este archivo en: backend/app/config_routes.py
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.model import Configuration, User
from app.schemas import ConfigurationCreate, ConfigurationUpdate, ConfigurationResponse
from app.dependencies import get_current_active_user, require_admin

router = APIRouter(prefix="/api/configuracion", tags=["configuracion"])

@router.get("/", response_model=ConfigurationResponse)
async def get_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener configuración actual del sistema
    Requiere autenticación
    """
    try:
        # Buscar configuración existente (debería haber solo una)
        config = db.query(Configuration).first()
        
        # Si no existe, crear configuración por defecto
        if not config:
            config = Configuration()
            db.add(config)
            db.commit()
            db.refresh(config)
        
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo configuración: {str(e)}")

@router.put("/", response_model=ConfigurationResponse)
async def update_configuration(
    config_data: ConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Solo admin puede modificar
):
    """
    Actualizar configuración del sistema
    Solo administradores pueden modificar la configuración
    """
    try:
        # Buscar configuración existente
        config = db.query(Configuration).first()
        
        # Si no existe, crear nueva
        if not config:
            config = Configuration()
            db.add(config)
        
        # Actualizar campos
        for field, value in config_data.dict(exclude_unset=True).items():
            setattr(config, field, value)
        
        db.commit()
        db.refresh(config)
        
        return config
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error actualizando configuración: {str(e)}")

@router.post("/reset", response_model=ConfigurationResponse)
async def reset_configuration(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Restaurar configuración a valores por defecto
    Solo administradores
    """
    try:
        # Buscar configuración existente
        config = db.query(Configuration).first()
        
        if config:
            # Eliminar y crear nueva con valores por defecto
            db.delete(config)
            db.commit()
        
        # Crear configuración por defecto
        config = Configuration()
        db.add(config)
        db.commit()
        db.refresh(config)
        
        return config
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error restaurando configuración: {str(e)}")

       