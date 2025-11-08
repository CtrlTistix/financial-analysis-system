"""
Script de migración para agregar tabla password_reset_tokens
"""
from app.database import engine
from app.models import Base

def run_migration():
    """Crear tabla password_reset_tokens"""
    print("🔄 Ejecutando migración: password_reset_tokens table...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Migración completada exitosamente")
        print("✅ Tabla password_reset_tokens creada")
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        raise

if __name__ == "__main__":
    run_migration()