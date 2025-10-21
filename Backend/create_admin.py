"""
Script para crear usuario administrador inicial
Ejecutar: python create_admin.py
"""
import sys
import os

# Agregar el directorio Backend al path para poder importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import User, UserRole, Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    """Crear usuario administrador inicial"""
    print("🔧 Creando usuario administrador...")
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin:
            print("❌ El usuario 'admin' ya existe")
            print(f"   ID: {existing_admin.id}")
            print(f"   Email: {existing_admin.email}")
            return
        
        # Crear usuario admin
        hashed_password = pwd_context.hash("admin123")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=hashed_password,
            first_name="Admin",
            last_name="System",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Usuario administrador creado exitosamente!")
        print("=" * 50)
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@example.com")
        print(f"   Role: {admin_user.role}")
        print("=" * 50)
        print("⚠️  Recuerda cambiar la contraseña después del primer login")
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        db.rollback()
    finally:
        db.close()

def create_test_user():
    """Crear usuario de prueba (cliente)"""
    print("\n🔧 Creando usuario de prueba...")
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existe
        existing_user = db.query(User).filter(User.username == "testuser").first()
        
        if existing_user:
            print("❌ El usuario 'testuser' ya existe")
            return
        
        # Crear usuario de prueba
        hashed_password = pwd_context.hash("test123")
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hashed_password,
            first_name="Test",
            last_name="User",
            role=UserRole.CLIENT,
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Usuario de prueba creado exitosamente!")
        print("=" * 50)
        print(f"   Username: testuser")
        print(f"   Password: test123")
        print(f"   Email: test@example.com")
        print(f"   Role: {test_user.role}")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error al crear usuario de prueba: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  CREACIÓN DE USUARIOS INICIALES")
    print("=" * 50 + "\n")
    
    create_admin()
    
    # Preguntar si desea crear usuario de prueba
    response = input("\n¿Deseas crear también un usuario de prueba (cliente)? (s/n): ")
    if response.lower() in ['s', 'si', 'y', 'yes']:
        create_test_user()
    
    print("\n✅ Proceso completado\n")