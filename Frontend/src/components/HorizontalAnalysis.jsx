import React, { useState } from 'react';
import { Bar } from 'react-chartjs-2';

const HorizontalAnalysis = ({ data }) => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  if (!data || !data.raw_data || !data.available_years || data.available_years.length < 2) {
    return (
      <div className="horizontal-analysis-section">
        <div className="section-header">
          <h3>Análisis Horizontal</h3>
          <p>Se requieren al menos 2 períodos para realizar el análisis</p>
        </div>
      </div>
    );
  }

  const years = data.available_years;
  const rawData = data.raw_data;
  
  // Tomar los dos últimos años
  const year1 = years[years.length - 2];
  const year2 = years[years.length - 1];

  // Categorizar cuentas
  const categories = {
    activos: ['activo_corriente', 'activo_total', 'inventario', 'cuentas_por_cobrar'],
    pasivos: ['pasivo_corriente', 'pasivo_total'],
    patrimonio: ['patrimonio'],
    resultados: ['ingresos', 'ventas', 'costo_ventas', 'utilidad_bruta', 'utilidad_neta', 'utilidad_antes_impuestos']
  };

  // Calcular variaciones
  const calculateVariations = () => {
    const variations = [];
    
    Object.entries(rawData).forEach(([account, values]) => {
      const value1 = parseFloat(values[year1]) || 0;
      const value2 = parseFloat(values[year2]) || 0;
      
      if (value1 !== 0 || value2 !== 0) {
        const absoluteVariation = value2 - value1;
        const percentageVariation = value1 !== 0 ? ((value2 / value1) - 1) * 100 : 0;
        
        // Determinar categoría
        let category = 'otros';
        for (const [cat, accounts] of Object.entries(categories)) {
          if (accounts.includes(account)) {
            category = cat;
            break;
          }
        }
        
        variations.push({
          account,
          accountLabel: account.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          value1,
          value2,
          absoluteVariation,
          percentageVariation,
          category
        });
      }
    });
    
    return variations;
  };

  const allVariations = calculateVariations();
  
  // Filtrar por categoría
  const filteredVariations = selectedCategory === 'all' 
    ? allVariations 
    : allVariations.filter(v => v.category === selectedCategory);

  // Ordenar por variación porcentual
  const sortedVariations = [...filteredVariations].sort((a, b) => 
    Math.abs(b.percentageVariation) - Math.abs(a.percentageVariation)
  );

  // Top 5 mayores incrementos y decrementos
  const topIncreases = [...allVariations]
    .filter(v => v.percentageVariation > 0)
    .sort((a, b) => b.percentageVariation - a.percentageVariation)
    .slice(0, 5);

  const topDecreases = [...allVariations]
    .filter(v => v.percentageVariation < 0)
    .sort((a, b) => a.percentageVariation - b.percentageVariation)
    .slice(0, 5);

  // Datos para gráfica de barras
  const chartData = {
    labels: sortedVariations.slice(0, 10).map(v => v.accountLabel),
    datasets: [{
      label: 'Variación %',
      data: sortedVariations.slice(0, 10).map(v => v.percentageVariation),
      backgroundColor: sortedVariations.slice(0, 10).map(v => 
        v.percentageVariation > 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(239, 68, 68, 0.7)'
      ),
      borderColor: sortedVariations.slice(0, 10).map(v => 
        v.percentageVariation > 0 ? 'rgb(16, 185, 129)' : 'rgb(239, 68, 68)'
      ),
      borderWidth: 2
    }]
  };

  const chartOptions = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: `Top 10 Variaciones ${year1} - ${year2}`,
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `Variación: ${context.parsed.x.toFixed(2)}%`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Variación Porcentual (%)'
        },
        ticks: {
          callback: function(value) {
            return value + '%';
          }
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

  const getVariationColor = (variation) => {
    if (variation > 10) return 'positive-high';
    if (variation > 0) return 'positive-low';
    if (variation < -10) return 'negative-high';
    return 'negative-low';
  };

  return (
    <div className="horizontal-analysis-section">
      <div className="section-header">
        <h3>Análisis Horizontal</h3>
        <p>Comparación de estados financieros entre {year1} y {year2}</p>
      </div>

      {/* Resumen ejecutivo */}
      <div className="summary-cards">
        <div className="summary-card highlight">
          <div className="summary-icon">📊</div>
          <div className="summary-content">
            <div className="summary-label">Cuentas Analizadas</div>
            <div className="summary-value">{allVariations.length}</div>
          </div>
        </div>
        <div className="summary-card positive">
          <div className="summary-icon">📈</div>
          <div className="summary-content">
            <div className="summary-label">Incrementos</div>
            <div className="summary-value">
              {allVariations.filter(v => v.percentageVariation > 0).length}
            </div>
          </div>
        </div>
        <div className="summary-card negative">
          <div className="summary-icon">📉</div>
          <div className="summary-content">
            <div className="summary-label">Decrementos</div>
            <div className="summary-value">
              {allVariations.filter(v => v.percentageVariation < 0).length}
            </div>
          </div>
        </div>
        <div className="summary-card neutral">
          <div className="summary-icon">➖</div>
          <div className="summary-content">
            <div className="summary-label">Sin Cambio</div>
            <div className="summary-value">
              {allVariations.filter(v => v.percentageVariation === 0).length}
            </div>
          </div>
        </div>
      </div>

      {/* Top Variaciones */}
      <div className="top-variations-grid">
        <div className="top-variations-card increases">
          <h4>Top 5 Mayores Incrementos</h4>
          <div className="variations-list">
            {topIncreases.map((item, index) => (
              <div key={index} className="variation-item">
                <div className="variation-rank">{index + 1}</div>
                <div className="variation-info">
                  <div className="variation-account">{item.accountLabel}</div>
                  <div className="variation-value positive">
                    +{item.percentageVariation.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="top-variations-card decreases">
          <h4>Top 5 Mayores Decrementos</h4>
          <div className="variations-list">
            {topDecreases.map((item, index) => (
              <div key={index} className="variation-item">
                <div className="variation-rank">{index + 1}</div>
                <div className="variation-info">
                  <div className="variation-account">{item.accountLabel}</div>
                  <div className="variation-value negative">
                    {item.percentageVariation.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Gráfica de barras */}
      <div className="chart-container">
        <div className="chart-wrapper" style={{ height: '400px' }}>
          <Bar data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Filtros */}
      <div className="filters-section">
        <label>Filtrar por categoría:</label>
        <div className="filter-buttons">
          <button 
            className={`filter-btn ${selectedCategory === 'all' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('all')}
          >
            Todas
          </button>
          <button 
            className={`filter-btn ${selectedCategory === 'activos' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('activos')}
          >
            Activos
          </button>
          <button 
            className={`filter-btn ${selectedCategory === 'pasivos' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('pasivos')}
          >
            Pasivos
          </button>
          <button 
            className={`filter-btn ${selectedCategory === 'patrimonio' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('patrimonio')}
          >
            Patrimonio
          </button>
          <button 
            className={`filter-btn ${selectedCategory === 'resultados' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('resultados')}
          >
            Resultados
          </button>
        </div>
      </div>

      {/* Tabla detallada */}
      <div className="detailed-table">
        <h4>Análisis Detallado</h4>
        <div className="table-responsive">
          <table className="analysis-table">
            <thead>
              <tr>
                <th>Cuenta</th>
                <th className="text-right">{year1}</th>
                <th className="text-right">{year2}</th>
                <th className="text-right">Variación Absoluta</th>
                <th className="text-right">Variación %</th>
                <th>Tendencia</th>
              </tr>
            </thead>
            <tbody>
              {filteredVariations.map((item, index) => (
                <tr key={index}>
                  <td className="account-name">{item.accountLabel}</td>
                  <td className="text-right">{formatCurrency(item.value1)}</td>
                  <td className="text-right">{formatCurrency(item.value2)}</td>
                  <td className="text-right">
                    <span className={item.absoluteVariation >= 0 ? 'positive' : 'negative'}>
                      {formatCurrency(item.absoluteVariation)}
                    </span>
                  </td>
                  <td className="text-right">
                    <span className={`variation-badge ${getVariationColor(item.percentageVariation)}`}>
                      {item.percentageVariation >= 0 ? '+' : ''}{item.percentageVariation.toFixed(2)}%
                    </span>
                  </td>
                  <td className="text-center">
                    {item.percentageVariation > 5 ? '📈' : 
                     item.percentageVariation < -5 ? '📉' : '➡️'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Análisis automático */}
      <div className="analysis-box">
        <h4>Interpretación del Análisis Horizontal</h4>
        <div className="analysis-content">
          {topIncreases.length > 0 && (
            <div className="analysis-item info">
              <strong>Crecimiento Destacado:</strong> {topIncreases[0].accountLabel} creció {topIncreases[0].percentageVariation.toFixed(2)}%, 
              pasando de {formatCurrency(topIncreases[0].value1)} a {formatCurrency(topIncreases[0].value2)}.
            </div>
          )}
          
          {topDecreases.length > 0 && (
            <div className="analysis-item warning">
              <strong>Reducción Significativa:</strong> {topDecreases[0].accountLabel} disminuyó {Math.abs(topDecreases[0].percentageVariation).toFixed(2)}%, 
              de {formatCurrency(topDecreases[0].value1)} a {formatCurrency(topDecreases[0].value2)}.
            </div>
          )}

          <div className="analysis-item">
            <strong>Resumen:</strong> Entre {year1} y {year2}, se observaron {allVariations.filter(v => Math.abs(v.percentageVariation) > 10).length} 
            cambios significativos (mayores al 10%) en las cuentas financieras.
          </div>
        </div>
      </div>
    </div>
  );
};

export default HorizontalAnalysis;