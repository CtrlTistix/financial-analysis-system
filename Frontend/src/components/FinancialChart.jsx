import annotationPlugin from 'chartjs-plugin-annotation';
ChartJS.register(annotationPlugin);
import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const FinancialChart = ({ data, type = 'liquidity', title }) => {
  if (!data || !data.available_years || data.available_years.length === 0) {
    return (
      <div className="chart-container">
        <div className="chart-placeholder">
          <p>No hay datos disponibles para la gráfica</p>
        </div>
      </div>
    );
  }

  const { available_years, indicators } = data;

  // Preparar datos para la gráfica de liquidez
  const liquidityData = {
    labels: available_years,
    datasets: [
      {
        label: 'Razón Corriente',
        data: available_years.map(year => indicators.liquidez?.razon_corriente?.[year] || 0),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        borderWidth: 2,
      },
      {
        label: 'Prueba Ácida',
        data: available_years.map(year => indicators.liquidez?.prueba_acida?.[year] || 0),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  };

  // Preparar datos para la gráfica de rentabilidad
  const profitabilityData = {
    labels: available_years,
    datasets: [
      {
        label: 'ROE (%)',
        data: available_years.map(year => (indicators.rentabilidad?.roe?.[year] || 0) * 100),
        borderColor: 'rgb(139, 92, 246)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        tension: 0.4,
        borderWidth: 2,
      },
      {
        label: 'ROA (%)',
        data: available_years.map(year => (indicators.rentabilidad?.roa?.[year] || 0) * 100),
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4,
        borderWidth: 2,
      },
      {
        label: 'Margen Bruto (%)',
        data: available_years.map(year => (indicators.rentabilidad?.margen_bruto?.[year] || 0) * 100),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  };

  // Preparar datos para Z-Score
  const zscoreData = {
    labels: available_years,
    datasets: [
      {
        label: 'Z-Score',
        data: available_years.map(year => indicators.quiebra?.z_score?.[year] || 0),
        borderColor: 'rgb(139, 92, 246)',
        backgroundColor: 'rgba(139, 92, 246, 0.2)',
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 6,
        pointHoverRadius: 8,
      },
    ],
  };

  const baseOptions = {
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
        text: title,
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: {
          size: 14
        },
        bodyFont: {
          size: 13
        },
        padding: 12,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          font: {
            size: 12
          }
        }
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          font: {
            size: 12
          }
        }
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    },
  };

  const chartConfigs = {
    liquidity: {
      data: liquidityData,
      options: {
        ...baseOptions,
        scales: {
          ...baseOptions.scales,
          y: {
            ...baseOptions.scales.y,
            title: {
              display: true,
              text: 'Ratio',
              font: {
                size: 12,
                weight: 'bold'
              }
            }
          },
        },
      },
      chartType: 'line'
    },
    profitability: {
      data: profitabilityData,
      options: {
        ...baseOptions,
        scales: {
          ...baseOptions.scales,
          y: {
            ...baseOptions.scales.y,
            title: {
              display: true,
              text: 'Porcentaje (%)',
              font: {
                size: 12,
                weight: 'bold'
              }
            }
          },
        },
      },
      chartType: 'line'
    },
    zscore: {
      data: zscoreData,
      options: {
        ...baseOptions,
        scales: {
          ...baseOptions.scales,
          y: {
            ...baseOptions.scales.y,
            min: 0,
            max: 5,
            title: {
              display: true,
              text: 'Z-Score',
              font: {
                size: 12,
                weight: 'bold'
              }
            }
          },
        },
        plugins: {
          ...baseOptions.plugins,
          annotation: {
            annotations: {
              line1: {
                type: 'line',
                yMin: 2.99,
                yMax: 2.99,
                borderColor: 'rgb(16, 185, 129)',
                borderWidth: 2,
                borderDash: [5, 5],
                label: {
                  display: true,
                  content: 'Zona Segura (> 2.99)',
                  position: 'end'
                }
              },
              line2: {
                type: 'line',
                yMin: 1.81,
                yMax: 1.81,
                borderColor: 'rgb(245, 158, 11)',
                borderWidth: 2,
                borderDash: [5, 5],
                label: {
                  display: true,
                  content: 'Zona Gris (1.81 - 2.99)',
                  position: 'end'
                }
              }
            }
          }
        }
      },
      chartType: 'line'
    }
  };

  const config = chartConfigs[type] || chartConfigs.liquidity;

  const renderChart = () => {
    if (config.chartType === 'bar') {
      return <Bar data={config.data} options={config.options} />;
    } else if (config.chartType === 'doughnut') {
      return <Doughnut data={config.data} options={config.options} />;
    } else {
      return <Line data={config.data} options={config.options} />;
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-wrapper">
        {renderChart()}
      </div>
    </div>
  );
};

export default FinancialChart;