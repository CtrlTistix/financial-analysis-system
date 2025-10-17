import React, { useState, useEffect } from 'react';
import FinancialChart from './components/FinancialChart';
import AdditionalCharts from './components/AdditionalCharts';
import AnalysisView from './components/AnalysisView';
import Requirements from './components/Requirements';
import ChatWindow from './components/ChatWindow';
import './App.css';

const API_BASE = 'https://financial-analysis-system-qhnz.onrender.com';

// Iconos SVG
const Icons = {
  Menu: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="3" y1="12" x2="21" y2="12"></line>
      <line x1="3" y1="6" x2="21" y2="6"></line>
      <line x1="3" y1="18" x2="21" y2="18"></line>
    </svg>
  ),
  Dashboard: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="7" height="7"></rect>
      <rect x="14" y="3" width="7" height="7"></rect>
      <rect x="14" y="14" width="7" height="7"></rect>
      <rect x="3" y="14" width="7" height="7"></rect>
    </svg>
  ),
  Chart: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="12" y1="20" x2="12" y2="10"></line>
      <line x1="18" y1="20" x2="18" y2="4"></line>
      <line x1="6" y1="20" x2="6" y2="16"></line>
    </svg>
  ),
  Analysis: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
    </svg>
  ),
  Report: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
      <line x1="16" y1="13" x2="8" y2="13"></line>
      <line x1="16" y1="17" x2="8" y2="17"></line>
      <polyline points="10 9 9 9 8 9"></polyline>
    </svg>
  ),
  Settings: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="3"></circle>
      <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"></path>
    </svg>
  ),
  Upload: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
      <polyline points="17 8 12 3 7 8"></polyline>
      <line x1="12" y1="3" x2="12" y2="15"></line>
    </svg>
  ),
  Chat: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
  ),
  Send: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
    </svg>
  ),
  Close: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="18" y1="6" x2="6" y2="18"></line>
      <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
  ),
  Minimize: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="5" y1="12" x2="19" y2="12"></line>
    </svg>
  ),
  Maximize: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
    </svg>
  ),
  File: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
      <polyline points="13 2 13 9 20 9"></polyline>
    </svg>
  ),
};

function App() {
  const [financialData, setFinancialData] = useState(null);
  const [selectedYear, setSelectedYear] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMode, setChatMode] = useState('fixed'); // 'fixed' o 'floating'
  const [chatMinimized, setChatMinimized] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { type: 'bot', text: 'Bienvenido al Sistema de Análisis Financiero. Estoy aquí para ayudarte a interpretar tus indicadores financieros.' }
  ]);
  const [userInput, setUserInput] = useState('');

  useEffect(() => {
    fetchTestData();
    
    // Detectar tamaño de pantalla
    const handleResize = () => {
      if (window.innerWidth < 992) {
        setSidebarCollapsed(false);
        setSidebarOpen(false);
        setChatMode('floating');
      } else {
        setChatMode('fixed');
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const fetchTestData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/test-data`);
      if (!response.ok) throw new Error('Error cargando datos');
      const result = await response.json();
      setFinancialData(result);
      setSelectedYear(result.available_years[0]?.toString() || '');
    } catch (err) {
      setError('Error cargando datos de prueba');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setLoading(true);
      setError('');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}`);
      }

      const result = await response.json();
      setFinancialData(result);
      setSelectedYear(result.available_years[0]?.toString() || '');
      addChatMessage('bot', `Archivo ${file.name} procesado exitosamente. Se encontraron ${result.available_years.length} años de datos.`);
      
    } catch (err) {
      console.error('Error completo:', err);
      setError(`Error procesando archivo: ${err.message}`);
      addChatMessage('bot', `Error al procesar el archivo: ${err.message}`);
    } finally {
      setLoading(false);
      event.target.value = '';
    }
  };

  const addChatMessage = (type, text) => {
    setChatMessages(prev => [...prev, { type, text }]);
  };

  const handleSendMessage = async () => {
    if (!userInput.trim()) return;
    
    addChatMessage('user', userInput);
    const currentInput = userInput;
    setUserInput('');
    
    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentInput,
          financial_data: financialData
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error en la respuesta del servidor');
      }

      const data = await response.json();
      addChatMessage('bot', data.response);
      
    } catch (error) {
      console.error('Error:', error);
      addChatMessage('bot', 'Lo siento, hubo un error al procesar tu mensaje.');
    }
  };

  const formatIndicatorValue = (indicatorName, value) => {
    if (value === undefined || value === null || value === '') {
      return 'No disponible';
    }
    
    if (typeof value === 'string') return value;
    
    const numValue = typeof value === 'number' ? value : parseFloat(value);
    if (isNaN(numValue)) return 'No disponible';
    
    switch (indicatorName) {
      case 'razon_corriente':
      case 'prueba_acida':
      case 'endeudamiento_total':
      case 'deuda_patrimonio':
      case 'cobertura_intereses':
      case 'rotacion_inventarios':
      case 'rotacion_cartera':
      case 'rotacion_activos':
      case 'z_score':
        return numValue.toFixed(2);
        
      case 'capital_trabajo':
        return `$${Math.abs(numValue).toLocaleString('es-CO', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        })}`;
        
      case 'roe':
      case 'roa':
      case 'margen_bruto':
      case 'margen_neto':
        return `${(numValue * 100).toFixed(2)}%`;
        
      case 'dias_inventario':
      case 'dias_cartera':
        return `${Math.round(numValue)} días`;
        
      case 'clasificacion_liquidez':
      case 'clasificacion_riesgo':
      case 'clasificacion_z':
      case 'probabilidad_quiebra':
        return value;
        
      default:
        return numValue.toFixed(2);
    }
  };

  const getIndicatorLabel = (key) => {
    const labels = {
      'razon_corriente': 'Razón Corriente',
      'prueba_acida': 'Prueba Ácida',
      'capital_trabajo': 'Capital de Trabajo',
      'clasificacion_liquidez': 'Clasificación',
      'roe': 'Return on Equity (ROE)',
      'roa': 'Return on Assets (ROA)',
      'margen_bruto': 'Margen Bruto',
      'margen_neto': 'Margen Neto',
      'endeudamiento_total': 'Endeudamiento Total',
      'deuda_patrimonio': 'Deuda/Patrimonio',
      'cobertura_intereses': 'Cobertura de Intereses',
      'clasificacion_riesgo': 'Clasificación de Riesgo',
      'rotacion_inventarios': 'Rotación de Inventarios',
      'rotacion_cartera': 'Rotación de Cartera',
      'rotacion_activos': 'Rotación de Activos',
      'dias_inventario': 'Días de Inventario',
      'dias_cartera': 'Días de Cartera',
      'z_score': 'Z-Score Altman',
      'clasificacion_z': 'Clasificación Z-Score',
      'probabilidad_quiebra': 'Probabilidad de Quiebra'
    };
    return labels[key] || key;
  };

  const getIndicatorDescription = (key) => {
    const descriptions = {
      'razon_corriente': 'Capacidad de pagar obligaciones a corto plazo',
      'prueba_acida': 'Liquidez inmediata sin considerar inventarios',
      'capital_trabajo': 'Recursos disponibles para operaciones',
      'clasificacion_liquidez': 'Estado general de liquidez',
      'roe': 'Rentabilidad sobre el capital de los accionistas',
      'roa': 'Eficiencia en el uso de los activos',
      'margen_bruto': 'Porcentaje de utilidad sobre ventas',
      'margen_neto': 'Utilidad neta como porcentaje de ventas',
      'endeudamiento_total': 'Proporción de activos financiados con deuda',
      'deuda_patrimonio': 'Relación entre deuda y capital propio',
      'cobertura_intereses': 'Capacidad de cubrir gastos financieros',
      'clasificacion_riesgo': 'Nivel de riesgo crediticio',
      'rotacion_inventarios': 'Veces que se vende el inventario al año',
      'rotacion_cartera': 'Eficiencia en cobro de cuentas',
      'rotacion_activos': 'Eficiencia en el uso de activos totales',
      'dias_inventario': 'Tiempo promedio de permanencia del inventario',
      'dias_cartera': 'Tiempo promedio de cobro',
      'z_score': 'Indicador de salud financiera y riesgo de quiebra',
      'clasificacion_z': 'Zona de riesgo según Z-Score',
      'probabilidad_quiebra': 'Riesgo de insolvencia'
    };
    return descriptions[key] || 'Indicador financiero clave';
  };

  const getCategoryTitle = (category) => {
    const titles = {
      'liquidez': 'Indicadores de Liquidez',
      'rentabilidad': 'Indicadores de Rentabilidad',
      'endeudamiento': 'Indicadores de Endeudamiento',
      'rotacion': 'Indicadores de Rotación',
      'quiebra': 'Análisis de Quiebra'
    };
    return titles[category] || category;
  };

  const getCategoryTag = (category) => {
    const tags = {
      'liquidez': 'Liquidez',
      'rentabilidad': 'Rentabilidad',
      'endeudamiento': 'Deuda',
      'rotacion': 'Rotación',
      'quiebra': 'Riesgo'
    };
    return tags[category] || category;
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'liquidez': '💧',
      'rentabilidad': '💰',
      'endeudamiento': '📊',
      'rotacion': '🔄',
      'quiebra': '⚠️'
    };
    return icons[category] || '📈';
  };

  const toggleSidebar = () => {
    if (window.innerWidth < 992) {
      setSidebarOpen(!sidebarOpen);
    } else {
      setSidebarCollapsed(!sidebarCollapsed);
    }
  };

  const handleNavClick = (view) => {
    setCurrentView(view);
    if (window.innerWidth < 992) {
      setSidebarOpen(false);
    }
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2>Procesando análisis financiero</h2>
          <p>Calculando indicadores y preparando visualizaciones</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <button 
              className={`menu-toggle ${sidebarOpen ? 'active' : ''}`}
              onClick={toggleSidebar}
            >
              <span></span>
              <span></span>
              <span></span>
            </button>
            
            <div className="header-brand">
              <div className="brand-icon">FA</div>
              <div className="header-title">
                <h1>Financial Analysis</h1>
                <p>Sistema de Análisis Financiero</p>
              </div>
            </div>
          </div>

          <div className="header-actions">
            <input
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileUpload}
              disabled={loading}
              className="file-input"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="upload-btn">
              <Icons.Upload />
              <span>Cargar Excel</span>
            </label>
            
            <button 
              className={`chat-toggle-btn ${chatOpen ? 'active' : ''}`}
              onClick={() => setChatOpen(!chatOpen)}
              title="Abrir chat"
            >
              <Icons.Chat />
            </button>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="app-layout">
        {/* Sidebar */}
        <aside className={`sidebar ${sidebarOpen ? 'open' : ''} ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <nav className="sidebar-nav">
            <div className="nav-section">
              <h3>Análisis</h3>
              <ul>
                <li>
                  <div
                    className={`nav-item ${currentView === 'dashboard' ? 'active' : ''}`}
                    onClick={() => handleNavClick('dashboard')}
                    data-tooltip="Dashboard Principal"
                  >
                    <span className="nav-icon"><Icons.Dashboard /></span>
                    <span className="nav-text">Dashboard Principal</span>
                  </div>
                </li>
                <li>
                  <div
                    className={`nav-item ${currentView === 'charts' ? 'active' : ''}`}
                    onClick={() => handleNavClick('charts')}
                    data-tooltip="Gráficas Detalladas"
                  >
                    <span className="nav-icon"><Icons.Chart /></span>
                    <span className="nav-text">Gráficas Detalladas</span>
                  </div>
                </li>
                <li>
                  <div
                    className={`nav-item ${currentView === 'horizontal' ? 'active' : ''}`}
                    onClick={() => handleNavClick('horizontal')}
                    data-tooltip="Análisis H/V"
                  >
                    <span className="nav-icon"><Icons.Analysis /></span>
                    <span className="nav-text">Análisis Horizontal/Vertical</span>
                  </div>
                </li>
              </ul>
            </div>
            
            <div className="nav-section">
              <h3>Reportes</h3>
              <ul>
                <li>
                  <div className="nav-item" data-tooltip="Reporte Liquidez">
                    <span className="nav-icon"><Icons.Report /></span>
                    <span className="nav-text">Reporte de Liquidez</span>
                  </div>
                </li>
                <li>
                  <div className="nav-item" data-tooltip="Reporte Rentabilidad">
                    <span className="nav-icon"><Icons.Report /></span>
                    <span className="nav-text">Reporte de Rentabilidad</span>
                  </div>
                </li>
                <li>
                  <div className="nav-item" data-tooltip="Reporte Completo">
                    <span className="nav-icon"><Icons.Report /></span>
                    <span className="nav-text">Reporte Completo</span>
                  </div>
                </li>
              </ul>
            </div>
            
            <div className="nav-section">
              <h3>Sistema</h3>
              <ul>
                <li>
                  <div
                    className={`nav-item ${currentView === 'requirements' ? 'active' : ''}`}
                    onClick={() => handleNavClick('requirements')}
                    data-tooltip="Requerimientos"
                  >
                    <span className="nav-icon"><Icons.File /></span>
                    <span className="nav-text">Requerimientos</span>
                  </div>
                </li>
                <li>
                  <div className="nav-item" data-tooltip="Configuración">
                    <span className="nav-icon"><Icons.Settings /></span>
                    <span className="nav-text">Configuración</span>
                  </div>
                </li>
              </ul>
            </div>
          </nav>
        </aside>

        {/* Overlay para móvil */}
        {sidebarOpen && window.innerWidth < 992 && (
          <div 
            className="sidebar-overlay active"
            onClick={() => setSidebarOpen(false)}
          ></div>
        )}

        {/* Main Content */}
        <main className={`main-content ${chatOpen && chatMode === 'fixed' ? 'with-chat' : ''}`}>
          {currentView === 'requirements' ? (
            <Requirements />
          ) : currentView === 'horizontal' ? (
            <AnalysisView data={financialData} />
          ) : currentView === 'charts' ? (
            <>
              <section className="dashboard-header">
                <div className="dashboard-title">
                  <h2>Gráficas Detalladas</h2>
                  <p>Visualizaciones completas de todos los indicadores</p>
                </div>
              </section>

              <section className="charts-section">
                <div className="charts-grid">
                  <div className="chart-card">
                    <div className="chart-header">
                      <h4>Evolución de Liquidez</h4>
                      <p>Razón Corriente y Prueba Ácida</p>
                    </div>
                    <FinancialChart 
                      data={financialData} 
                      type="liquidity" 
                      title="Indicadores de Liquidez"
                    />
                  </div>

                  <div className="chart-card">
                    <div className="chart-header">
                      <h4>Rentabilidad Histórica</h4>
                      <p>ROE, ROA y Márgenes</p>
                    </div>
                    <FinancialChart 
                      data={financialData} 
                      type="profitability" 
                      title="Indicadores de Rentabilidad"
                    />
                  </div>

                  <div className="chart-card">
                    <div className="chart-header">
                      <h4>Estructura de Deuda</h4>
                      <p>Endeudamiento y Cobertura</p>
                    </div>
                    <AdditionalCharts 
                      data={financialData} 
                      type="debt"
                    />
                  </div>

                  <div className="chart-card">
                    <div className="chart-header">
                      <h4>Indicadores de Rotación</h4>
                      <p>Eficiencia Operativa</p>
                    </div>
                    <AdditionalCharts 
                      data={financialData} 
                      type="rotation"
                    />
                  </div>

                  <div className="chart-card">
                    <div className="chart-header">
                      <h4>Ciclo Operativo</h4>
                      <p>Días de Inventario y Cartera</p>
                    </div>
                    <AdditionalCharts 
                      data={financialData} 
                      type="efficiency"
                    />
                  </div>

                  <div className="chart-card">
                    <div className="chart-header">
                      <h4>Análisis de Riesgo</h4>
                      <p>Z-Score de Altman</p>
                    </div>
                    <FinancialChart 
                      data={financialData} 
                      type="zscore"
                      title="Z-Score"
                    />
                  </div>
                </div>
              </section>
            </>
          ) : (
            <>
              {error && (
                <div className="error-alert">
                  <div className="alert-content">
                    <strong>Error:</strong> {error}
                  </div>
                </div>
              )}

              <section className="dashboard-header">
                <div className="dashboard-title">
                  <h2>Dashboard de Análisis</h2>
                  <p>Indicadores financieros y métricas clave</p>
                </div>
                <div className="dashboard-controls">
                  <div className="year-filter">
                    <label>Periodo:</label>
                    <select 
                      value={selectedYear} 
                      onChange={(e) => setSelectedYear(e.target.value)}
                      className="filter-select"
                    >
                      {financialData?.available_years.map(year => (
                        <option key={year} value={year.toString()}>
                          {year}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </section>

              {financialData && (
                <section className="indicators-section">
                  <div className="section-header">
                    <h3>Indicadores Financieros</h3>
                    <p>Resultados para el año {selectedYear}</p>
                  </div>
                  
                  <div className="indicators-grid">
                    {Object.entries(financialData.indicators).map(([category, indicators]) => (
                      <div key={category} className="indicator-category">
                        <h4 className="category-title">
                          <span className="category-icon">{getCategoryIcon(category)}</span>
                          {getCategoryTitle(category)}
                        </h4>
                        <div className="category-cards">
                          {Object.entries(indicators).map(([key, values]) => {
                            const currentValue = values[selectedYear];
                            
                            return (
                              <div key={key} className="indicator-card">
                                <div className="card-header">
                                  <h5>{getIndicatorLabel(key)}</h5>
                                  <span className="indicator-tag">{getCategoryTag(category)}</span>
                                </div>
                                <div className="card-value">
                                  {formatIndicatorValue(key, currentValue)}
                                </div>
                                <div className="card-description">
                                  {getIndicatorDescription(key)}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              <section className="charts-section">
                <div className="section-header">
                  <h3>Visualizaciones</h3>
                  <p>Evolución temporal de indicadores clave</p>
                </div>
                <div className="charts-grid">
                  <div className="chart-card">
                    <div className="chart-header">
                      <h4>Evolución de Liquidez</h4>
                      <p>Tendencia en el tiempo</p>
                    </div>
                    <FinancialChart 
                      data={financialData} 
                      type="liquidity" 
                      title="Liquidez"
                    />
                  </div>
                  <div className="chart-card">
                    <div className="chart-header">
                      <h4>Rentabilidad Histórica</h4>
                      <p>ROE, ROA y Márgenes</p>
                    </div>
                    <FinancialChart 
                      data={financialData} 
                      type="profitability" 
                      title="Rentabilidad"
                    />
                  </div>
                </div>
                <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                  <button 
                    onClick={() => handleNavClick('charts')}
                    className="upload-btn"
                    style={{ display: 'inline-flex' }}
                  >
                    <Icons.Chart />
                    <span>Ver todas las gráficas</span>
                  </button>
                </div>
              </section>

              {financialData && (
                <section className="summary-section">
                  <div className="summary-cards">
                    <div className="summary-card">
                      <h4>Periodos Analizados</h4>
                      <div className="summary-value">
                        {financialData.available_years.length}
                      </div>
                      <p>Años de datos financieros</p>
                    </div>
                    <div className="summary-card">
                      <h4>Indicadores Calculados</h4>
                      <div className="summary-value">
                        {Object.values(financialData.indicators).reduce((sum, category) => 
                          sum + Object.keys(category).length, 0
                        )}
                      </div>
                      <p>Métricas clave</p>
                    </div>
                    <div className="summary-card">
                      <h4>Análisis Disponibles</h4>
                      <div className="summary-value">
                        {(financialData.horizontal_analysis ? 1 : 0) + 
                         (financialData.vertical_analysis ? 1 : 0)}
                      </div>
                      <p>Horizontal y Vertical</p>
                    </div>
                  </div>
                </section>
              )}
            </>
          )}
        </main>

        {/* Chat - Modo Fixed o Floating */}
        {chatMode === 'fixed' ? (
          <aside className={`chat-sidebar ${!chatOpen ? 'hidden' : ''}`}>
            <div className="chat-header">
              <div className="chat-header-title">
                <h3>Asistente de Análisis</h3>
                <p>Consulta sobre indicadores</p>
              </div>
              <div className="chat-controls">
                <button 
                  className="chat-control-btn"
                  onClick={() => setChatOpen(false)}
                  title="Cerrar"
                >
                  <Icons.Close />
                </button>
              </div>
            </div>
            <div className="chat-messages">
              {chatMessages.map((message, index) => (
                <div key={index} className={`message ${message.type}`}>
                  <div className="message-content">
                    {message.text}
                  </div>
                </div>
              ))}
            </div>
            <div className="chat-input">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Escribe tu pregunta..."
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              />
              <button onClick={handleSendMessage}>
                <Icons.Send />
              </button>
            </div>
          </aside>
        ) : (
          <div className={`chat-floating ${!chatOpen ? 'hidden' : ''} ${chatMinimized ? 'minimized' : ''}`}>
            <div className="chat-header">
              <div className="chat-header-title">
                <h3>Asistente</h3>
                {!chatMinimized && <p>Consultas financieras</p>}
              </div>
              <div className="chat-controls">
                <button 
                  className="chat-control-btn"
                  onClick={() => setChatMinimized(!chatMinimized)}
                  title={chatMinimized ? "Maximizar" : "Minimizar"}
                >
                  {chatMinimized ? <Icons.Maximize /> : <Icons.Minimize />}
                </button>
                <button 
                  className="chat-control-btn"
                  onClick={() => setChatOpen(false)}
                  title="Cerrar"
                >
                  <Icons.Close />
                </button>
              </div>
            </div>
            {!chatMinimized && (
              <>
                <div className="chat-messages">
                  {chatMessages.map((message, index) => (
                    <div key={index} className={`message ${message.type}`}>
                      <div className="message-content">
                        {message.text}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="chat-input">
                  <input
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder="Escribe tu pregunta..."
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  />
                  <button onClick={handleSendMessage}>
                    <Icons.Send />
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;