"""
Dependencias de FastAPI
Gestión de base de datos, autenticación y autorización
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Generator
from app.database import SessionLocal
from app.auth_service import AuthService
from app.model import User, UserRole

# Seguridad HTTP Bearer
security = HTTPBearer()

def get_db() -> Generator:
    """
    Dependency para obtener sesión de base de datos
    Se cierra automáticamente después de cada request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obtener usuario actual desde token JWT
    Valida el token y retorna el usuario
    """
    token = credentials.credentials
    
    # Validar que el token no esté vacío
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario desde el token
    user = AuthService.get_current_user_from_token(db, token)
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para obtener usuario activo
    Verifica que el usuario esté activo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency para verificar que el usuario sea administrador
    Solo administradores pueden acceder a rutas protegidas con esta dependency
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user

def get_client_ip(request: Request) -> str:
    """
    Obtener IP del cliente
    Considera proxy headers para obtener la IP real
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    """Obtener User-Agent del cliente"""
    return request.headers.get("User-Agent", "unknown")