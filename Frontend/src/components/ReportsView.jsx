import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './ReportsView.css';

const ReportsView = ({ financialData }) => {
  const { api, isAuthenticated } = useAuth();
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      fetchAvailableReports();
    }
  }, [isAuthenticated]);

  const fetchAvailableReports = async () => {
    try {
      const response = await api.get('/reports/available');
      setReports(response.data.reports);
      if (response.data.reports.length > 0) {
        setSelectedReport(response.data.reports[0]);
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
    }
  };

  const handleDownloadReport = async (report) => {
    if (!financialData) {
      alert('No hay datos para generar reportes. Por favor carga un archivo primero.');
      return;
    }

    setDownloading(true);

    try {
      const response = await api.get(report.endpoint, {
        responseType: 'blob'
      });

      const contentDisposition = response.headers['content-disposition'];
      let filename = `reporte_${report.id}_${new Date().toISOString().split('T')[0]}.xlsx`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      alert(`✅ ${report.name} descargado exitosamente`);
      
    } catch (error) {
      console.error('Error downloading report:', error);
      const errorMsg = error.response?.data?.detail || 'Error al descargar el reporte';
      alert(`❌ ${errorMsg}`);
    } finally {
      setDownloading(false);
    }
  };

  if (!financialData) {
    return (
      <div className="reports-view">
        <div className="reports-empty-state">
          <div className="empty-icon">📊</div>
          <h2>No hay datos disponibles</h2>
          <p>Para generar reportes, primero debes cargar un archivo Excel con tus estados financieros.</p>
          <div className="empty-steps">
            <div className="step">
              <span className="step-number">1</span>
              <span>Haz clic en "Cargar Excel"</span>
            </div>
            <div className="step">
              <span className="step-number">2</span>
              <span>Selecciona tu archivo de estados financieros</span>
            </div>
            <div className="step">
              <span className="step-number">3</span>
              <span>Los reportes se generarán automáticamente</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="reports-view">
      {/* Header */}
      <div className="reports-header">
        <div className="header-content">
          <h2>📊 Centro de Reportes</h2>
          <p>Análisis especializados listos para descargar</p>
        </div>
        <div className="header-stats">
          <div className="stat-card">
            <span className="stat-label">Archivo</span>
            <span className="stat-value">{financialData.filename || 'N/A'}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Períodos</span>
            <span className="stat-value">{financialData.available_years?.join(', ') || 'N/A'}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Reportes</span>
            <span className="stat-value">{reports.length}</span>
          </div>
        </div>
      </div>

      <div className="reports-container">
        {/* Sidebar de Reportes */}
        <div className="reports-sidebar">
          <div className="sidebar-header">
            <h3>Tipos de Reportes</h3>
          </div>
          <div className="reports-list">
            {reports.map((report) => (
              <div
                key={report.id}
                className={`report-item ${selectedReport?.id === report.id ? 'active' : ''}`}
                onClick={() => setSelectedReport(report)}
              >
                <div className="report-item-icon" style={{ background: `${report.color}15`, color: report.color }}>
                  {report.icon}
                </div>
                <div className="report-item-info">
                  <h4>{report.name}</h4>
                  <p>{report.description}</p>
                </div>
                <div className="report-item-arrow">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Contenido del Reporte Seleccionado */}
        <div className="reports-content">
          {selectedReport && (
            <>
              <div className="report-detail-header" style={{ borderLeft: `4px solid ${selectedReport.color}` }}>
                <div className="detail-icon" style={{ background: `${selectedReport.color}15`, color: selectedReport.color }}>
                  {selectedReport.icon}
                </div>
                <div className="detail-info">
                  <h2>{selectedReport.name}</h2>
                  <p>{selectedReport.description}</p>
                </div>
              </div>

              <div className="report-sections-info">
                <h3>📋 Contenido del Reporte</h3>
                <div className="sections-grid">
                  {selectedReport.sections?.map((section, index) => (
                    <div key={index} className="section-badge">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      <span>{section}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="report-features">
                <h3>✨ Características</h3>
                <div className="features-grid">
                  <div className="feature-card">
                    <div className="feature-icon">📊</div>
                    <div className="feature-content">
                      <h4>Formato Profesional</h4>
                      <p>Excel con estilos, colores y formato listo para presentar</p>
                    </div>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">📈</div>
                    <div className="feature-content">
                      <h4>Análisis Detallado</h4>
                      <p>Indicadores calculados con interpretaciones y recomendaciones</p>
                    </div>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">🎯</div>
                    <div className="feature-content">
                      <h4>Datos Precisos</h4>
                      <p>Basado en tus estados financieros cargados</p>
                    </div>
                  </div>
                  <div className="feature-card">
                    <div className="feature-icon">⚡</div>
                    <div className="feature-content">
                      <h4>Generación Rápida</h4>
                      <p>Descarga inmediata en formato Excel (.xlsx)</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Casos de Uso */}
              <div className="report-use-cases">
                <h3>💡 ¿Cuándo usar este reporte?</h3>
                <div className="use-cases-list">
                  {getUseCases(selectedReport.id).map((useCase, index) => (
                    <div key={index} className="use-case-item">
                      <div className="use-case-icon">{useCase.icon}</div>
                      <div className="use-case-content">
                        <h4>{useCase.title}</h4>
                        <p>{useCase.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Botón de Descarga */}
              <div className="report-action">
                <button
                  className="download-report-btn"
                  style={{ background: selectedReport.color }}
                  onClick={() => handleDownloadReport(selectedReport)}
                  disabled={downloading}
                >
                  {downloading ? (
                    <>
                      <div className="btn-spinner"></div>
                      <span>Generando reporte...</span>
                    </>
                  ) : (
                    <>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                      </svg>
                      <span>Descargar Reporte</span>
                    </>
                  )}
                </button>
                <p className="download-note">
                  El reporte se descargará en formato Excel (.xlsx) y estará listo para usar
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// Función auxiliar para casos de uso
const getUseCases = (reportId) => {
  const useCases = {
    liquidez: [
      {
        icon: '👔',
        title: 'Reuniones con Bancos',
        description: 'Demuestra tu capacidad de pago para solicitar créditos o líneas de financiamiento'
      },
      {
        icon: '📊',
        title: 'Análisis Interno',
        description: 'Monitorea tu salud financiera y detecta problemas de liquidez a tiempo'
      },
      {
        icon: '🎯',
        title: 'Toma de Decisiones',
        description: 'Identifica si puedes realizar inversiones o si necesitas mejorar el flujo de caja'
      }
    ],
    rentabilidad: [
      {
        icon: '💼',
        title: 'Presentaciones a Inversionistas',
        description: 'Muestra el retorno sobre inversión y atractivo de tu empresa'
      },
      {
        icon: '📈',
        title: 'Evaluación de Desempeño',
        description: 'Compara la rentabilidad entre períodos y contra objetivos'
      },
      {
        icon: '🔍',
        title: 'Identificación de Áreas',
        description: 'Detecta qué áreas generan más valor y cuáles necesitan mejora'
      }
    ],
    endeudamiento: [
      {
        icon: '🏦',
        title: 'Reestructuración de Deuda',
        description: 'Analiza tu estructura financiera para negociar mejores términos'
      },
      {
        icon: '⚖️',
        title: 'Evaluación de Riesgo',
        description: 'Determina si tu nivel de endeudamiento es sostenible'
      },
      {
        icon: '📉',
        title: 'Plan de Reducción',
        description: 'Establece estrategias para disminuir el apalancamiento'
      }
    ],
    eficiencia: [
      {
        icon: '⚡',
        title: 'Optimización Operativa',
        description: 'Mejora la gestión de inventarios y cobros'
      },
      {
        icon: '📦',
        title: 'Gestión de Inventarios',
        description: 'Reduce costos de almacenamiento y obsolescencia'
      },
      {
        icon: '💳',
        title: 'Políticas de Cobro',
        description: 'Acelera la recuperación de cartera'
      }
    ],
    riesgo: [
      {
        icon: '🚨',
        title: 'Alertas Tempranas',
        description: 'Detecta señales de problemas financieros antes de que sean críticos'
      },
      {
        icon: '🛡️',
        title: 'Due Diligence',
        description: 'Evalúa la viabilidad financiera en fusiones o adquisiciones'
      },
      {
        icon: '📋',
        title: 'Cumplimiento',
        description: 'Demuestra solvencia a reguladores o auditores'
      }
    ],
    ejecutivo: [
      {
        icon: '👥',
        title: 'Juntas Directivas',
        description: 'Presenta KPIs clave de forma clara y concisa'
      },
      {
        icon: '📊',
        title: 'Reportes Gerenciales',
        description: 'Comunicación rápida del estado financiero a la alta dirección'
      },
      {
        icon: '🎯',
        title: 'Seguimiento Estratégico',
        description: 'Monitorea el cumplimiento de objetivos corporativos'
      }
    ],
    completo: [
      {
        icon: '📚',
        title: 'Auditorías',
        description: 'Documentación completa para procesos de auditoría interna o externa'
      },
      {
        icon: '🎓',
        title: 'Análisis Académico',
        description: 'Material de estudio o casos de análisis financiero'
      },
      {
        icon: '📑',
        title: 'Archivo Histórico',
        description: 'Mantén un registro completo del análisis financiero por período'
      }
    ],
    comparativo: [
      {
        icon: '🏆',
        title: 'Benchmarking',
        description: 'Compara tu desempeño contra competidores del sector'
      },
      {
        icon: '📊',
        title: 'Posicionamiento',
        description: 'Identifica ventajas competitivas y áreas de mejora'
      },
      {
        icon: '🎯',
        title: 'Fijación de Metas',
        description: 'Establece objetivos realistas basados en estándares de la industria'
      }
    ]
  };

  return useCases[reportId] || [
    {
      icon: '📊',
      title: 'Análisis General',
      description: 'Útil para cualquier análisis financiero profesional'
    }
  ];
};

export default ReportsView;