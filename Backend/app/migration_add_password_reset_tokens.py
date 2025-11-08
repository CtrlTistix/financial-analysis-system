"""
Script de migración para agregar tabla password_reset_tokens
Ejecutar después de actualizar los modelos
"""

# Si estás usando Alembic para migraciones, crea una migración así:
# alembic revision -m "add password reset tokens table"

# Si no usas Alembic, puedes ejecutar este script directamente:

from app.database import engine
from app.model import Base

def run_migration():
    """Crear tabla password_reset_tokens"""
    print("🔄 Ejecutando migración: password_reset_tokens table...")
    
    try:
        # Esto creará solo las tablas nuevas que no existan
        Base.metadata.create_all(bind=engine)
        print("✅ Migración completada exitosamente")
        print("✅ Tabla password_reset_tokens creada")
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        raise

if __name__ == "__main__":
    run_migration()