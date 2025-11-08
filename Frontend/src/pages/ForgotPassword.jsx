/**
 * Página para solicitar restablecimiento de contraseña
 * El usuario ingresa su email y recibe un link de reset
 */
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './ForgotPassword.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validación básica
    if (!email || !email.includes('@')) {
      setError('Por favor ingresa un email válido');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(
        `${API_URL}/api/auth/forgot-password`,
        { email }
      );

      if (response.status === 200) {
        setSubmitted(true);
      }
    } catch (err) {
      console.error('Error requesting password reset:', err);
      // No mostramos error específico por seguridad
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="forgot-password-container">
        <div className="forgot-password-card success-card">
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

          <h1>Revisa tu email</h1>
          <p className="success-message">
            Si existe una cuenta con el email <strong>{email}</strong>, recibirás
            un enlace para restablecer tu contraseña.
          </p>

          <div className="info-box">
            <p>
              <strong>📧 No recibes el email?</strong>
            </p>
            <ul>
              <li>Revisa tu carpeta de spam</li>
              <li>Verifica que el email sea correcto</li>
              <li>El enlace expira en 1 hora</li>
            </ul>
          </div>

          <Link to="/login" className="btn-back">
            Volver al Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="forgot-password-container">
      <div className="forgot-password-card">
        <div className="forgot-password-header">
          <h1>¿Olvidaste tu contraseña?</h1>
          <p>
            Ingresa tu email y te enviaremos un enlace para restablecerla
          </p>
        </div>

        <form onSubmit={handleSubmit} className="forgot-password-form">
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
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@email.com"
              disabled={loading}
              autoFocus
              required
            />
          </div>

          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Enviando...
              </>
            ) : (
              'Enviar enlace de restablecimiento'
            )}
          </button>
        </form>

        <div className="forgot-password-footer">
          <Link to="/login">← Volver al login</Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;