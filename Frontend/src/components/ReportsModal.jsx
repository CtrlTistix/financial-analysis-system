import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './ReportsModal.css';

const ReportsModal = ({ isOpen, onClose, financialData }) => {
  const { api, isAuthenticated } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    if (isOpen && isAuthenticated) {
      fetchAvailableReports();
    }
  }, [isOpen, isAuthenticated]);

  const fetchAvailableReports = async () => {
    try {
      const response = await api.get('/reports/available');
      setReports(response.data.reports);
    } catch (error) {
      console.error('Error fetching reports:', error);
    }
  };

  const handleDownloadReport = async (report) => {
    if (!financialData) {
      alert('No hay datos para generar reportes. Por favor carga un archivo primero.');
      return;
    }

    setLoading(true);
    setSelectedReport(report.id);

    try {
      const response = await api.get(report.endpoint, {
        responseType: 'blob'
      });

      // Obtener nombre del archivo
      const contentDisposition = response.headers['content-disposition'];
      let filename = `reporte_${report.id}_${new Date().toISOString().split('T')[0]}.xlsx`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
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

      showNotification('success', `${report.name} descargado exitosamente`);
      
    } catch (error) {
      console.error('Error downloading report:', error);
      const errorMsg = error.response?.data?.detail || 'Error al descargar el reporte';
      showNotification('error', errorMsg);
    } finally {
      setLoading(false);
      setSelectedReport(null);
    }
  };

  const showNotification = (type, message) => {
    if (type === 'success') {
      alert(`✅ ${message}`);
    } else {
      alert(`❌ ${message}`);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="reports-modal-overlay" onClick={onClose}>
      <div className="reports-modal" onClick={(e) => e.stopPropagation()}>
        <div className="reports-modal-header">
          <h2>📊 Reportes Especializados</h2>
          <button className="close-button" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="reports-modal-body">
          {!financialData ? (
            <div className="reports-warning">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <p>No hay datos disponibles para generar reportes.</p>
              <p className="warning-subtitle">Por favor, carga un archivo Excel primero.</p>
            </div>
          ) : (
            <>
              <div className="reports-info">
                <div className="info-banner">
                  <div className="banner-icon">📋</div>
                  <div className="banner-content">
                    <h3>Reportes Profesionales</h3>
                    <p>Análisis detallados en formato Excel listos para presentar</p>
                  </div>
                </div>
                <div className="info-stats">
                  <div className="stat-item">
                    <span className="stat-icon">📁</span>
                    <div>
                      <span className="stat-label">Archivo</span>
                      <span className="stat-value">{financialData.filename || 'N/A'}</span>
                    </div>
                  </div>
                  <div className="stat-item">
                    <span className="stat-icon">📅</span>
                    <div>
                      <span className="stat-label">Períodos</span>
                      <span className="stat-value">
                        {financialData.available_years?.length || 0} años
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="reports-grid">
                {reports.map((report) => (
                  <div
                    key={report.id}
                    className={`report-card ${selectedReport === report.id && loading ? 'loading' : ''}`}
                    style={{ borderLeft: `4px solid ${report.color}` }}
                    onClick={() => !loading && handleDownloadReport(report)}
                  >
                    <div className="report-header">
                      <div className="report-icon" style={{ background: `${report.color}15` }}>
                        {report.icon}
                      </div>
                      <h4>{report.name}</h4>
                    </div>
                    
                    <p className="report-description">{report.description}</p>
                    
                    {report.sections && (
                      <div className="report-sections">
                        <span className="sections-label">Incluye:</span>
                        <ul>
                          {report.sections.slice(0, 3).map((section, index) => (
                            <li key={index}>{section}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="report-footer">
                      <button 
                        className="download-btn"
                        style={{ background: report.color }}
                      >
                        {selectedReport === report.id && loading ? (
                          <>
                            <div className="btn-spinner"></div>
                            <span>Generando...</span>
                          </>
                        ) : (
                          <>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                              <polyline points="7 10 12 15 17 10"></polyline>
                              <line x1="12" y1="15" x2="12" y2="3"></line>
                            </svg>
                            <span>Descargar</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="reports-help">
                <h4>💡 Guía de Reportes</h4>
                <div className="help-grid">
                  <div className="help-item">
                    <strong>Para reuniones ejecutivas:</strong>
                    <p>Usa el Reporte Ejecutivo o Resumen Ejecutivo</p>
                  </div>
                  <div className="help-item">
                    <strong>Para análisis detallado:</strong>
                    <p>Descarga reportes específicos por área (Liquidez, Rentabilidad, etc.)</p>
                  </div>
                  <div className="help-item">
                    <strong>Para presentaciones completas:</strong>
                    <p>Utiliza el Reporte Completo con todas las secciones</p>
                  </div>
                  <div className="help-item">
                    <strong>Para comparaciones:</strong>
                    <p>El Comparativo Sectorial te ayuda con benchmarking</p>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="reports-modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReportsModal;