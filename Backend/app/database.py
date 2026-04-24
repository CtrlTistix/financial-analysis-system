"""
Configuración de Base de Datos PostgreSQL
Compatible con Render y desarrollo local
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.models import Base

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

connect_args = {
    "connect_timeout": 10,
    "options": "-c timezone=utc"
}

DATABASE_SSLMODE = os.getenv("DATABASE_SSLMODE", "")
if DATABASE_SSLMODE:
    connect_args["sslmode"] = DATABASE_SSLMODE
elif not any(host in DATABASE_URL for host in ("localhost", "127.0.0.1", "db:")):
    connect_args["sslmode"] = "require"

# Crear engine con configuración optimizada
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=300,    # Reciclar conexiones cada 5 minutos
    pool_size=10,        # Tamaño del pool de conexiones
    max_overflow=20,     # Conexiones adicionales permitidas
    echo=False,          # No mostrar SQL en logs (cambiar a True para debug)
    connect_args=connect_args
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Inicializar base de datos
    Crear todas las tablas si no existen
    """
    import app.models  # Registrar todos los modelos en el metadata compartido
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