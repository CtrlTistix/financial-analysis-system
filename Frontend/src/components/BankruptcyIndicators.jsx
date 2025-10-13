import React from 'react';
import { Line } from 'react-chartjs-2';

const BankruptcyIndicators = ({ data, selectedYear }) => {
  if (!data || !data.indicators || !data.indicators.quiebra) {
    return <div>No hay datos de análisis de quiebra disponibles</div>;
  }

  const { quiebra } = data.indicators;
  const years = data.available_years || [];

  const getZScoreData = (year) => {
    const yearData = quiebra.z_score?.[year];
    return typeof yearData === 'object' ? yearData : { value: yearData };
  };

  const currentYearData = {
    z_score: getZScoreData(selectedYear).value || quiebra.z_score?.[selectedYear] || 0,
    clasificacion: quiebra.clasificacion_z?.[selectedYear] || 'Sin datos',
    probabilidad: quiebra.probabilidad_quiebra?.[selectedYear] || 'Indeterminada',
    componentes: getZScoreData(selectedYear).componentes
  };

  const getZoneColor = (clasificacion) => {
    switch (clasificacion) {
      case 'Zona Segura':
        return '#059669';
      case 'Zona Gris':
        return '#d97706';
      case 'Zona de Peligro':
        return '#dc2626';
      default:
        return '#6b7280';
    }
  };

  const getZoneBackground = (clasificacion) => {
    switch (clasificacion) {
      case 'Zona Segura':
        return 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)';
      case 'Zona Gris':
        return 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)';
      case 'Zona de Peligro':
        return 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)';
      default:
        return '#f3f4f6';
    }
  };

  // Datos para gráfica de evolución Z-Score
  const chartData = {
    labels: years,
    datasets: [
      {
        label: 'Z-Score',
        data: years.map(year => {
          const zData = getZScoreData(year);
          return zData.value || quiebra.z_score?.[year] || 0;
        }),
        borderColor: 'rgb(37, 99, 235)',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.4,
        borderWidth: 3,
        fill: true,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: 'Evolución del Z-Score de Altman',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const value = context.parsed.y;
            let zone = 'Zona de Peligro';
            if (value > 2.99) zone = 'Zona Segura';
            else if (value >= 1.81) zone = 'Zona Gris';
            return `Z-Score: ${value.toFixed(2)} (${zone})`;
          }
        }
      },
      annotation: {
        annotations: {
          line1: {
            type: 'line',
            yMin: 2.99,
            yMax: 2.99,
            borderColor: '#059669',
            borderWidth: 2,
            borderDash: [5, 5],
            label: {
              content: 'Zona Segura (> 2.99)',
              enabled: true,
              position: 'end'
            }
          },
          line2: {
            type: 'line',
            yMin: 1.81,
            yMax: 1.81,
            borderColor: '#dc2626',
            borderWidth: 2,
            borderDash: [5, 5],
            label: {
              content: 'Zona Peligro (< 1.81)',
              enabled: true,
              position: 'end'
            }
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Z-Score'
        },
        ticks: {
          callback: function(value) {
            return value.toFixed(1);
          }
        }
      }
    }
  };

  return (
    <div className="bankruptcy-indicators-section">
      <div className="section-header">
        <h3>Análisis de Quiebra - Modelo Z-Score de Altman</h3>
        <p>Evaluación del riesgo de insolvencia empresarial</p>
      </div>

      {/* Z-Score Principal */}
      <div className="z-score-main" style={{ background: getZoneBackground(currentYearData.clasificacion) }}>
        <div className="z-score-container">
          <div className="z-score-label">Z-Score Actual</div>
          <div className="z-score-value" style={{ color: getZoneColor(currentYearData.clasificacion) }}>
            {currentYearData.z_score.toFixed(2)}
          </div>
          <div className="z-score-classification">
            <span className="classification-badge" style={{ 
              backgroundColor: getZoneColor(currentYearData.clasificacion),
              color: 'white'
            }}>
              {currentYearData.clasificacion}
            </span>
          </div>
          <div className="z-score-probability">
            Probabilidad de Quiebra: <strong>{currentYearData.probabilidad}</strong>
          </div>
        </div>

        <div className="z-score-interpretation">
          <h4>Interpretación</h4>
          <div className="interpretation-zones">
            <div className={`zone-item ${currentYearData.z_score > 2.99 ? 'active' : ''}`}>
              <div className="zone-color" style={{ backgroundColor: '#059669' }}></div>
              <div className="zone-info">
                <strong>Zona Segura (Z {'>'} 2.99)</strong>
                <p>Baja probabilidad de quiebra en los próximos 2 años</p>
              </div>
            </div>
            <div className={`zone-item ${currentYearData.z_score >= 1.81 && currentYearData.z_score <= 2.99 ? 'active' : ''}`}>
              <div className="zone-color" style={{ backgroundColor: '#d97706' }}></div>
              <div className="zone-info">
                <strong>Zona Gris (1.81 ≤ Z ≤ 2.99)</strong>
                <p>Probabilidad media - requiere atención y seguimiento</p>
              </div>
            </div>
            <div className={`zone-item ${currentYearData.z_score < 1.81 ? 'active' : ''}`}>
              <div className="zone-color" style={{ backgroundColor: '#dc2626' }}></div>
              <div className="zone-info">
                <strong>Zona de Peligro (Z {'<'} 1.81)</strong>
                <p>Alta probabilidad de quiebra - situación crítica</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Gráfica de evolución */}
      <div className="chart-container">
        <div className="chart-wrapper" style={{ height: '350px' }}>
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Componentes del Z-Score */}
      {currentYearData.componentes && (
        <div className="components-section">
          <h4>Componentes del Z-Score</h4>
          <p className="components-description">
            El Z-Score se calcula combinando 5 ratios financieros ponderados
          </p>
          <div className="components-grid">
            <div className="component-card">
              <div className="component-label">Capital de Trabajo / Activos</div>
              <div className="component-value">{(currentYearData.componentes.capital_trabajo_activos * 100).toFixed(2)}%</div>
              <div className="component-weight">Peso: 1.2</div>
            </div>
            <div className="component-card">
              <div className="component-label">Utilidades Retenidas / Activos</div>
              <div className="component-value">{(currentYearData.componentes.utilidades_retenidas_activos * 100).toFixed(2)}%</div>
              <div className="component-weight">Peso: 1.4</div>
            </div>
            <div className="component-card">
              <div className="component-label">EBIT / Activos</div>
              <div className="component-value">{(currentYearData.componentes.ebit_activos * 100).toFixed(2)}%</div>
              <div className="component-weight">Peso: 3.3</div>
            </div>
            <div className="component-card">
              <div className="component-label">Patrimonio / Pasivos</div>
              <div className="component-value">{(currentYearData.componentes.patrimonio_pasivos * 100).toFixed(2)}%</div>
              <div className="component-weight">Peso: 0.6</div>
            </div>
            <div className="component-card">
              <div className="component-label">Ventas / Activos</div>
              <div className="component-value">{currentYearData.componentes.ventas_activos.toFixed(2)}x</div>
              <div className="component-weight">Peso: 1.0</div>
            </div>
          </div>
        </div>
      )}

      {/* Análisis y Recomendaciones */}
      <div className="analysis-box">
        <h4>Análisis y Recomendaciones</h4>
        <div className="analysis-content">
          {currentYearData.z_score < 1.81 && (
            <>
              <div className="analysis-item critical">
                <strong>Situación Crítica:</strong> El Z-Score indica alta probabilidad de quiebra. 
                Se requieren acciones inmediatas para mejorar la situación financiera.
              </div>
              <div className="recommendations">
                <h5>Acciones Urgentes:</h5>
                <ul>
                  <li>Reestructurar deuda inmediatamente</li>
                  <li>Mejorar generación de flujo de caja</li>
                  <li>Reducir gastos operativos no esenciales</li>
                  <li>Considerar venta de activos no productivos</li>
                  <li>Buscar inyección de capital</li>
                </ul>
              </div>
            </>
          )}

          {currentYearData.z_score >= 1.81 && currentYearData.z_score <= 2.99 && (
            <>
              <div className="analysis-item warning">
                <strong>Zona de Atención:</strong> La empresa está en zona gris. 
                Se recomienda monitoreo constante y acciones preventivas.
              </div>
              <div className="recommendations">
                <h5>Acciones Recomendadas:</h5>
                <ul>
                  <li>Fortalecer capital de trabajo</li>
                  <li>Mejorar rentabilidad operativa</li>
                  <li>Optimizar estructura de capital</li>
                  <li>Incrementar eficiencia en uso de activos</li>
                  <li>Controlar crecimiento de pasivos</li>
                </ul>
              </div>
            </>
          )}

          {currentYearData.z_score > 2.99 && (
            <>
              <div className="analysis-item success">
                <strong>Situación Saludable:</strong> El Z-Score indica baja probabilidad de quiebra. 
                La empresa muestra solidez financiera.
              </div>
              <div className="recommendations">
                <h5>Recomendaciones de Mejora:</h5>
                <ul>
                  <li>Mantener disciplina financiera</li>
                  <li>Considerar inversiones en crecimiento</li>
                  <li>Optimizar estructura de capital para eficiencia fiscal</li>
                  <li>Evaluar oportunidades de expansión</li>
                  <li>Continuar monitoreo preventivo</li>
                </ul>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Información del modelo */}
      <div className="model-info">
        <h4>Sobre el Modelo Z-Score de Altman</h4>
        <p>
          El Z-Score es un modelo estadístico desarrollado por Edward Altman en 1968 
          para predecir la probabilidad de quiebra de una empresa. El modelo ha demostrado 
          una precisión del 80-90% en predicciones a 2 años.
        </p>
        <p>
          <strong>Fórmula:</strong> Z = 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅
        </p>
      </div>
    </div>
  );
};

export default BankruptcyIndicators;