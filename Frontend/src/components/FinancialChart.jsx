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

const FinancialChart = ({ data, type = 'line', title }) => {
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

  const options = {
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
        ...options,
        scales: {
          ...options.scales,
          y: {
            ...options.scales.y,
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
      }
    },
    profitability: {
      data: profitabilityData,
      options: {
        ...options,
        scales: {
          ...options.scales,
          y: {
            ...options.scales.y,
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
      }
    }
  };

  const config = chartConfigs[type] || { data: liquidityData, options };

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return <Bar data={config.data} options={config.options} />;
      case 'doughnut':
        return <Doughnut data={config.data} options={config.options} />;
      default:
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