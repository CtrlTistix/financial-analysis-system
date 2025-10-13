import React, { useState } from 'react';

const API_BASE = 'http://127.0.0.1:8000';

const ExportButton = ({ disabled = false, variant = 'primary' }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState('');
  const [exportSuccess, setExportSuccess] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    setExportError('');
    setExportSuccess(false);

    try {
      const response = await fetch(`${API_BASE}/export/excel`, {
        method: 'GET',
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al exportar');
      }

      // Obtener el blob del archivo
      const blob = await response.blob();
      
      // Crear URL temporal para descargar
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Extraer nombre del archivo del header si existe
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'analisis_financiero.xlsx';
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      
      // Limpiar
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setExportSuccess(true);
      
      // Limpiar mensaje de éxito después de 3 segundos
      setTimeout(() => {
        setExportSuccess(false);
      }, 3000);

    } catch (error) {
      console.error('Error exportando:', error);
      setExportError(error.message || 'Error al exportar el archivo');
      
      // Limpiar mensaje de error después de 5 segundos
      setTimeout(() => {
        setExportError('');
      }, 5000);
    } finally {
      setIsExporting(false);
    }
  };

  const getButtonClass = () => {
    let baseClass = 'export-button';
    if (variant === 'secondary') baseClass += ' export-button-secondary';
    if (variant === 'outline') baseClass += ' export-button-outline';
    if (disabled || isExporting) baseClass += ' export-button-disabled';
    return baseClass;
  };

  return (
    <div className="export-button-container">
      <button
        className={getButtonClass()}
        onClick={handleExport}
        disabled={disabled || isExporting}
        title="Exportar análisis completo a Excel"
      >
        {isExporting ? (
          <>
            <span className="export-spinner"></span>
            <span>Exportando...</span>
          </>
        ) : (
          <>
            <svg 
              width="20" 
              height="20" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            <span>Exportar a Excel</span>
          </>
        )}
      </button>

      {/* Mensaje de éxito */}
      {exportSuccess && (
        <div className="export-message export-success">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
          </svg>
          <span>Archivo exportado exitosamente</span>
        </div>
      )}

      {/* Mensaje de error */}
      {exportError && (
        <div className="export-message export-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <span>{exportError}</span>
        </div>
      )}
    </div>
  );
};

export default ExportButton;