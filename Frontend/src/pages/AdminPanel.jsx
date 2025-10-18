import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './AdminPanel.css';

const AdminPanel = () => {
  const { api } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'client',
    is_active: true
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/users/');
      setUsers(response.data);
    } catch (err) {
      setError('Error cargando usuarios');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      setError('');
      await api.post('/api/users/', formData);
      setSuccess('Usuario creado exitosamente');
      setShowModal(false);
      resetForm();
      fetchUsers();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error creando usuario');
    }
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();
    try {
      setError('');
      const updateData = { ...formData };
      delete updateData.username;
      if (!updateData.password) delete updateData.password;
      
      await api.put(`/api/users/${editingUser.id}`, updateData);
      setSuccess('Usuario actualizado exitosamente');
      setShowModal(false);
      setEditingUser(null);
      resetForm();
      fetchUsers();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error actualizando usuario');
    }
  };

  const handleDeleteUser = async (userId, username) => {
    if (!window.confirm(`¿Estás seguro de eliminar al usuario ${username}?`)) {
      return;
    }

    try {
      await api.delete(`/api/users/${userId}`);
      setSuccess('Usuario eliminado exitosamente');
      fetchUsers();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error eliminando usuario');
    }
  };

  const openCreateModal = () => {
    resetForm();
    setEditingUser(null);
    setShowModal(true);
  };

  const openEditModal = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      role: user.role,
      is_active: user.is_active
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: 'client',
      is_active: true
    });
    setError('');
  };

  const getRoleBadge = (role) => {
    return role === 'admin' ? (
      <span className="badge badge-admin">Admin</span>
    ) : (
      <span className="badge badge-client">Cliente</span>
    );
  };

  const getStatusBadge = (isActive) => {
    return isActive ? (
      <span className="badge badge-active">Activo</span>
    ) : (
      <span className="badge badge-inactive">Inactivo</span>
    );
  };

  if (loading && users.length === 0) {
    return (
      <div className="admin-panel">
        <div className="loading">Cargando usuarios...</div>
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <div>
          <h1>Gestión de Usuarios</h1>
          <p>Administra los usuarios del sistema</p>
        </div>
        <button className="btn-primary" onClick={openCreateModal}>
          + Nuevo Usuario
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
          <button onClick={() => setError('')}>×</button>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          {success}
          <button onClick={() => setSuccess('')}>×</button>
        </div>
      )}

      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario</th>
              <th>Email</th>
              <th>Nombre</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Último acceso</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td><strong>{user.username}</strong></td>
                <td>{user.email}</td>
                <td>{user.first_name || user.last_name ? `${user.first_name || ''} ${user.last_name || ''}` : '-'}</td>
                <td>{getRoleBadge(user.role)}</td>
                <td>{getStatusBadge(user.is_active)}</td>
                <td>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Nunca'}</td>
                <td>
                  <div className="action-buttons">
                    <button 
                      className="btn-edit"
                      onClick={() => openEditModal(user)}
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button 
                      className="btn-delete"
                      onClick={() => handleDeleteUser(user.id, user.username)}
                      title="Eliminar"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingUser ? 'Editar Usuario' : 'Crear Usuario'}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>

            <form onSubmit={editingUser ? handleUpdateUser : handleCreateUser}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Usuario *</label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    required
                    disabled={editingUser !== null}
                    placeholder="nombre_usuario"
                  />
                </div>

                <div className="form-group">
                  <label>Email *</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    placeholder="usuario@ejemplo.com"
                  />
                </div>

                <div className="form-group">
                  <label>Contraseña {editingUser ? '' : '*'}</label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required={!editingUser}
                    placeholder={editingUser ? 'Dejar vacío para no cambiar' : 'Mínimo 6 caracteres'}
                  />
                </div>

                <div className="form-group">
                  <label>Nombre</label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    placeholder="Nombre"
                  />
                </div>

                <div className="form-group">
                  <label>Apellido</label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    placeholder="Apellido"
                  />
                </div>

                <div className="form-group">
                  <label>Rol *</label>
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="client">Cliente</option>
                    <option value="admin">Administrador</option>
                  </select>
                </div>

                <div className="form-group checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      name="is_active"
                      checked={formData.is_active}
                      onChange={handleInputChange}
                    />
                    <span>Usuario activo</span>
                  </label>
                </div>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  {editingUser ? 'Actualizar' : 'Crear'} Usuario
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="admin-stats">
        <div className="stat-card">
          <h3>{users.length}</h3>
          <p>Usuarios totales</p>
        </div>
        <div className="stat-card">
          <h3>{users.filter(u => u.role === 'admin').length}</h3>
          <p>Administradores</p>
        </div>
        <div className="stat-card">
          <h3>{users.filter(u => u.role === 'client').length}</h3>
          <p>Clientes</p>
        </div>
        <div className="stat-card">
          <h3>{users.filter(u => u.is_active).length}</h3>
          <p>Activos</p>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;