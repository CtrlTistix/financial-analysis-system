import React, { useState, useRef, useEffect } from 'react';

const ChatWindow = ({ 
  isOpen, 
  onClose, 
  messages, 
  onSendMessage, 
  onFileUpload,
  isFloating = true 
}) => {
  const [userInput, setUserInput] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const [isFileDragging, setIsFileDragging] = useState(false);
  
  const chatRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Drag & drop de archivos
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('📥 Drag Enter');
    
    // Verificar si hay archivos
    if (e.dataTransfer && e.dataTransfer.types && e.dataTransfer.types.includes('Files')) {
      setIsFileDragging(true);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    // Esto es CRÍTICO para que funcione el drop
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Solo ocultar si realmente salimos del área del chat
    const rect = chatRef.current?.getBoundingClientRect();
    if (rect) {
      const isOutside = (
        e.clientX < rect.left ||
        e.clientX > rect.right ||
        e.clientY < rect.top ||
        e.clientY > rect.bottom
      );
      
      if (isOutside) {
        console.log('📤 Drag Leave');
        setIsFileDragging(false);
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('📍 Drop detected!');
    setIsFileDragging(false);

    const files = e.dataTransfer.files;
    console.log('Files dropped:', files.length);
    
    if (files && files.length > 0) {
      const file = files[0];
      console.log('File name:', file.name);
      console.log('File type:', file.type);
      
      if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        console.log('✅ Archivo válido, procesando...');
        onFileUpload(file);
      } else {
        console.log('❌ Tipo de archivo no válido');
        alert('Por favor, arrastra un archivo Excel (.xlsx o .xls)');
      }
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log('Archivo seleccionado:', file.name);
      onFileUpload(file);
    }
  };

  const handleSend = () => {
    if (userInput.trim()) {
      onSendMessage(userInput);
      setUserInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  const chatClassName = `${isFloating ? 'chat-floating' : 'chat-sidebar'} ${isMinimized ? 'minimized' : ''}`;

  return (
    <div 
      ref={chatRef}
      className={chatClassName}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="chat-header">
        <div className="chat-header-title">
          <h3>Asistente de Análisis</h3>
          {!isMinimized && <p>Arrastra Excel o usa el botón</p>}
        </div>
        <div className="chat-controls">
          {isFloating && (
            <button 
              className="chat-control-btn"
              onClick={() => setIsMinimized(!isMinimized)}
              title={isMinimized ? "Maximizar" : "Minimizar"}
              style={{ fontSize: '18px', lineHeight: 1 }}
            >
              {isMinimized ? '⬜' : '➖'}
            </button>
          )}
          <button 
            className="chat-control-btn"
            onClick={onClose}
            title="Cerrar"
            style={{ fontSize: '18px', lineHeight: 1 }}
          >
            ✕
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {isFileDragging && (
            <div className="file-drop-overlay">
              <div className="file-drop-content">
                <div style={{ fontSize: '48px', marginBottom: '1rem' }}>📄</div>
                <h4>Suelta tu archivo Excel aquí</h4>
                <p>Formatos: .xlsx, .xls</p>
              </div>
            </div>
          )}

          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="chat-empty-state">
                <div style={{ fontSize: '48px', marginBottom: '1rem' }}>📊</div>
                <h4>¡Comienza tu análisis!</h4>
                <p>Arrastra un archivo Excel aquí</p>
                <p style={{ marginTop: '1rem' }}>O usa el botón:</p>
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    marginTop: '1rem',
                    padding: '0.75rem 1.5rem',
                    background: 'linear-gradient(135deg, #1E88E5, #0D47A1)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  📁 Seleccionar archivo
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                />
              </div>
            ) : (
              <>
                {messages.map((message, index) => (
                  <div key={index} className={`message ${message.type}`}>
                    <div className="message-content">
                      {message.text}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          <div className="chat-input">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu pregunta..."
              disabled={isFileDragging}
            />
            <button onClick={handleSend} disabled={!userInput.trim()}>
              ➤
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ChatWindow;