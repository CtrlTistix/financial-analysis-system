import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './ExportModal.css';

const ExportModal = ({ isOpen, onClose, financialData }) => {
  const { api, isAuthenticated } = useAuth();
  const [exportFormats, setExportFormats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState(null);

  useEffect(() => {
    if (isOpen && isAuthenticated) {
      fetchExportFormats();
    }
  }, [isOpen, isAuthenticated]);

  const fetchExportFormats = async () => {
    try {
      const response = await api.get('/export/formats');
      setExportFormats(response.data.formats);
    } catch (error) {
      console.error('Error fetching export formats:', error);
    }
  };

  const handleExport = async (format) => {
    if (!financialData) {
      alert('No hay datos para exportar. Por favor carga un archivo primero.');
      return;
    }

    setLoading(true);
    setSelectedFormat(format.id);

    try {
      const response = await api.get(format.endpoint, {
        responseType: 'blob'
      });

      // Obtener nombre del archivo desde Content-Disposition o usar uno por defecto
      const contentDisposition = response.headers['content-disposition'];
      let filename = `reporte_${format.id}_${new Date().toISOString().split('T')[0]}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      } else {
        // Determinar extensión según el formato
        const extension = format.id.includes('csv') ? '.csv' : 
                         format.id.includes('json') ? '.json' : '.xlsx';
        filename += extension;
      }

      // Crear y descargar el archivo
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      // Mostrar mensaje de éxito
      showNotification('success', `Reporte ${format.name} descargado exitosamente`);
      
    } catch (error) {
      console.error('Error exporting:', error);
      const errorMsg = error.response?.data?.detail || 'Error al exportar el archivo';
      showNotification('error', errorMsg);
    } finally {
      setLoading(false);
      setSelectedFormat(null);
    }
  };

  const showNotification = (type, message) => {
    // Puedes implementar un sistema de notificaciones más sofisticado
    if (type === 'success') {
      alert(`✅ ${message}`);
    } else {
      alert(`❌ ${message}`);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="export-modal-overlay" onClick={onClose}>
      <div className="export-modal" onClick={(e) => e.stopPropagation()}>
        <div className="export-modal-header">
          <h2>📤 Exportar Análisis Financiero</h2>
          <button className="close-button" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="export-modal-body">
          {!financialData ? (
            <div className="export-warning">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <p>No hay datos disponibles para exportar.</p>
              <p className="warning-subtitle">Por favor, carga un archivo Excel primero.</p>
            </div>
          ) : (
            <>
              <div className="export-info">
                <div className="info-item">
                  <span className="info-label">📁 Archivo:</span>
                  <span className="info-value">{financialData.filename || 'N/A'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">📅 Períodos:</span>
                  <span className="info-value">
                    {financialData.available_years?.join(', ') || 'N/A'}
                  </span>
                </div>
                <div className="info-item">
                  <span className="info-label">📊 Indicadores:</span>
                  <span className="info-value">
                    {Object.values(financialData.indicators || {}).reduce(
                      (sum, category) => sum + Object.keys(category).length, 0
                    )}
                  </span>
                </div>
              </div>

              <div className="export-formats">
                <h3>Selecciona el formato de exportación:</h3>
                <div className="formats-grid">
                  {exportFormats.map((format) => (
                    <div
                      key={format.id}
                      className={`format-card ${selectedFormat === format.id && loading ? 'loading' : ''}`}
                      onClick={() => !loading && handleExport(format)}
                    >
                      <div className="format-icon">{format.icon}</div>
                      <div className="format-details">
                        <h4>{format.name}</h4>
                        <p>{format.description}</p>
                      </div>
                      {selectedFormat === format.id && loading && (
                        <div className="format-loading">
                          <div className="spinner"></div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="export-tips">
                <h4>💡 Sugerencias:</h4>
                <ul>
                  <li><strong>Excel Completo:</strong> Ideal para presentaciones ejecutivas y reportes detallados</li>
                  <li><strong>Resumen Ejecutivo:</strong> Perfecto para reuniones de directorio</li>
                  <li><strong>CSV/JSON:</strong> Útil para análisis personalizado o integración con otros sistemas</li>
                </ul>
              </div>
            </>
          )}
        </div>

        <div className="export-modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportModal;