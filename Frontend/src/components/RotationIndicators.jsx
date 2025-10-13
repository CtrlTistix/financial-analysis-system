import React from 'react';
import { Bar } from 'react-chartjs-2';

const RotationIndicators = ({ data, selectedYear }) => {
  if (!data || !data.indicators || !data.indicators.rotacion) {
    return <div>No hay datos de rotación disponibles</div>;
  }

  const { rotacion } = data.indicators;
  const years = data.available_years || [];

  const formatNumber = (value) => {
    if (value === undefined || value === null) return 'N/A';
    return value.toFixed(2);
  };

  const formatDays = (value) => {
    if (value === undefined || value === null) return 'N/A';
    return `${Math.round(value)} días`;
  };

  // Datos para gráfica de rotaciones
  const rotationChartData = {
    labels: years,
    datasets: [
      {
        label: 'Rotación de Inventarios',
        data: years.map(year => rotacion.rotacion_inventarios?.[year] || 0),
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 2,
      },
      {
        label: 'Rotación de Cartera',
        data: years.map(year => rotacion.rotacion_cartera?.[year] || 0),
        backgroundColor: 'rgba(16, 185, 129, 0.7)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 2,
      }
    ]
  };

  // Datos para gráfica de días
  const daysChartData = {
    labels: years,
    datasets: [
      {
        label: 'Días de Inventario',
        data: years.map(year => rotacion.dias_inventario?.[year] || 0),
        backgroundColor: 'rgba(245, 158, 11, 0.7)',
        borderColor: 'rgb(245, 158, 11)',
        borderWidth: 2,
      },
      {
        label: 'Días de Cartera',
        data: years.map(year => rotacion.dias_cartera?.[year] || 0),
        backgroundColor: 'rgba(139, 92, 246, 0.7)',
        borderColor: 'rgb(139, 92, 246)',
        borderWidth: 2,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  const currentYearData = {
    rotacion_inventarios: rotacion.rotacion_inventarios?.[selectedYear],
    rotacion_cartera: rotacion.rotacion_cartera?.[selectedYear],
    rotacion_activos: rotacion.rotacion_activos?.[selectedYear],
    dias_inventario: rotacion.dias_inventario?.[selectedYear],
    dias_cartera: rotacion.dias_cartera?.[selectedYear]
  };

  // Calcular ciclo de conversión de efectivo
  const cicloCaja = (currentYearData.dias_inventario || 0) + (currentYearData.dias_cartera || 0);

  return (
    <div className="rotation-indicators-section">
      <div className="section-header">
        <h3>Indicadores de Rotación y Actividad</h3>
        <p>Eficiencia en el uso de activos operativos</p>
      </div>

      {/* Cards de indicadores */}
      <div className="indicators-grid">
        <div className="indicator-card">
          <div className="card-header">
            <h5>Rotación de Inventarios</h5>
            <span className="indicator-tag">Eficiencia</span>
          </div>
          <div className="card-value">
            {formatNumber(currentYearData.rotacion_inventarios)}x
          </div>
          <div className="card-description">
            Veces que el inventario se vende y repone en el año
          </div>
          <div className="card-metric">
            <span className="metric-label">Días:</span>
            <span className="metric-value">{formatDays(currentYearData.dias_inventario)}</span>
          </div>
        </div>

        <div className="indicator-card">
          <div className="card-header">
            <h5>Rotación de Cartera</h5>
            <span className="indicator-tag">Cobros</span>
          </div>
          <div className="card-value">
            {formatNumber(currentYearData.rotacion_cartera)}x
          </div>
          <div className="card-description">
            Veces que se cobran las cuentas por cobrar al año
          </div>
          <div className="card-metric">
            <span className="metric-label">Días:</span>
            <span className="metric-value">{formatDays(currentYearData.dias_cartera)}</span>
          </div>
        </div>

        <div className="indicator-card">
          <div className="card-header">
            <h5>Rotación de Activos</h5>
            <span className="indicator-tag">Productividad</span>
          </div>
          <div className="card-value">
            {formatNumber(currentYearData.rotacion_activos)}x
          </div>
          <div className="card-description">
            Ventas generadas por cada peso invertido en activos
          </div>
          <div className="card-interpretation">
            {currentYearData.rotacion_activos && (
              <span className={`interpretation-badge ${currentYearData.rotacion_activos < 0.5 ? 'bad' : currentYearData.rotacion_activos < 1 ? 'warning' : 'good'}`}>
                {currentYearData.rotacion_activos < 0.5 ? 'Bajo' : currentYearData.rotacion_activos < 1 ? 'Moderado' : 'Bueno'}
              </span>
            )}
          </div>
        </div>

        <div className="indicator-card highlight-card">
          <div className="card-header">
            <h5>Ciclo de Caja</h5>
            <span className="indicator-tag">Gestión</span>
          </div>
          <div className="card-value">
            {Math.round(cicloCaja)} días
          </div>
          <div className="card-description">
            Tiempo desde la compra hasta el cobro final
          </div>
          <div className="card-interpretation">
            {cicloCaja > 0 && (
              <span className={`interpretation-badge ${cicloCaja > 90 ? 'bad' : cicloCaja > 60 ? 'warning' : 'good'}`}>
                {cicloCaja > 90 ? 'Largo' : cicloCaja > 60 ? 'Moderado' : 'Corto'}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Gráficas */}
      <div className="charts-grid">
        <div className="chart-card">
          <div className="chart-header">
            <h4>Evolución de Rotaciones</h4>
            <p>Mayor rotación indica mejor eficiencia operativa</p>
          </div>
          <div className="chart-wrapper" style={{ height: '300px' }}>
            <Bar data={rotationChartData} options={{...chartOptions, plugins: {...chartOptions.plugins, title: {display: false}}}} />
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h4>Días de Operación</h4>
            <p>Menos días significa mayor liquidez</p>
          </div>
          <div className="chart-wrapper" style={{ height: '300px' }}>
            <Bar data={daysChartData} options={{...chartOptions, plugins: {...chartOptions.plugins, title: {display: false}}}} />
          </div>
        </div>
      </div>

      {/* Tabla comparativa */}
      <div className="comparison-table">
        <h4>Comparativo Multi-período</h4>
        <table>
          <thead>
            <tr>
              <th>Indicador</th>
              {years.map(year => (
                <th key={year}>{year}</th>
              ))}
              <th>Tendencia</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Rotación Inventarios</td>
              {years.map(year => (
                <td key={year}>{formatNumber(rotacion.rotacion_inventarios?.[year])}</td>
              ))}
              <td>{this.getTrend(rotacion.rotacion_inventarios, years)}</td>
            </tr>
            <tr>
              <td>Rotación Cartera</td>
              {years.map(year => (
                <td key={year}>{formatNumber(rotacion.rotacion_cartera?.[year])}</td>
              ))}
              <td>{this.getTrend(rotacion.rotacion_cartera, years)}</td>
            </tr>
            <tr>
              <td>Días Inventario</td>
              {years.map(year => (
                <td key={year}>{Math.round(rotacion.dias_inventario?.[year] || 0)}</td>
              ))}
              <td>{this.getTrend(rotacion.dias_inventario, years, true)}</td>
            </tr>
            <tr>
              <td>Días Cartera</td>
              {years.map(year => (
                <td key={year}>{Math.round(rotacion.dias_cartera?.[year] || 0)}</td>
              ))}
              <td>{this.getTrend(rotacion.dias_cartera, years, true)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Análisis */}
      <div className="analysis-box">
        <h4>Análisis de Eficiencia Operativa</h4>
        <div className="analysis-content">
          {currentYearData.dias_inventario && currentYearData.dias_inventario > 60 && (
            <div className="analysis-item warning">
              <strong>Inventarios:</strong> Los productos permanecen {Math.round(currentYearData.dias_inventario)} días en inventario. 
              Considerar estrategias para agilizar la rotación.
            </div>
          )}
          
          {currentYearData.dias_cartera && currentYearData.dias_cartera > 45 && (
            <div className="analysis-item warning">
              <strong>Cartera:</strong> El período de cobro es de {Math.round(currentYearData.dias_cartera)} días. 
              Evaluar políticas de crédito y gestión de cobranza.
            </div>
          )}

          {cicloCaja > 90 && (
            <div className="analysis-item warning">
              <strong>Ciclo de Caja:</strong> El ciclo completo toma {Math.round(cicloCaja)} días. 
              Un ciclo más corto mejoraría la liquidez de la empresa.
            </div>
          )}

          {currentYearData.rotacion_activos < 1 && (
            <div className="analysis-item info">
              <strong>Activos:</strong> La rotación de activos es {formatNumber(currentYearData.rotacion_activos)}x. 
              Se genera menos de $1 en ventas por cada $1 en activos.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Función helper para determinar tendencia
RotationIndicators.prototype.getTrend = function(values, years, inverse = false) {
  if (!values || years.length < 2) return '—';
  
  const firstValue = values[years[0]];
  const lastValue = values[years[years.length - 1]];
  
  if (!firstValue || !lastValue) return '—';
  
  const change = ((lastValue - firstValue) / firstValue) * 100;
  const isPositive = inverse ? change < 0 : change > 0;
  
  return (
    <span className={isPositive ? 'trend-up' : 'trend-down'}>
      {isPositive ? '↑' : '↓'} {Math.abs(change).toFixed(1)}%
    </span>
  );
};

export default RotationIndicators;