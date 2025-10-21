"""
Rutas de Gestión de Usuarios
Solo accesibles por administradores
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas import UserCreate, UserUpdate, UserResponse, MessageResponse
from app.dependencies import get_db, get_current_admin_user, get_client_ip, get_user_agent
from app.auth_service import AuthService
from app.model import User, ActionType

router = APIRouter(prefix="/api/users", tags=["User Management"])

@router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de todos los usuarios
    Solo administradores
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Obtener usuario por ID
    Solo administradores
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return UserResponse.from_orm(user)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Crear nuevo usuario
    Solo administradores
    
    - **username**: Nombre de usuario único (3-80 caracteres)
    - **email**: Correo electrónico único
    - **password**: Contraseña (mínimo 6 caracteres)
    - **first_name**: Nombre (opcional)
    - **last_name**: Apellido (opcional)
    - **role**: Rol del usuario (admin o client)
    """
    # Verificar si el username ya existe
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Verificar si el email ya existe
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Crear nuevo usuario
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=AuthService.get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Crear log de auditoría
    AuthService.create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=ActionType.CREATE_USER,
        description=f"Created new user: {new_user.username} with role: {new_user.role}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return UserResponse.from_orm(new_user)

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar usuario existente
    Solo administradores
    
    Permite actualizar: email, first_name, last_name, role, is_active
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Actualizar campos si se proporcionan
    update_data = user_data.dict(exclude_unset=True)
    
    # Verificar email único si se está actualizando
    if 'email' in update_data and update_data['email'] != user.email:
        existing_email = db.query(User).filter(User.email == update_data['email']).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Crear log de auditoría
    AuthService.create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=ActionType.UPDATE_USER,
        description=f"Updated user: {user.username}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return UserResponse.from_orm(user)

@router.delete("/{user_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar usuario
    Solo administradores
    
    No se puede eliminar a sí mismo
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    username = user.username
    
    # Crear log de auditoría antes de eliminar
    AuthService.create_audit_log(
        db=db,
        user_id=current_user.id,
        action_type=ActionType.DELETE_USER,
        description=f"Deleted user: {username}",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    # Eliminar usuario
    db.delete(user)
    db.commit()
    
    return MessageResponse(
        message="User deleted successfully",
        detail=f"User {username} has been removed from the system"
    )