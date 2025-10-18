"""
Schemas Pydantic para validación de datos
Request/Response models
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

# ============ ENUMS ============

class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"

# ============ AUTH SCHEMAS ============

class LoginRequest(BaseModel):
    """Schema para solicitud de login"""
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=6, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }

class LoginResponse(BaseModel):
    """Schema para respuesta de login"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "role": "admin"
                },
                "expires_in": 3600
            }
        }

class RefreshTokenRequest(BaseModel):
    """Schema para renovar token"""
    refresh_token: str

# ============ USER SCHEMAS ============

class UserBase(BaseModel):
    """Base schema de usuario"""
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRoleEnum = UserRoleEnum.CLIENT

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.replace('_', '').replace('-', '').isalnum(), 'Username must be alphanumeric'
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "securepassword123",
                "role": "client"
            }
        }

class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None

class UserChangePassword(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)

class UserResponse(BaseModel):
    """Schema de respuesta de usuario"""
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

# ============ GENERAL RESPONSES ============

class MessageResponse(BaseModel):
    """Schema para mensajes simples"""
    message: str
    detail: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation successful",
                "detail": "User created successfully"
            }
        }

class ErrorResponse(BaseModel):
    """Schema para errores"""
    error: str
    detail: str
    status_code: int

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "Invalid credentials",
                "status_code": 401
            }
        }