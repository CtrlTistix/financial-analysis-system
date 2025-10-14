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
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const AdditionalCharts = ({ data, type }) => {
  if (!data || !data.indicators) return null;

  const years = data.available_years || [];

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
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        }
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        }
      },
    },
  };

  if (type === 'debt') {
    // Gráfica de Endeudamiento
    const chartData = {
      labels: years,
      datasets: [
        {
          label: 'Endeudamiento Total (%)',
          data: years.map(year => (data.indicators.endeudamiento?.endeudamiento_total?.[year] || 0) * 100),
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          borderWidth: 2,
        },
        {
          label: 'Deuda/Patrimonio',
          data: years.map(year => data.indicators.endeudamiento?.deuda_patrimonio?.[year] || 0),
          borderColor: 'rgb(249, 115, 22)',
          backgroundColor: 'rgba(249, 115, 22, 0.1)',
          tension: 0.4,
          borderWidth: 2,
        },
        {
          label: 'Cobertura Intereses',
          data: years.map(year => data.indicators.endeudamiento?.cobertura_intereses?.[year] || 0),
          borderColor: 'rgb(16, 185, 129)',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          borderWidth: 2,
        }
      ]
    };

    return (
      <div className="chart-wrapper">
        <Line data={chartData} options={baseOptions} />
      </div>
    );
  }

  if (type === 'rotation') {
    // Gráfica de Rotación
    const chartData = {
      labels: years,
      datasets: [
        {
          label: 'Rotación Inventarios',
          data: years.map(year => data.indicators.rotacion?.rotacion_inventarios?.[year] || 0),
          backgroundColor: 'rgba(139, 92, 246, 0.8)',
          borderColor: 'rgb(139, 92, 246)',
          borderWidth: 1,
        },
        {
          label: 'Rotación Cartera',
          data: years.map(year => data.indicators.rotacion?.rotacion_cartera?.[year] || 0),
          backgroundColor: 'rgba(6, 182, 212, 0.8)',
          borderColor: 'rgb(6, 182, 212)',
          borderWidth: 1,
        },
        {
          label: 'Rotación Activos',
          data: years.map(year => data.indicators.rotacion?.rotacion_activos?.[year] || 0),
          backgroundColor: 'rgba(16, 185, 129, 0.8)',
          borderColor: 'rgb(16, 185, 129)',
          borderWidth: 1,
        }
      ]
    };

    return (
      <div className="chart-wrapper">
        <Bar data={chartData} options={baseOptions} />
      </div>
    );
  }

  if (type === 'efficiency') {
    // Días de rotación
    const chartData = {
      labels: years,
      datasets: [
        {
          label: 'Días Inventario',
          data: years.map(year => data.indicators.rotacion?.dias_inventario?.[year] || 0),
          backgroundColor: 'rgba(245, 158, 11, 0.8)',
          borderColor: 'rgb(245, 158, 11)',
          borderWidth: 1,
        },
        {
          label: 'Días Cartera',
          data: years.map(year => data.indicators.rotacion?.dias_cartera?.[year] || 0),
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1,
        }
      ]
    };

    const options = {
      ...baseOptions,
      plugins: {
        ...baseOptions.plugins,
        tooltip: {
          ...baseOptions.plugins.tooltip,
          callbacks: {
            label: function(context) {
              return `${context.dataset.label}: ${Math.round(context.parsed.y)} días`;
            }
          }
        }
      }
    };

    return (
      <div className="chart-wrapper">
        <Bar data={chartData} options={options} />
      </div>
    );
  }

  return null;
};

export default AdditionalCharts;