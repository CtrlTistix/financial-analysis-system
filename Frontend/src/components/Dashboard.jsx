import React, { useState } from 'react';
import YearFilter from './YearFilter';
import IndicatorCard from './IndicatorCard';
import FinancialChart from './FinancialChart';

const Dashboard = ({ data }) => {
  const [selectedYear, setSelectedYear] = useState(data.available_years[0]?.toString() || '');

  if (!data || !data.indicators) {
    return <div>No hay datos disponibles</div>;
  }

  const { available_years, indicators } = data;

  return (
    <div className="dashboard">
      <h2>📈 Dashboard de Análisis Financiero</h2>
      
      <YearFilter 
        years={available_years} 
        selectedYear={selectedYear}
        onYearChange={setSelectedYear}
      />

      <div className="indicators-grid">
        {/* Indicadores de Liquidez */}
        <div className="indicator-section">
          <h3>💧 Indicadores de Liquidez</h3>
          {indicators.liquidez && Object.entries(indicators.liquidez).map(([key, values]) => (
            <IndicatorCard
              key={key}
              title={key.replace('_', ' ').toUpperCase()}
              value={values[selectedYear]}
              year={selectedYear}
            />
          ))}
        </div>

        {/* Indicadores de Rentabilidad */}
        <div className="indicator-section">
          <h3>💰 Indicadores de Rentabilidad</h3>
          {indicators.rentabilidad && Object.entries(indicators.rentabilidad).map(([key, values]) => (
            <IndicatorCard
              key={key}
              title={key.toUpperCase()}
              value={values[selectedYear]}
              year={selectedYear}
            />
          ))}
        </div>
      </div>

      {/* Gráficas */}
      <div className="charts-section">
        <h3>📊 Evolución de Indicadores</h3>
        <div className="charts-grid">
          <FinancialChart 
            data={indicators.liquidez} 
            title="Liquidez" 
            selectedYear={selectedYear}
          />
          <FinancialChart 
            data={indicators.rentabilidad} 
            title="Rentabilidad" 
            selectedYear={selectedYear}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;