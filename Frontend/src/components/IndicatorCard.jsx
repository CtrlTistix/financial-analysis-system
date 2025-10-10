import React from 'react';

const IndicatorCard = ({ title, value, year }) => {
  const formatValue = (val) => {
    if (typeof val === 'number') {
      // Si es un ratio, mostrar como porcentaje, si es capital como moneda
      if (title.includes('CAPITAL')) {
        return `$${val.toLocaleString()}`;
      } else if (val < 1) {
        return `${(val * 100).toFixed(2)}%`;
      } else {
        return val.toFixed(2);
      }
    }
    return val;
  };

  return (
    <div className="indicator-card">
      <h4>{title}</h4>
      <div className="indicator-value">{formatValue(value)}</div>
      <div className="indicator-year">Año {year}</div>
    </div>
  );
};

export default IndicatorCard;