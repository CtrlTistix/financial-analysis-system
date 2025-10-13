import React, { useState, useEffect } from 'react';
import FinancialChart from './components/FinancialChart';
import Requirements from './components/Requirements';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [financialData, setFinancialData] = useState(null);
  const [selectedYear, setSelectedYear] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' o 'requirements'
  const [chatMessages, setChatMessages] = useState([
    { type: 'bot', text: 'Bienvenido al Sistema de Análisis Financiero. Estoy aquí para ayudarte a interpretar tus indicadores financieros.' }
  ]);
  const [userInput, setUserInput] = useState('');

  useEffect(() => {
    fetchTestData();
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
      addChatMessage('bot', 'Archivo procesado exitosamente. Los indicadores han sido actualizados.');
    } catch (err) {
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
      addChatMessage('bot', 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta nuevamente.');
    }
  };

  const formatIndicatorValue = (indicatorName, value) => {
    if (value === undefined || value === null) return 'No disponible';
    
    switch (indicatorName) {
      case 'razon_corriente':
      case 'prueba_acida':
        return value.toFixed(2);
      case 'capital_trabajo':
        return `$${Math.abs(value).toLocaleString()}`;
      case 'roe':
      case 'roa':
      case 'margen_bruto':
        return `${(value * 100).toFixed(2)}%`;
      default:
        return value;
    }
  };

  const getIndicatorLabel = (key) => {
    const labels = {
      'razon_corriente': 'Razón Corriente',
      'prueba_acida': 'Prueba Ácida',
      'capital_trabajo': 'Capital de Trabajo',
      'roe': 'Return on Equity (ROE)',
      'roa': 'Return on Assets (ROA)',
      'margen_bruto': 'Margen Bruto'
    };
    return labels[key] || key;
  };

  const getIndicatorDescription = (key) => {
    const descriptions = {
      'razon_corriente': 'Capacidad de pagar obligaciones a corto plazo',
      'prueba_acida': 'Liquidez inmediata sin considerar inventarios',
      'capital_trabajo': 'Recursos disponibles para operaciones',
      'roe': 'Rentabilidad sobre el capital de los accionistas',
      'roa': 'Eficiencia en el uso de los activos',
      'margen_bruto': 'Porcentaje de utilidad sobre ventas'
    };
    return descriptions[key] || 'Indicador financiero clave';
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
          <button 
            className="menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
          <div className="header-title">
            <h1>Sistema de Análisis Financiero</h1>
            <p>Análisis automatizado de estados financieros</p>
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
              Cargar Excel
            </label>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="app-layout">
        {/* Sidebar */}
        <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
          <nav className="sidebar-nav">
            <div className="nav-section">
              <h3>Análisis</h3>
              <ul>
                <li 
                  className={currentView === 'dashboard' ? 'active' : ''}
                  onClick={() => setCurrentView('dashboard')}
                >
                  Dashboard Principal
                </li>
                <li>Indicadores Financieros</li>
                <li>Análisis Comparativo</li>
                <li>Proyecciones</li>
              </ul>
            </div>
            <div className="nav-section">
              <h3>Reportes</h3>
              <ul>
                <li>Reporte de Liquidez</li>
                <li>Reporte de Rentabilidad</li>
                <li>Análisis Vertical</li>
                <li>Análisis Horizontal</li>
              </ul>
            </div>
            <div className="nav-section">
              <h3>Sistema</h3>
              <ul>
                <li 
                  className={currentView === 'requirements' ? 'active' : ''}
                  onClick={() => setCurrentView('requirements')}
                >
                  📋 Requerimientos
                </li>
                <li>Configuración</li>
                <li>Documentación</li>
              </ul>
            </div>
          </nav>
        </aside>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div 
            className="sidebar-overlay"
            onClick={() => setSidebarOpen(false)}
          ></div>
        )}

        {/* Main Content */}
        <main className="main-content">
          {currentView === 'requirements' ? (
            <Requirements />
          ) : (
            <>
              {error && (
                <div className="error-alert">
                  <div className="alert-content">
                    <strong>Error:</strong> {error}
                  </div>
                </div>
              )}

              {/* Dashboard Header */}
              <section className="dashboard-header">
                <div className="dashboard-title">
                  <h2>Dashboard de Análisis</h2>
                  <p>Indicadores financieros y métricas clave</p>
                </div>
                <div className="dashboard-controls">
                  <div className="year-filter">
                    <label>Periodo de análisis:</label>
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

              {/* Indicators Grid */}
              {financialData && (
                <section className="indicators-section">
                  <div className="section-header">
                    <h3>Indicadores Financieros</h3>
                    <p>Resultados para el año {selectedYear}</p>
                  </div>
                  
                  <div className="indicators-grid">
                    {/* Liquidity Indicators */}
                    <div className="indicator-category">
                      <h4 className="category-title">Indicadores de Liquidez</h4>
                      <div className="category-cards">
                        {financialData.indicators.liquidez && 
                        Object.entries(financialData.indicators.liquidez).map(([key, values]) => (
                          <div key={key} className="indicator-card">
                            <div className="card-header">
                              <h5>{getIndicatorLabel(key)}</h5>
                              <span className="indicator-tag">Liquidez</span>
                            </div>
                            <div className="card-value">
                              {formatIndicatorValue(key, values[selectedYear])}
                            </div>
                            <div className="card-description">
                              {getIndicatorDescription(key)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Profitability Indicators */}
                    <div className="indicator-category">
                      <h4 className="category-title">Indicadores de Rentabilidad</h4>
                      <div className="category-cards">
                        {financialData.indicators.rentabilidad && 
                        Object.entries(financialData.indicators.rentabilidad).map(([key, values]) => (
                          <div key={key} className="indicator-card">
                            <div className="card-header">
                              <h5>{getIndicatorLabel(key)}</h5>
                              <span className="indicator-tag">Rentabilidad</span>
                            </div>
                            <div className="card-value">
                              {formatIndicatorValue(key, values[selectedYear])}
                            </div>
                            <div className="card-description">
                              {getIndicatorDescription(key)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </section>
              )}

              {/* Charts Section */}
              <section className="charts-section">
                <div className="section-header">
                  <h3>Visualizaciones</h3>
                  <p>Evolución temporal de indicadores clave</p>
                </div>
                <div className="charts-grid">
                  <div className="chart-card">
                    <div className="chart-header">
                      <h4>Evolución de Liquidez</h4>
                      <p>Razón Corriente y Prueba Ácida a través del tiempo</p>
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
                      <p>ROE, ROA y Margen Bruto en porcentaje</p>
                    </div>
                    <FinancialChart 
                      data={financialData} 
                      type="profitability" 
                      title="Indicadores de Rentabilidad"
                    />
                  </div>
                </div>
              </section>

              {/* Data Summary */}
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
                      <div className="summary-value">6</div>
                      <p>Métricas clave</p>
                    </div>
                    <div className="summary-card">
                      <h4>Última Actualización</h4>
                      <div className="summary-value">Ahora</div>
                      <p>Datos en tiempo real</p>
                    </div>
                  </div>
                </section>
              )}
            </>
          )}
        </main>

        {/* Chat Sidebar */}
        <aside className="chat-sidebar">
          <div className="chat-header">
            <h3>Asistente de Análisis</h3>
            <p>Consulta sobre tus indicadores</p>
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
              placeholder="Escribe tu pregunta sobre los indicadores..."
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <button onClick={handleSendMessage}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default App;