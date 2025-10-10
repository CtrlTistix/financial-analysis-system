import React from 'react';

const YearFilter = ({ years, selectedYear, onYearChange }) => {
  return (
    <div className="year-filter">
      <label htmlFor="year-select">Filtrar por Año: </label>
      <select 
        id="year-select"
        value={selectedYear} 
        onChange={(e) => onYearChange(e.target.value)}
      >
        {years.map(year => (
          <option key={year} value={year.toString()}>
            {year}
          </option>
        ))}
      </select>
    </div>
  );
};

export default YearFilter;