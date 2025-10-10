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
import { Line } from 'react-chartjs-2';

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

const FinancialChart = ({ data, title, selectedYear }) => {
  if (!data) return <div>No hay datos para graficar</div>;

  const years = Object.keys(data[Object.keys(data)[0]] || {});
  const indicators = Object.keys(data);

  const chartData = {
    labels: years,
    datasets: indicators.map((indicator, index) => {
      const color = `hsl(${index * 137.5}, 70%, 50%)`;
      return {
        label: indicator.replace('_', ' ').toUpperCase(),
        data: years.map(year => data[indicator][year]),
        borderColor: color,
        backgroundColor: color + '20',
        tension: 0.1,
        fill: true,
      };
    }),
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: title,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="chart-container">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default FinancialChart;