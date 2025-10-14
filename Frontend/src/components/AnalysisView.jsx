import React, { useState } from 'react';

const AnalysisView = ({ data }) => {
  const [analysisType, setAnalysisType] = useState('horizontal');

  if (!data) return <div>No hay datos disponibles</div>;

  const getAccountLabel = (key) => {
    const labels = {
      'activo_corriente': 'Activo Corriente',
      'activo_total': 'Activo Total',
      'pasivo_corriente': 'Pasivo Corriente',
      'pasivo_total': 'Pasivo Total',
      'patrimonio': 'Patrimonio',
      'ingresos': 'Ingresos',
      'ventas': 'Ventas',
      'costo_ventas': 'Costo de Ventas',
      'utilidad_bruta': 'Utilidad Bruta',
      'utilidad_neta': 'Utilidad Neta',
      'inventario': 'Inventario',
      'cuentas_por_cobrar': 'Cuentas por Cobrar',
      'gastos_intereses': 'Gastos Financieros'
    };
    return labels[key] || key;
  };

  const formatCurrency = (value) => {
    return `$${Math.abs(value).toLocaleString('es-CO', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    })}`;
  };

  const formatPercentage = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const getVariationColor = (value) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const renderHorizontalAnalysis = () => {
    const horizontal = data.horizontal_analysis || {};
    const years = data.available_years || [];

    return (
      <div className="analysis-content">
        <div className="analysis-header" style={{ marginBottom: '20px' }}>
          <h3>Análisis Horizontal</h3>
          <p>Variaciones absolutas y porcentuales entre períodos</p>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600 }}>Cuenta</th>
                {years.map(year => (
                  <React.Fragment key={year}>
                    <th style={{ padding: '12px', textAlign: 'right' }}>{year}</th>
                    <th style={{ padding: '12px', textAlign: 'right' }}>Var. $</th>
                    <th style={{ padding: '12px', textAlign: 'right' }}>Var. %</th>
                  </React.Fragment>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(horizontal).map(([account, data]) => (
                <tr key={account} style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <td style={{ padding: '12px', fontWeight: 500 }}>{getAccountLabel(account)}</td>
                  {years.map((year, idx) => {
                    const value = data.values?.[year] || 0;
                    const absVar = data.absolute_variation?.[year] || 0;
                    const pctVar = data.percentage_variation?.[year] || 0;
                    
                    return (
                      <React.Fragment key={year}>
                        <td style={{ padding: '12px', textAlign: 'right' }}>
                          {formatCurrency(value)}
                        </td>
                        {idx > 0 ? (
                          <>
                            <td style={{ padding: '12px', textAlign: 'right' }} className={getVariationColor(absVar)}>
                              {formatCurrency(absVar)}
                            </td>
                            <td style={{ padding: '12px', textAlign: 'right', fontWeight: 600 }} className={getVariationColor(pctVar)}>
                              {formatPercentage(pctVar)}
                            </td>
                          </>
                        ) : (
                          <>
                            <td style={{ padding: '12px', textAlign: 'center' }}>-</td>
                            <td style={{ padding: '12px', textAlign: 'center' }}>-</td>
                          </>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderVerticalAnalysis = () => {
    const vertical = data.vertical_analysis || {};
    const years = data.available_years || [];

    return (
      <div className="analysis-content">
        <div className="analysis-header" style={{ marginBottom: '20px' }}>
          <h3>Análisis Vertical</h3>
          <p>Estructura porcentual de los estados financieros</p>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600 }}>Cuenta</th>
                {years.map(year => (
                  <th key={year} style={{ padding: '12px', textAlign: 'right' }}>
                    {year}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr style={{ backgroundColor: '#f9fafb', fontWeight: 600 }}>
                <td colSpan={years.length + 1} style={{ padding: '12px' }}>Balance General (% del Activo Total)</td>
              </tr>
              {Object.entries(vertical).filter(([key]) => 
                ['activo_corriente', 'activo_total', 'pasivo_corriente', 'pasivo_total', 'patrimonio'].includes(key)
              ).map(([account, data]) => (
                <tr key={account} style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <td style={{ padding: '12px', paddingLeft: '24px' }}>{getAccountLabel(account)}</td>
                  {years.map(year => {
                    const percentage = data[year] || 0;
                    return (
                      <td key={year} style={{ padding: '12px', textAlign: 'right' }}>
                        {percentage.toFixed(2)}%
                      </td>
                    );
                  })}
                </tr>
              ))}
              
              <tr style={{ backgroundColor: '#f9fafb', fontWeight: 600 }}>
                <td colSpan={years.length + 1} style={{ padding: '12px' }}>Estado de Resultados (% de Ingresos)</td>
              </tr>
              {Object.entries(vertical).filter(([key]) => 
                ['ingresos', 'costo_ventas', 'utilidad_bruta', 'utilidad_neta'].includes(key)
              ).map(([account, data]) => (
                <tr key={account} style={{ borderBottom: '1px solid #e5e7eb' }}>
                  <td style={{ padding: '12px', paddingLeft: '24px' }}>{getAccountLabel(account)}</td>
                  {years.map(year => {
                    const percentage = data[year] || 0;
                    return (
                      <td key={year} style={{ padding: '12px', textAlign: 'right' }}>
                        {percentage.toFixed(2)}%
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
        <button
          onClick={() => setAnalysisType('horizontal')}
          style={{
            padding: '10px 20px',
            backgroundColor: analysisType === 'horizontal' ? '#3b82f6' : '#e5e7eb',
            color: analysisType === 'horizontal' ? 'white' : '#374151',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 500
          }}
        >
          Análisis Horizontal
        </button>
        <button
          onClick={() => setAnalysisType('vertical')}
          style={{
            padding: '10px 20px',
            backgroundColor: analysisType === 'vertical' ? '#3b82f6' : '#e5e7eb',
            color: analysisType === 'vertical' ? 'white' : '#374151',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 500
          }}
        >
          Análisis Vertical
        </button>
      </div>

      {analysisType === 'horizontal' ? renderHorizontalAnalysis() : renderVerticalAnalysis()}
    </div>
  );
};

export default AnalysisView;