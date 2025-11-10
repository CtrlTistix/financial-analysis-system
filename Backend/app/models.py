"""
Modelos de Base de Datos - Sistema de Autenticación
SQLAlchemy Models para PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    """Enum para roles de usuario"""
    ADMIN = "admin"
    CLIENT = "client"

class ActionType(str, enum.Enum):
    """Enum para tipos de acciones en auditoría"""
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD_FILE = "upload_file"
    EXPORT_REPORT = "export_report"
    VIEW_DASHBOARD = "view_dashboard"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"

class User(Base):
    """Modelo de Usuario"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relaciones
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

class Session(Base):
    """Modelo de Sesión de Usuario"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(500), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relación
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

class AuditLog(Base):
    """Modelo de Auditoría de Acciones"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(SQLEnum(ActionType), nullable=False)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action_type}', user_id={self.user_id})>"

class PasswordResetToken(Base):
    """Modelo de Token de Restablecimiento de Contraseña"""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

    # Relación
    user = relationship("User", back_populates="password_reset_tokens")

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, used={self.used})>"
    
class Configuration(Base):
    """Modelo de Configuración del Sistema"""
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Configuración de la empresa
    nombre_empresa = Column(String(200), nullable=True)
    periodo_fiscal = Column(String(20), nullable=True, default="2020")
    moneda = Column(String(10), nullable=True, default="USD")
    
    # Configuración de cálculos
    dias_anio = Column(Integer, nullable=False, default=360)
    metodo_depreciacion = Column(String(50), nullable=True, default="lineal")
    
    # Configuración de archivos Excel
    fila_inicio = Column(Integer, nullable=False, default=2)
    permitir_filas_vacias = Column(Boolean, default=True, nullable=False)
    formato_numeros = Column(String(20), nullable=True, default="europeo")
    
    # Configuración de reportes
    incluir_graficos = Column(Boolean, default=True, nullable=False)
    formato_reporte = Column(String(20), nullable=True, default="xlsx")
    incluir_interpretacion = Column(Boolean, default=True, nullable=False)
    
    # Configuración de notificaciones
    notificaciones_email = Column(Boolean, default=True, nullable=False)
    email_admin = Column(String(120), nullable=True)
    
    # Configuración de seguridad
    requiere_autenticacion = Column(Boolean, default=True, nullable=False)
    expiracion_sesion = Column(Integer, nullable=False, default=60)
    
    # Configuración del chat AI
    chat_habilitado = Column(Boolean, default=True, nullable=False)
    modelo_ia = Column(String(50), nullable=True, default="gpt-4")
    contexto_corporativo = Column(Text, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Configuration(id={self.id}, empresa='{self.nombre_empresa}')>"