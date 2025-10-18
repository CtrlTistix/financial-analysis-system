"""
Rutas de Autenticación
Endpoints: login, logout, refresh token, cambio de contraseña
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas import (
    LoginRequest, 
    LoginResponse, 
    MessageResponse, 
    UserResponse,
    UserChangePassword
)
from app.dependencies import get_db, get_current_active_user, get_client_ip, get_user_agent
from app.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import User, ActionType

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login de usuario
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Retorna token JWT y datos del usuario
    """
    # Autenticar usuario
    user = AuthService.authenticate_user(db, login_data.username, login_data.password)
    
    if not user:
        # Crear log de intento fallido
        AuthService.create_audit_log(
            db=db,
            user_id=None,
            action_type=ActionType.LOGIN,
            description=f"Failed login attempt for username: {login_data.username}",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # Crear sesión en la base de datos
    AuthService.create_user_session(
        db=db,
        user_id=user.id,
        token=access_token,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    # Actualizar última fecha de login
    AuthService.update_last_login(db, user.id)
    
    # Crear log de auditoría
    AuthService.create_audit_log(
        db=db,
        user_id=user.id,
        action_type=ActionType.LOGIN,
        description=f"Successful login for user: {user.username}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    # Preparar respuesta
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout de usuario
    Invalida el token actual
    """
    # Obtener token del header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    # Invalidar sesión
    AuthService.invalidate_session(db, token)
    
    # Crear log de auditoría
    AuthService.create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=ActionType.LOGOUT,
        description=f"User {current_user.username} logged out",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return MessageResponse(
        message="Logout successful",
        detail=f"User {current_user.username} has been logged out"
    )

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener información del usuario actual
    Requiere autenticación
    """
    return UserResponse.from_orm(current_user)

@router.post("/change-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def change_password(
    password_data: UserChangePassword,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario actual
    
    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 6 caracteres)
    """
    # Verificar contraseña actual
    if not AuthService.verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Verificar que la nueva contraseña sea diferente
    if AuthService.verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Actualizar contraseña
    current_user.password_hash = AuthService.get_password_hash(password_data.new_password)
    db.commit()
    
    # Crear log de auditoría
    AuthService.create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=ActionType.UPDATE_USER,
        description="Password changed successfully",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return MessageResponse(
        message="Password changed successfully",
        detail="Your password has been updated"
    )

@router.post("/validate-token", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def validate_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Validar si el token actual es válido
    Útil para verificar la sesión en el frontend
    """
    return MessageResponse(
        message="Token is valid",
        detail=f"User {current_user.username} is authenticated"
    )