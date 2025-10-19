"""
Servicio de Autenticación y Autorización
Maneja login, tokens JWT, y validación de usuarios
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.model import User, Session as UserSession, AuditLog, UserRole, ActionType
import secrets
import os

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Contexto de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Servicio de autenticación"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generar hash de contraseña"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decodificar y validar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def create_user_session(
        db: Session, 
        user_id: int, 
        token: str, 
        ip_address: str = None, 
        user_agent: str = None
    ) -> UserSession:
        """Crear sesión de usuario"""
        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        session = UserSession(
            user_id=user_id,
            session_token=token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def invalidate_session(db: Session, token: str) -> bool:
        """Invalidar sesión (logout)"""
        session = db.query(UserSession).filter(
            UserSession.session_token == token,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def create_audit_log(
        db: Session,
        user_id: int,
        action_type: ActionType,
        description: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> AuditLog:
        """Crear registro de auditoría"""
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

    @staticmethod
    def update_last_login(db: Session, user_id: int) -> None:
        """Actualizar última fecha de login"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()

    @staticmethod
    def get_current_user_from_token(db: Session, token: str) -> User:
        """Obtener usuario actual desde token"""
        try:
            payload = AuthService.decode_token(token)
            user_id: int = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        return user

    @staticmethod
    def check_admin_role(user: User) -> None:
        """Verificar si el usuario es administrador"""
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions. Admin role required."
            )