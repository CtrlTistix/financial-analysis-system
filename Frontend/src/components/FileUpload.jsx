import React, { useState } from 'react';

const FileUpload = ({ onFileUpload, loading }) => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  return (
    <div className="file-upload">
      <h2>📤 Cargar Estados Financieros</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".xlsx, .xls"
          onChange={handleFileChange}
          disabled={loading}
        />
        <button type="submit" disabled={!selectedFile || loading}>
          {loading ? 'Procesando...' : 'Analizar Archivo'}
        </button>
      </form>
      <p>Formato esperado: Excel con columnas como Año, Activo_Corriente, Pasivo_Corriente, etc.</p>
    </div>
  );
};

export default FileUpload;