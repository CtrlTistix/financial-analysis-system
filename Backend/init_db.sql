-- =============================================
-- SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS
-- Sistema de Análisis Financiero con IA
-- PostgreSQL 15+
-- =============================================

-- Crear extensión para UUID si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- TABLA: USERS
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'client')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    CONSTRAINT username_min_length CHECK (LENGTH(username) >= 3),
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Índices para users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- =============================================
-- TABLA: SESSIONS
-- =============================================
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(500) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE
);

-- Índices para sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- =============================================
-- TABLA: AUDIT_LOGS
-- =============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action_type VARCHAR(50) NOT NULL CHECK (
        action_type IN (
            'login', 'logout', 'upload_file', 'export_report', 
            'view_dashboard', 'create_user', 'update_user', 'delete_user'
        )
    ),
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_logs_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE SET NULL
);

-- Índices para audit_logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- =============================================
-- FUNCIÓN: Actualizar updated_at automáticamente
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para users
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- FUNCIÓN: Limpiar sesiones expiradas
-- =============================================
CREATE OR REPLACE FUNCTION clean_expired_sessions()
RETURNS void AS $$
BEGIN
    UPDATE sessions 
    SET is_active = FALSE 
    WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE;
    
    DELETE FROM sessions 
    WHERE expires_at < (CURRENT_TIMESTAMP - INTERVAL '30 days');
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- DATOS INICIALES: Usuario Administrador
-- =============================================
-- Contraseña: admin123 (CAMBIAR EN PRODUCCIÓN)
-- Hash generado con bcrypt

INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active)
VALUES (
    'admin',
    'admin@financial-system.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LwlP.dVqn5pHZ9tte',
    'Admin',
    'System',
    'admin',
    TRUE
)
ON CONFLICT (username) DO NOTHING;

-- Usuario de prueba cliente
-- Contraseña: client123
INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_active)
VALUES (
    'cliente1',
    'cliente1@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LwlP.dVqn5pHZ9tte',
    'Cliente',
    'Demo',
    'client',
    TRUE
)
ON CONFLICT (username) DO NOTHING;

-- =============================================
-- VISTAS ÚTILES
-- =============================================

-- Vista de sesiones activas
CREATE OR REPLACE VIEW active_sessions AS
SELECT 
    s.id,
    s.user_id,
    u.username,
    u.email,
    u.role,
    s.created_at,
    s.expires_at,
    s.ip_address,
    s.user_agent
FROM sessions s
JOIN users u ON s.user_id = u.id
WHERE s.is_active = TRUE 
  AND s.expires_at > CURRENT_TIMESTAMP
ORDER BY s.created_at DESC;

-- Vista de actividad de usuarios
CREATE OR REPLACE VIEW user_activity AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.role,
    u.last_login,
    COUNT(DISTINCT s.id) as active_sessions,
    COUNT(DISTINCT al.id) as total_actions
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id AND s.is_active = TRUE
LEFT JOIN audit_logs al ON u.id = al.user_id
GROUP BY u.id, u.username, u.email, u.role, u.last_login;

-- =============================================
-- PERMISOS Y SEGURIDAD
-- =============================================

-- Comentarios en tablas
COMMENT ON TABLE users IS 'Usuarios del sistema con roles admin y client';
COMMENT ON TABLE sessions IS 'Sesiones activas de usuarios con tokens JWT';
COMMENT ON TABLE audit_logs IS 'Registro de auditoría de todas las acciones';

-- =============================================
-- FIN DEL SCRIPT
-- =============================================

-- Verificar la instalación
SELECT 'Base de datos inicializada correctamente' AS status;
SELECT COUNT(*) as total_users FROM users;