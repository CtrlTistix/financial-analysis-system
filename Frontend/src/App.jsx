import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import FileUpload from './components/FileUpload';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [financialData, setFinancialData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Cargar datos de prueba al inicio
  useEffect(() => {
    fetchTestData();
  }, []);

  const fetchTestData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/test-data`);
      setFinancialData(response.data);
      setError('');
    } catch (err) {
      setError('Error cargando datos de prueba');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setFinancialData(response.data);
      setError('');
    } catch (err) {
      setError('Error procesando archivo: ' + (err.response?.data?.detail || err.message));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📊 Sistema de Análisis Financiero con IA</h1>
      </header>

      <main>
        {error && <div className="error-message">{error}</div>}
        
        <FileUpload onFileUpload={handleFileUpload} loading={loading} />
        
        {financialData && (
          <Dashboard data={financialData} />
        )}
      </main>
    </div>
  );
}

export default App;