import React, { useState } from 'react';
import './Requirements.css';

const Requirements = () => {
  const [activeTab, setActiveTab] = useState('backend');

  const requirements = {
    backend: {
      title: "Backend - Python/FastAPI",
      icon: "🐍",
      packages: [
        { name: "fastapi", version: "0.104.1", description: "Framework web moderno y rápido para construir APIs" },
        { name: "uvicorn", version: "0.24.0", description: "Servidor ASGI de alto rendimiento" },
        { name: "sqlalchemy", version: "2.0.23", description: "ORM para Python" },
        { name: "psycopg2-binary", version: "2.9.7", description: "Adaptador PostgreSQL para Python" },
        { name: "pandas", version: "1.5.3", description: "Análisis y manipulación de datos" },
        { name: "numpy", version: "1.24.3", description: "Computación numérica" },
        { name: "openpyxl", version: "3.1.2", description: "Lectura/escritura de archivos Excel" },
        { name: "python-multipart", version: "0.0.6", description: "Manejo de formularios multipart" },
        { name: "python-jose[cryptography]", version: "3.3.0", description: "Implementación de JWT" },
        { name: "passlib[bcrypt]", version: "1.7.4", description: "Hash de contraseñas" },
        { name: "python-dotenv", version: "1.0.0", description: "Variables de entorno desde .env" },
        { name: "openai", version: ">=1.0.0", description: "Cliente para API de OpenAI/GPT" }
      ]
    },
    frontend: {
      title: "Frontend - React",
      icon: "⚛️",
      packages: [
        { name: "react", version: "^18.2.0", description: "Biblioteca para construir interfaces de usuario" },
        { name: "react-dom", version: "^18.2.0", description: "Renderizado de React en el DOM" },
        { name: "chart.js", version: "^4.4.0", description: "Biblioteca de gráficos JavaScript" },
        { name: "react-chartjs-2", version: "^5.2.0", description: "Componentes React para Chart.js" },
        { name: "vite", version: "^5.0.0", description: "Build tool rápido para desarrollo" }
      ]
    },
    infrastructure: {
      title: "Infraestructura",
      icon: "🐳",
      services: [
        { 
          name: "PostgreSQL", 
          version: "15", 
          description: "Base de datos relacional",
          config: "Usuario: admin, Puerto: 5432"
        },
        { 
          name: "Docker", 
          version: "latest", 
          description: "Contenedores para servicios",
          config: "docker-compose.yml incluido"
        },
        { 
          name: "Docker Compose", 
          version: "v2.x", 
          description: "Orquestación de contenedores",
          config: "Backend + DB + Network"
        }
      ]
    },
    apis: {
      title: "APIs Externas",
      icon: "🔌",
      services: [
        { 
          name: "OpenAI API", 
          version: "GPT-3.5-turbo", 
          description: "Chatbot de análisis financiero",
          required: "API Key necesaria",
          env: "OPENAI_API_KEY"
        },
        { 
          name: "Anthropic API", 
          version: "Claude", 
          description: "Alternativa para chatbot (opcional)",
          required: "API Key opcional",
          env: "ANTHROPIC_API_KEY"
        }
      ]
    },
    system: {
      title: "Requerimientos del Sistema",
      icon: "💻",
      requirements: [
        { 
          category: "Sistema Operativo",
          items: ["Windows 10/11", "macOS 10.15+", "Linux (Ubuntu 20.04+)"]
        },
        { 
          category: "RAM",
          items: ["Mínimo: 4GB", "Recomendado: 8GB o más"]
        },
        { 
          category: "Espacio en Disco",
          items: ["Mínimo: 2GB", "Recomendado: 5GB"]
        },
        { 
          category: "Software Requerido",
          items: ["Docker Desktop", "Git", "Node.js 18+ (para desarrollo)", "Python 3.11+ (para desarrollo)"]
        },
        { 
          category: "Navegador Web",
          items: ["Chrome 90+", "Firefox 88+", "Safari 14+", "Edge 90+"]
        }
      ]
    }
  };

  const installCommands = {
    backend: `# Instalación Backend
cd backend
pip install -r requirements.txt

# O con Docker
docker-compose build backend`,
    frontend: `# Instalación Frontend
cd frontend
npm install

# O con yarn
yarn install`,
    infrastructure: `# Levantar servicios con Docker
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down`,
    full: `# Instalación Completa del Proyecto

# 1. Clonar repositorio
git clone https://github.com/CtrlTistix/financial-analysis-system.git
cd financial-analysis-system

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 3. Levantar con Docker
cd backend
docker-compose up -d

# 4. Instalar frontend (en otra terminal)
cd ../frontend
npm install
npm run dev

# 5. Acceder a la aplicación
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Docs API: http://localhost:8000/docs`
  };

  return (
    <div className="requirements-container">
      <div className="requirements-header">
        <h1>📋 Requerimientos del Sistema</h1>
        <p>Documentación completa de dependencias y configuración</p>
      </div>

      {/* Tabs Navigation */}
      <div className="tabs-navigation">
        <button 
          className={`tab-btn ${activeTab === 'backend' ? 'active' : ''}`}
          onClick={() => setActiveTab('backend')}
        >
          🐍 Backend
        </button>
        <button 
          className={`tab-btn ${activeTab === 'frontend' ? 'active' : ''}`}
          onClick={() => setActiveTab('frontend')}
        >
          ⚛️ Frontend
        </button>
        <button 
          className={`tab-btn ${activeTab === 'infrastructure' ? 'active' : ''}`}
          onClick={() => setActiveTab('infrastructure')}
        >
          🐳 Infraestructura
        </button>
        <button 
          className={`tab-btn ${activeTab === 'apis' ? 'active' : ''}`}
          onClick={() => setActiveTab('apis')}
        >
          🔌 APIs
        </button>
        <button 
          className={`tab-btn ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => setActiveTab('system')}
        >
          💻 Sistema
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {/* Backend Packages */}
        {activeTab === 'backend' && (
          <div className="content-section">
            <h2>{requirements.backend.icon} {requirements.backend.title}</h2>
            <div className="packages-grid">
              {requirements.backend.packages.map((pkg, index) => (
                <div key={index} className="package-card">
                  <div className="package-header">
                    <h3>{pkg.name}</h3>
                    <span className="version-badge">{pkg.version}</span>
                  </div>
                  <p className="package-description">{pkg.description}</p>
                </div>
              ))}
            </div>
            <div className="install-section">
              <h3>📦 Instalación</h3>
              <pre className="code-block">{installCommands.backend}</pre>
            </div>
          </div>
        )}

        {/* Frontend Packages */}
        {activeTab === 'frontend' && (
          <div className="content-section">
            <h2>{requirements.frontend.icon} {requirements.frontend.title}</h2>
            <div className="packages-grid">
              {requirements.frontend.packages.map((pkg, index) => (
                <div key={index} className="package-card">
                  <div className="package-header">
                    <h3>{pkg.name}</h3>
                    <span className="version-badge">{pkg.version}</span>
                  </div>
                  <p className="package-description">{pkg.description}</p>
                </div>
              ))}
            </div>
            <div className="install-section">
              <h3>📦 Instalación</h3>
              <pre className="code-block">{installCommands.frontend}</pre>
            </div>
          </div>
        )}

        {/* Infrastructure */}
        {activeTab === 'infrastructure' && (
          <div className="content-section">
            <h2>{requirements.infrastructure.icon} {requirements.infrastructure.title}</h2>
            <div className="packages-grid">
              {requirements.infrastructure.services.map((service, index) => (
                <div key={index} className="package-card infrastructure-card">
                  <div className="package-header">
                    <h3>{service.name}</h3>
                    <span className="version-badge">{service.version}</span>
                  </div>
                  <p className="package-description">{service.description}</p>
                  {service.config && (
                    <div className="config-info">
                      <strong>Configuración:</strong> {service.config}
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div className="install-section">
              <h3>🚀 Comandos Docker</h3>
              <pre className="code-block">{installCommands.infrastructure}</pre>
            </div>
          </div>
        )}

        {/* APIs */}
        {activeTab === 'apis' && (
          <div className="content-section">
            <h2>{requirements.apis.icon} {requirements.apis.title}</h2>
            <div className="packages-grid">
              {requirements.apis.services.map((service, index) => (
                <div key={index} className="package-card api-card">
                  <div className="package-header">
                    <h3>{service.name}</h3>
                    <span className="version-badge">{service.version}</span>
                  </div>
                  <p className="package-description">{service.description}</p>
                  <div className="api-details">
                    <div className="api-requirement">
                      <strong>Requerido:</strong> {service.required}
                    </div>
                    <div className="api-env">
                      <strong>Variable:</strong> <code>{service.env}</code>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="install-section">
              <h3>🔑 Configuración de API Keys</h3>
              <pre className="code-block">{`# Archivo .env
OPENAI_API_KEY=tu_api_key_aqui
ANTHROPIC_API_KEY=tu_api_key_aqui (opcional)
DATABASE_URL=postgresql://admin:password@db:5432/financial_db`}</pre>
            </div>
          </div>
        )}

        {/* System Requirements */}
        {activeTab === 'system' && (
          <div className="content-section">
            <h2>{requirements.system.icon} {requirements.system.title}</h2>
            <div className="system-requirements">
              {requirements.system.requirements.map((req, index) => (
                <div key={index} className="requirement-section">
                  <h3>{req.category}</h3>
                  <ul className="requirement-list">
                    {req.items.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
            <div className="install-section">
              <h3>🚀 Instalación Completa</h3>
              <pre className="code-block">{installCommands.full}</pre>
            </div>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="stats-section">
        <div className="stat-card">
          <h4>📦 Total Dependencias Backend</h4>
          <div className="stat-number">{requirements.backend.packages.length}</div>
        </div>
        <div className="stat-card">
          <h4>⚛️ Total Dependencias Frontend</h4>
          <div className="stat-number">{requirements.frontend.packages.length}</div>
        </div>
        <div className="stat-card">
          <h4>🐳 Servicios Docker</h4>
          <div className="stat-number">{requirements.infrastructure.services.length}</div>
        </div>
        <div className="stat-card">
          <h4>🔌 APIs Externas</h4>
          <div className="stat-number">{requirements.apis.services.length}</div>
        </div>
      </div>
    </div>
  );
};

export default Requirements;