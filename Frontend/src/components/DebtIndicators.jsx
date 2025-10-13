import React from 'react';
import { Line } from 'react-chartjs-2';

const DebtIndicators = ({ data, selectedYear }) => {
  if (!data || !data.indicators || !data.indicators.endeudamiento) {
    return <div>No hay datos de endeudamiento disponibles</div>;
  }

  const { endeudamiento } = data.indicators;
  const years = data.available_years || [];

  const formatPercentage = (value) => {
    if (value === undefined || value === null) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatNumber = (value) => {
    if (value === undefined || value === null) return 'N/A';
    return value.toFixed(2);
  };

  const getRiskColor = (clasificacion) => {
    switch (clasificacion) {
      case 'Bajo':
        return '#059669';
      case 'Medio':
        return '#d97706';
      case 'Alto':
        return '#dc2626';
      default:
        return '#6b7280';
    }
  };

  // Datos para gráfica
  const chartData = {
    labels: years,
    datasets: [
      {
        label: 'Endeudamiento Total',
        data: years.map(year => (endeudamiento.endeudamiento_total?.[year] || 0) * 100),
        borderColor: 'rgb(220, 38, 38)',
        backgroundColor: 'rgba(220, 38, 38, 0.1)',
        tension: 0.4,
        borderWidth: 2,
      },
      {
        label: 'Deuda/Patrimonio',
        data: years.map(year => (endeudamiento.deuda_patrimonio?.[year] || 0) * 100),
        borderColor: 'rgb(217, 119, 6)',
        backgroundColor: 'rgba(217, 119, 6, 0.1)',
        tension: 0.4,
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
      title: {
        display: true,
        text: 'Evolución de Endeudamiento',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: function(context) {
            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Porcentaje (%)'
        },
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        }
      }
    }
  };

  const currentYearData = {
    endeudamiento_total: endeudamiento.endeudamiento_total?.[selectedYear],
    deuda_patrimonio: endeudamiento.deuda_patrimonio?.[selectedYear],
    cobertura_intereses: endeudamiento.cobertura_intereses?.[selectedYear],
    clasificacion_riesgo: endeudamiento.clasificacion_riesgo?.[selectedYear]
  };

  return (
    <div className="debt-indicators-section">
      <div className="section-header">
        <h3>Indicadores de Endeudamiento</h3>
        <p>Evaluación de la estructura de deuda y capacidad de pago</p>
      </div>

      {/* Cards de indicadores */}
      <div className="indicators-grid">
        <div className="indicator-card">
          <div className="card-header">
            <h5>Endeudamiento Total</h5>
            <span className="indicator-tag">Estructura</span>
          </div>
          <div className="card-value">
            {formatPercentage(currentYearData.endeudamiento_total)}
          </div>
          <div className="card-description">
            Proporción de activos financiados con deuda. Ideal menor a 50%
          </div>
          <div className="card-interpretation">
            {currentYearData.endeudamiento_total && (
              <span className={`interpretation-badge ${currentYearData.endeudamiento_total > 0.6 ? 'bad' : currentYearData.endeudamiento_total > 0.4 ? 'warning' : 'good'}`}>
                {currentYearData.endeudamiento_total > 0.6 ? 'Alto' : currentYearData.endeudamiento_total > 0.4 ? 'Moderado' : 'Bajo'}
              </span>
            )}
          </div>
        </div>

        <div className="indicator-card">
          <div className="card-header">
            <h5>Deuda/Patrimonio</h5>
            <span className="indicator-tag">Apalancamiento</span>
          </div>
          <div className="card-value">
            {formatNumber(currentYearData.deuda_patrimonio)}
          </div>
          <div className="card-description">
            Veces que la deuda supera al patrimonio. Menor es mejor
          </div>
          <div className="card-interpretation">
            {currentYearData.deuda_patrimonio && (
              <span className={`interpretation-badge ${currentYearData.deuda_patrimonio > 1.5 ? 'bad' : currentYearData.deuda_patrimonio > 1 ? 'warning' : 'good'}`}>
                {currentYearData.deuda_patrimonio > 1.5 ? 'Muy Alto' : currentYearData.deuda_patrimonio > 1 ? 'Alto' : 'Adecuado'}
              </span>
            )}
          </div>
        </div>

        <div className="indicator-card">
          <div className="card-header">
            <h5>Cobertura de Intereses</h5>
            <span className="indicator-tag">Capacidad de Pago</span>
          </div>
          <div className="card-value">
            {formatNumber(currentYearData.cobertura_intereses)}x
          </div>
          <div className="card-description">
            Veces que las utilidades cubren los intereses. Mayor a 3 es bueno
          </div>
          <div className="card-interpretation">
            {currentYearData.cobertura_intereses && (
              <span className={`interpretation-badge ${currentYearData.cobertura_intereses < 2 ? 'bad' : currentYearData.cobertura_intereses < 3 ? 'warning' : 'good'}`}>
                {currentYearData.cobertura_intereses < 2 ? 'Insuficiente' : currentYearData.cobertura_intereses < 3 ? 'Justo' : 'Bueno'}
              </span>
            )}
          </div>
        </div>

        <div className="indicator-card risk-classification">
          <div className="card-header">
            <h5>Clasificación de Riesgo</h5>
            <span className="indicator-tag">Evaluación Global</span>
          </div>
          <div className="card-value" style={{ color: getRiskColor(currentYearData.clasificacion_riesgo) }}>
            {currentYearData.clasificacion_riesgo || 'N/A'}
          </div>
          <div className="card-description">
            Evaluación integral del riesgo crediticio de la empresa
          </div>
        </div>
      </div>

      {/* Gráfica */}
      <div className="chart-container">
        <div className="chart-wrapper" style={{ height: '350px' }}>
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Análisis y Recomendaciones */}
      <div className="analysis-box">
        <h4>Análisis de Endeudamiento</h4>
        <div className="analysis-content">
          {currentYearData.endeudamiento_total && (
            <>
              {currentYearData.endeudamiento_total > 0.6 ? (
                <div className="analysis-item warning">
                  <strong>Alerta:</strong> El nivel de endeudamiento es alto ({formatPercentage(currentYearData.endeudamiento_total)}). 
                  Se recomienda reducir deuda o aumentar patrimonio.
                </div>
              ) : currentYearData.endeudamiento_total > 0.4 ? (
                <div className="analysis-item info">
                  <strong>Atención:</strong> El endeudamiento está en nivel moderado ({formatPercentage(currentYearData.endeudamiento_total)}). 
                  Mantener vigilancia sobre nuevas deudas.
                </div>
              ) : (
                <div className="analysis-item success">
                  <strong>Positivo:</strong> El nivel de endeudamiento es bajo ({formatPercentage(currentYearData.endeudamiento_total)}). 
                  La empresa tiene capacidad para asumir más deuda si es necesario.
                </div>
              )}

              {currentYearData.cobertura_intereses < 2 && (
                <div className="analysis-item warning">
                  <strong>Riesgo:</strong> La cobertura de intereses es baja ({formatNumber(currentYearData.cobertura_intereses)}x). 
                  Las utilidades apenas cubren los gastos financieros.
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default DebtIndicators;