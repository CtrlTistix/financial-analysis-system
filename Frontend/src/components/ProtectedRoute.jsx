/**
 * Protected Route Component
 * Componente para proteger rutas que requieren autenticación
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  // Mostrar loading mientras se verifica la autenticación
  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner-large"></div>
        <p>Cargando...</p>
      </div>
    );
  }

  // Si no está autenticado, redirigir a login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Si la ruta es solo para admin y el usuario no es admin
  if (adminOnly && user?.role !== 'admin') {
    return (
      <div className="unauthorized-container">
        <h1>❌ Acceso Denegado</h1>
        <p>No tienes permisos para acceder a esta página.</p>
        <p>Se requiere rol de <strong>Administrador</strong>.</p>
        <button onClick={() => window.history.back()}>
          Volver
        </button>
      </div>
    );
  }

  // Si todo está bien, renderizar el contenido
  return children;
};

export default ProtectedRoute;