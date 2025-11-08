/**
 * Página para establecer nueva contraseña
 * El usuario llega aquí desde el link del email
 */
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';
import './ResetPassword.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ResetPassword = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Validar token al cargar
  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        setError('Token de restablecimiento no válido');
        setValidating(false);
        return;
      }

      try {
        const response = await axios.post(
          `${API_URL}/api/auth/validate-reset-token`,
          { token }
        );

        if (response.status === 200) {
          setTokenValid(true);
        }
      } catch (err) {
        console.error('Error validating token:', err);
        setError('El enlace de restablecimiento ha expirado o no es válido');
        setTokenValid(false);
      } finally {
        setValidating(false);
      }
    };

    validateToken();
  }, [token]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validaciones
    if (!formData.password || !formData.confirmPassword) {
      setError('Por favor completa todos los campos');
      return;
    }

    if (formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/auth/reset-password`, {
        token: token,
        new_password: formData.password,
      });

      if (response.status === 200) {
        setSuccess(true);
        // Redirigir al login después de 3 segundos
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      }
    } catch (err) {
      console.error('Error resetting password:', err);
      setError(
        err.response?.data?.detail ||
          'Error al restablecer contraseña. Intenta nuevamente.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Mostrando validación de token
  if (validating) {
    return (
      <div className="reset-password-container">
        <div className="reset-password-card">
          <div className="loading-state">
            <div className="spinner-large"></div>
            <p>Validando enlace...</p>
          </div>
        </div>
      </div>
    );
  }

  // Token inválido
  if (!tokenValid) {
    return (
      <div className="reset-password-container">
        <div className="reset-password-card error-card">
          <div className="error-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" fill="#ef4444" opacity="0.2" />
              <path
                d="M15 9l-6 6m0-6l6 6"
                stroke="#ef4444"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </div>

          <h1>Enlace no válido</h1>
          <p className="error-text">{error}</p>

          <div className="error-actions">
            <Link to="/forgot-password" className="btn-secondary">
              Solicitar nuevo enlace
            </Link>
            <Link to="/login" className="btn-primary">
              Ir al Login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Éxito
  if (success) {
    return (
      <div className="reset-password-container">
        <div className="reset-password-card success-card">
          <div className="success-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" fill="#10b981" opacity="0.2" />
              <path
                d="M9 12l2 2 4-4"
                stroke="#10b981"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>

          <h1>¡Contraseña actualizada!</h1>
          <p className="success-message">
            Tu contraseña ha sido restablecida exitosamente.
          </p>
          <p className="redirect-message">
            Serás redirigido al login en unos segundos...
          </p>

          <Link to="/login" className="btn-primary">
            Ir al Login ahora
          </Link>
        </div>
      </div>
    );
  }

  // Formulario de nueva contraseña
  return (
    <div className="reset-password-container">
      <div className="reset-password-card">
        <div className="reset-password-header">
          <h1>Crear Nueva Contraseña</h1>
          <p>Ingresa tu nueva contraseña</p>
        </div>

        <form onSubmit={handleSubmit} className="reset-password-form">
          {error && (
            <div className="error-message">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">Nueva Contraseña</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Mínimo 6 caracteres"
              disabled={loading}
              autoFocus
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmar Contraseña</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Repite la contraseña"
              disabled={loading}
              required
            />
          </div>

          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Actualizando...
              </>
            ) : (
              'Restablecer Contraseña'
            )}
          </button>
        </form>

        <div className="reset-password-footer">
          <Link to="/login">← Volver al login</Link>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;