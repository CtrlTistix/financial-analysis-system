import React, { useState, useEffect } from 'react';
import { Settings, Save, RefreshCw, Database, FileSpreadsheet, MessageSquare, Shield, Bell } from 'lucide-react';

const ConfigurationPage = () => {
  const [config, setConfig] = useState({
    nombre_empresa: '',
    periodo_fiscal: '2020',
    moneda: 'USD',
    dias_anio: 360,
    metodo_depreciacion: 'lineal',
    fila_inicio: 2,
    permitir_filas_vacias: true,
    formato_numeros: 'europeo',
    incluir_graficos: true,
    formato_reporte: 'xlsx',
    incluir_interpretacion: true,
    notificaciones_email: true,
    email_admin: '',
    requiere_autenticacion: true,
    expiracion_sesion: 60,
    chat_habilitado: true,
    modelo_ia: 'gpt-4',
    contexto_corporativo: ''
  });

  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });

  const API_BASE = 'https://financial-analysis-system-qhnz.onrender.com';

  useEffect(() => {
    cargarConfiguracion();
  }, []);

  const cargarConfiguracion = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API_BASE}/api/configuracion/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      } else if (response.status === 401) {
        setMensaje({ tipo: 'error', texto: 'Sesión expirada. Por favor inicia sesión nuevamente.' });
      }
    } catch (error) {
      console.error('Error al cargar configuración:', error);
      setMensaje({ tipo: 'error', texto: 'Error al cargar la configuración' });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleGuardar = async () => {
    setSaving(true);
    setMensaje({ tipo: '', texto: '' });

    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API_BASE}/api/configuracion/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(config)
      });

      if (response.ok) {
        setMensaje({ tipo: 'success', texto: '✅ Configuración guardada exitosamente' });
        setTimeout(() => setMensaje({ tipo: '', texto: '' }), 3000);
      } else if (response.status === 403) {
        setMensaje({ tipo: 'error', texto: 'Solo los administradores pueden modificar la configuración' });
      } else if (response.status === 401) {
        setMensaje({ tipo: 'error', texto: 'Sesión expirada. Por favor inicia sesión nuevamente.' });
      } else {
        setMensaje({ tipo: 'error', texto: 'Error al guardar la configuración' });
      }
    } catch (error) {
      console.error('Error:', error);
      setMensaje({ tipo: 'error', texto: 'Error de conexión al guardar' });
    } finally {
      setSaving(false);
    }
  };

  const handleRestaurar = async () => {
    if (!window.confirm('¿Estás seguro de restaurar la configuración por defecto? Esta acción no se puede deshacer.')) {
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API_BASE}/api/configuracion/reset`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setConfig(data);
        setMensaje({ tipo: 'info', texto: '🔄 Configuración restaurada a valores por defecto' });
        setTimeout(() => setMensaje({ tipo: '', texto: '' }), 3000);
      } else if (response.status === 403) {
        setMensaje({ tipo: 'error', texto: 'Solo los administradores pueden restaurar la configuración' });
      }
    } catch (error) {
      console.error('Error:', error);
      setMensaje({ tipo: 'error', texto: 'Error al restaurar configuración' });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '50px', 
            height: '50px', 
            border: '4px solid #e2e8f0',
            borderTop: '4px solid #3182ce',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }}></div>
          <p>Cargando configuración...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f7fafc', padding: '1.5rem' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ 
          background: 'white', 
          borderRadius: '12px', 
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)', 
          padding: '1.5rem',
          marginBottom: '1.5rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <Settings size={32} color="#3182ce" />
              <div>
                <h1 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 700, color: '#1a202c' }}>
                  Configuración del Sistema
                </h1>
                <p style={{ margin: '0.25rem 0 0', color: '#718096' }}>
                  Personaliza el comportamiento de Financial Analysis
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <button
                onClick={handleRestaurar}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.75rem 1.25rem',
                  background: '#edf2f7',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 600,
                  color: '#4a5568',
                  transition: 'all 0.2s'
                }}
                onMouseOver={e => e.target.style.background = '#e2e8f0'}
                onMouseOut={e => e.target.style.background = '#edf2f7'}
              >
                <RefreshCw size={16} />
                Restaurar
              </button>
              <button
                onClick={handleGuardar}
                disabled={saving}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.75rem 1.25rem',
                  background: saving ? '#cbd5e0' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: saving ? 'not-allowed' : 'pointer',
                  fontWeight: 600,
                  color: 'white',
                  transition: 'all 0.2s'
                }}
              >
                <Save size={16} />
                {saving ? 'Guardando...' : 'Guardar Cambios'}
              </button>
            </div>
          </div>

          {/* Mensaje de estado */}
          {mensaje.texto && (
            <div style={{
              marginTop: '1rem',
              padding: '1rem',
              borderRadius: '8px',
              background: mensaje.tipo === 'success' ? '#c6f6d5' :
                         mensaje.tipo === 'error' ? '#fed7d7' : '#bee3f8',
              color: mensaje.tipo === 'success' ? '#2f855a' :
                     mensaje.tipo === 'error' ? '#c53030' : '#2c5282',
              border: `1px solid ${mensaje.tipo === 'success' ? '#9ae6b4' :
                                  mensaje.tipo === 'error' ? '#fc8181' : '#90cdf4'}`
            }}>
              {mensaje.texto}
            </div>
          )}
        </div>

        {/* Configuración General */}
        <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '1.5rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '2px solid #e2e8f0' }}>
            <Database size={24} color="#3182ce" />
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>Configuración General</h2>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#4a5568', marginBottom: '0.5rem' }}>
                Nombre de la Empresa
              </label>
              <input
                type="text"
                name="nombre_empresa"
                value={config.nombre_empresa}
                onChange={handleChange}
                style={{ width: '100%', padding: '0.75rem', border: '2px solid #e2e8f0', borderRadius: '8px', fontSize: '1rem' }}
                placeholder="Mi Empresa S.A."
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#4a5568', marginBottom: '0.5rem' }}>
                Periodo Fiscal
              </label>
              <input
                type="text"
                name="periodo_fiscal"
                value={config.periodo_fiscal}
                onChange={handleChange}
                style={{ width: '100%', padding: '0.75rem', border: '2px solid #e2e8f0', borderRadius: '8px', fontSize: '1rem' }}
                placeholder="2020"
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#4a5568', marginBottom: '0.5rem' }}>
                Moneda
              </label>
              <select
                name="moneda"
                value={config.moneda}
                onChange={handleChange}
                style={{ width: '100%', padding: '0.75rem', border: '2px solid #e2e8f0', borderRadius: '8px', fontSize: '1rem' }}
              >
                <option value="USD">USD - Dólar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="COP">COP - Peso Colombiano</option>
                <option value="MXN">MXN - Peso Mexicano</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#4a5568', marginBottom: '0.5rem' }}>
                Días del Año para Cálculos
              </label>
              <select
                name="dias_anio"
                value={config.dias_anio}
                onChange={handleChange}
                style={{ width: '100%', padding: '0.75rem', border: '2px solid #e2e8f0', borderRadius: '8px', fontSize: '1rem' }}
              >
                <option value={360}>360 días (Comercial)</option>
                <option value={365}>365 días (Real)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Configuración de Excel */}
        <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '1.5rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '2px solid #e2e8f0' }}>
            <FileSpreadsheet size={24} color="#48bb78" />
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>Configuración de Archivos Excel</h2>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#4a5568', marginBottom: '0.5rem' }}>
                Fila de Inicio de Datos
              </label>
              <input
                type="number"
                name="fila_inicio"
                value={config.fila_inicio}
                onChange={handleChange}
                style={{ width: '100%', padding: '0.75rem', border: '2px solid #e2e8f0', borderRadius: '8px', fontSize: '1rem' }}
                min="1"
              />
              <p style={{ fontSize: '0.75rem', color: '#718096', marginTop: '0.25rem' }}>Primera fila donde comienzan los datos</p>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#4a5568', marginBottom: '0.5rem' }}>
                Formato de Números
              </label>
              <select
                name="formato_numeros"
                value={config.formato_numeros}
                onChange={handleChange}
                style={{ width: '100%', padding: '0.75rem', border: '2px solid #e2e8f0', borderRadius: '8px', fontSize: '1rem' }}
              >
                <option value="europeo">Europeo (1.234,56)</option>
                <option value="americano">Americano (1,234.56)</option>
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                name="permitir_filas_vacias"
                checked={config.permitir_filas_vacias}
                onChange={handleChange}
                style={{ width: '18px', height: '18px' }}
              />
              <label style={{ fontSize: '0.875rem', color: '#4a5568' }}>
                Permitir filas vacías entre datos
              </label>
            </div>
          </div>
        </div>

        {/* Configuración del Chat AI */}
        <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '1.5rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '2px solid #e2e8f0' }}>
            <MessageSquare size={24} color="#805ad5" />
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>Configuración del Chat AI</h2>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                name="chat_habilitado"
                checked={config.chat_habilitado}
                onChange={handleChange}
                style={{ width: '18px', height: '18px' }}
              />
              <label style={{ fontSize: '0.875rem', color: '#4a5568' }}>
                Habilitar asistente de chat con IA
              </label>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#4a5568', marginBottom: '0.5rem' }}>
                Contexto Corporativo (opcional)
              </label>
              <textarea
                name="contexto_corporativo"
                value={config.contexto_corporativo}
                onChange={handleChange}
                rows="4"
                style={{ width: '100%', padding: '0.75rem', border: '2px solid #e2e8f0', borderRadius: '8px', fontSize: '1rem', fontFamily: 'inherit' }}
                placeholder="Información adicional sobre tu empresa que el asistente debe conocer..."
              />
              <p style={{ fontSize: '0.75rem', color: '#718096', marginTop: '0.25rem' }}>
                Este contexto ayudará al asistente a dar respuestas más personalizadas
              </p>
            </div>
          </div>
        </div>

        {/* Configuración de Seguridad */}
        <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '1.5rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '2px solid #e2e8f0' }}>
            <Shield size={24} color="#e53e3e" />
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>Configuración de Seguridad</h2>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                name="requiere_autenticacion"
                checked={config.requiere_autenticacion}
                onChange={handleChange}
                style={{ width: '18px', height: '18px' }}
              />
              <label style={{ fontSize: '0.875rem', color: '#4a5568' }}>
                Requerir autenticación para funciones avanzadas
              </label>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#4a5568', marginBottom: '0.5rem' }}>
                Tiempo de Expiración de Sesión (minutos)
              </label>
              <input
                type="number"
                name="expiracion_sesion"
                value={config.expiracion_sesion}
                onChange={handleChange}
                style={{ width: '100%', maxWidth: '300px', padding: '0.75rem', border: '2px solid #e2e8f0', borderRadius: '8px', fontSize: '1rem' }}
                min="15"
                max="480"
              />
            </div>
          </div>
        </div>

        {/* Configuración de Notificaciones */}
        <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '2px solid #e2e8f0' }}>
            <Bell size={24} color="#ecc94b" />
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>Notificaciones</h2>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                name="notificaciones_email"
                checked={config.notificaciones_email}
                onChange={handleChange}
                style={{ width: '18px', height: '18px' }}
              />
              <label style={{ fontSize: '0.875rem', color: '#4a5568' }}>
                Enviar notificaciones por correo electrónico
              </label>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#4a5568', marginBottom: '0.5rem' }}>
                Email del Administrador
              </label>
              <input
                type="email"
                name="email_admin"
                value={config.email_admin}
                onChange={handleChange}
                style={{ width: '100%', maxWidth: '400px', padding: '0.75rem', border: '2px solid #e2e8f0', borderRadius: '8px', fontSize: '1rem' }}
                placeholder="admin@empresa.com"
              />
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ConfigurationPage;