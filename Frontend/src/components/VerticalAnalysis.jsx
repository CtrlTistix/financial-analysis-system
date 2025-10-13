import React, { useState } from 'react';
import { Doughnut, Bar } from 'react-chartjs-2';

const VerticalAnalysis = ({ data, selectedYear }) => {
  const [viewType, setViewType] = useState('balance'); // 'balance' o 'results'
  
  if (!data || !data.raw_data || !data.available_years) {
    return (
      <div className="vertical-analysis-section">
        <div className="section-header">
          <h3>Análisis Vertical</h3>
          <p>No hay datos disponibles para el análisis</p>
        </div>
      </div>
    );
  }

  const rawData = data.raw_data;
  const activoTotal = parseFloat(rawData.activo_total?.[selectedYear]) || 1;
  const ingresos = parseFloat(rawData.ingresos?.[selectedYear] || rawData.ventas?.[selectedYear]) || 1;

  // Cuentas de balance
  const balanceAccounts = {
    'Activo Corriente': parseFloat(rawData.activo_corriente?.[selectedYear]) || 0,
    'Inventario': parseFloat(rawData.inventario?.[selectedYear]) || 0,
    'Cuentas por Cobrar': parseFloat(rawData.cuentas_por_cobrar?.[selectedYear]) || 0,
    'Pasivo Corriente': parseFloat(rawData.pasivo_corriente?.[selectedYear]) || 0,
    'Pasivo Total': parseFloat(rawData.pasivo_total?.[selectedYear]) || 0,
    'Patrimonio': parseFloat(rawData.patrimonio?.[selectedYear]) || 0
  };

  // Cuentas de resultados
  const resultsAccounts = {
    'Costo de Ventas': parseFloat(rawData.costo_ventas?.[selectedYear]) || 0,
    'Utilidad Bruta': parseFloat(rawData.utilidad_bruta?.[selectedYear]) || 0,
    'Gastos Operacionales': Math.abs(parseFloat(rawData.gastos_intereses?.[selectedYear])) || 0,
    'Utilidad Neta': parseFloat(rawData.utilidad_neta?.[selectedYear]) || 0
  };

  // Calcular porcentajes para balance
  const balancePercentages = Object.entries(balanceAccounts).map(([name, value]) => ({
    name,
    value,
    percentage: (value / activoTotal) * 100
  })).filter(item => item.value !== 0);

  // Calcular porcentajes para resultados
  const resultsPercentages = Object.entries(resultsAccounts).map(([name, value]) => ({
    name,
    value,
    percentage: (value / ingresos) * 100
  })).filter(item => item.value !== 0);

  // Datos para gráfica de dona (Balance)
  const balanceDoughnutData = {
    labels: balancePercentages.map(item => item.name),
    datasets: [{
      data: balancePercentages.map(item => item.percentage),
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(236, 72, 153, 0.8)'
      ],
      borderColor: [
        'rgb(59, 130, 246)',
        'rgb(16, 185, 129)',
        'rgb(245, 158, 11)',
        'rgb(239, 68, 68)',
        'rgb(139, 92, 246)',
        'rgb(236, 72, 153)'
      ],
      borderWidth: 2
    }]
  };

  // Datos para gráfica de barras (Resultados)
  const resultsBarData = {
    labels: resultsPercentages.map(item => item.name),
    datasets: [{
      label: '% sobre Ingresos',
      data: resultsPercentages.map(item => item.percentage),
      backgroundColor: resultsPercentages.map(item => {
        if (item.name.includes('Utilidad')) return 'rgba(16, 185, 129, 0.7)';
        if (item.name.includes('Costo')) return 'rgba(239, 68, 68, 0.7)';
        return 'rgba(245, 158, 11, 0.7)';
      }),
      borderColor: resultsPercentages.map(item => {
        if (item.name.includes('Utilidad')) return 'rgb(16, 185, 129)';
        if (item.name.includes('Costo')) return 'rgb(239, 68, 68)';
        return 'rgb(245, 158, 11)';
      }),
      borderWidth: 2
    }]
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          padding: 15,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed || 0;
            return `${label}: ${value.toFixed(2)}%`;
          }
        }
      }
    }
  };

  const barOptions = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.parsed.x.toFixed(2)}% sobre ingresos`;
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        },
        title: {
          display: true,
          text: 'Porcentaje sobre Ingresos'
        }
      }
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const getComponentClass = (percentage) => {
    if (percentage >= 30) return 'major-component';
    if (percentage >= 15) return 'significant-component';
    if (percentage >= 5) return 'moderate-component';
    return 'minor-component';
  };

  return (
    <div className="vertical-analysis-section">
      <div className="section-header">
        <h3>Análisis Vertical</h3>
        <p>Estructura porcentual de estados financieros para {selectedYear}</p>
      </div>

      {/* Selector de vista */}
      <div className="view-selector">
        <button 
          className={`view-btn ${viewType === 'balance' ? 'active' : ''}`}
          onClick={() => setViewType('balance')}
        >
          Balance General
        </button>
        <button 
          className={`view-btn ${viewType === 'results' ? 'active' : ''}`}
          onClick={() => setViewType('results')}
        >
          Estado de Resultados
        </button>
      </div>

      {/* Vista de Balance General */}
      {viewType === 'balance' && (
        <>
          <div className="analysis-header">
            <h4>Estructura del Balance General</h4>
            <div className="base-info">
              <span className="base-label">Base de Cálculo:</span>
              <span className="base-value">Activo Total = {formatCurrency(activoTotal)}</span>
            </div>
          </div>

          <div className="content-grid">
            {/* Gráfica de dona */}
            <div className="chart-card">
              <h5>Distribución de Cuentas</h5>
              <div className="chart-wrapper" style={{ height: '350px' }}>
                <Doughnut data={balanceDoughnutData} options={doughnutOptions} />
              </div>
            </div>

            {/* Tabla de componentes */}
            <div className="components-table-card">
              <h5>Detalle de Componentes</h5>
              <div className="table-responsive">
                <table className="vertical-table">
                  <thead>
                    <tr>
                      <th>Cuenta</th>
                      <th className="text-right">Monto</th>
                      <th className="text-right">% del Total</th>
                      <th>Clasificación</th>
                    </tr>
                  </thead>
                  <tbody>
                    {balancePercentages
                      .sort((a, b) => b.percentage - a.percentage)
                      .map((item, index) => (
                        <tr key={index} className={getComponentClass(item.percentage)}>
                          <td className="account-name">{item.name}</td>
                          <td className="text-right">{formatCurrency(item.value)}</td>
                          <td className="text-right">
                            <strong>{item.percentage.toFixed(2)}%</strong>
                          </td>
                          <td>
                            <div className="percentage-bar">
                              <div 
                                className="percentage-fill" 
                                style={{ width: `${Math.min(item.percentage, 100)}%` }}
                              ></div>
                            </div>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Análisis */}
          <div className="analysis-box">
            <h4>Interpretación de la Estructura</h4>
            <div className="analysis-content">
              {balancePercentages.filter(item => item.percentage >= 30).length > 0 && (
                <div className="analysis-item info">
                  <strong>Componentes Principales:</strong> {balancePercentages
                    .filter(item => item.percentage >= 30)
                    .map(item => `${item.name} (${item.percentage.toFixed(1)}%)`)
                    .join(', ')} representan las partidas más significativas del balance.
                </div>
              )}
              
              {(() => {
                const pasivosPerc = (parseFloat(rawData.pasivo_total?.[selectedYear]) / activoTotal) * 100;
                const patrimonioPerc = (parseFloat(rawData.patrimonio?.[selectedYear]) / activoTotal) * 100;
                
                return (
                  <div className="analysis-item">
                    <strong>Estructura de Financiamiento:</strong> La empresa se financia en un {pasivosPerc.toFixed(1)}% 
                    con pasivos y {patrimonioPerc.toFixed(1)}% con patrimonio propio.
                  </div>
                );
              })()}
            </div>
          </div>
        </>
      )}

      {/* Vista de Estado de Resultados */}
      {viewType === 'results' && (
        <>
          <div className="analysis-header">
            <h4>Estructura del Estado de Resultados</h4>
            <div className="base-info">
              <span className="base-label">Base de Cálculo:</span>
              <span className="base-value">Ingresos = {formatCurrency(ingresos)}</span>
            </div>
          </div>

          <div className="content-grid">
            {/* Gráfica de barras */}
            <div className="chart-card">
              <h5>Composición de Resultados</h5>
              <div className="chart-wrapper" style={{ height: '350px' }}>
                <Bar data={resultsBarData} options={barOptions} />
              </div>
            </div>

            {/* Tabla de componentes */}
            <div className="components-table-card">
              <h5>Análisis de Márgenes</h5>
              <div className="table-responsive">
                <table className="vertical-table">
                  <thead>
                    <tr>
                      <th>Concepto</th>
                      <th className="text-right">Monto</th>
                      <th className="text-right">% sobre Ingresos</th>
                      <th>Evaluación</th>
                    </tr>
                  </thead>
                  <tbody>
                    {resultsPercentages
                      .sort((a, b) => b.percentage - a.percentage)
                      .map((item, index) => (
                        <tr key={index}>
                          <td className="account-name">{item.name}</td>
                          <td className="text-right">{formatCurrency(item.value)}</td>
                          <td className="text-right">
                            <strong>{item.percentage.toFixed(2)}%</strong>
                          </td>
                          <td>
                            {item.name.includes('Utilidad') ? (
                              <span className="badge-positive">Positivo</span>
                            ) : item.name.includes('Costo') ? (
                              <span className="badge-neutral">Operativo</span>
                            ) : (
                              <span className="badge-warning">Gasto</span>
                            )}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Análisis de márgenes */}
          <div className="margins-analysis">
            <h4>Análisis de Márgenes</h4>
            <div className="margins-grid">
              {resultsPercentages.map((item, index) => (
                <div key={index} className="margin-card">
                  <div className="margin-header">
                    <span className="margin-name">{item.name}</span>
                    <span className="margin-percentage">{item.percentage.toFixed(2)}%</span>
                  </div>
                  <div className="margin-bar">
                    <div 
                      className={`margin-fill ${item.name.includes('Utilidad') ? 'positive' : 'neutral'}`}
                      style={{ width: `${Math.min(Math.abs(item.percentage), 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Análisis */}
          <div className="analysis-box">
            <h4>Interpretación de Resultados</h4>
            <div className="analysis-content">
              {(() => {
                const costoPerc = (parseFloat(rawData.costo_ventas?.[selectedYear]) / ingresos) * 100;
                const utilidadNetaPerc = (parseFloat(rawData.utilidad_neta?.[selectedYear]) / ingresos) * 100;
                
                return (
                  <>
                    <div className="analysis-item">
                      <strong>Margen Bruto:</strong> Por cada $100 en ventas, la empresa retiene ${(100 - costoPerc).toFixed(2)} 
                      después de cubrir los costos directos.
                    </div>
                    <div className="analysis-item">
                      <strong>Margen Neto:</strong> La utilidad final representa el {utilidadNetaPerc.toFixed(2)}% de los ingresos totales.
                    </div>
                    {utilidadNetaPerc < 5 && (
                      <div className="analysis-item warning">
                        <strong>Atención:</strong> El margen neto es relativamente bajo. Considerar optimización de costos y gastos.
                      </div>
                    )}
                  </>
                );
              })()}
            </div>
          </div>
        </>
      )}

      {/* Leyenda de clasificación */}
      <div className="legend-box">
        <h5>Clasificación de Componentes</h5>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color major-component"></span>
            <span>Mayor (≥30%): Componente principal</span>
          </div>
          <div className="legend-item">
            <span className="legend-color significant-component"></span>
            <span>Significativo (15-30%): Componente importante</span>
          </div>
          <div className="legend-item">
            <span className="legend-color moderate-component"></span>
            <span>Moderado (5-15%): Componente relevante</span>
          </div>
          <div className="legend-item">
            <span className="legend-color minor-component"></span>
            <span>Menor ({'<'}5%): Componente secundario</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerticalAnalysis;