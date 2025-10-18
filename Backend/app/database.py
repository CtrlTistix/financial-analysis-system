"""
Configuración de Base de Datos PostgreSQL
Compatible con Render y desarrollo local
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener URL de base de datos desde variables de entorno
# Render proporciona automáticamente DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/financial_db"
)

# Render usa postgres:// pero SQLAlchemy necesita postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Crear engine con configuración optimizada
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=300,    # Reciclar conexiones cada 5 minutos
    pool_size=10,        # Tamaño del pool de conexiones
    max_overflow=20,     # Conexiones adicionales permitidas
    echo=False,          # No mostrar SQL en logs (cambiar a True para debug)
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    }
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def init_db():
    """
    Inicializar base de datos
    Crear todas las tablas si no existen
    """
    from app.models import User, Session, AuditLog  # Importar modelos
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_db():
    """
    Dependency para obtener sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()