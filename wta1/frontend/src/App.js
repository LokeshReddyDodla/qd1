import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import DocumentManager from './components/DocumentManager';
import Header from './components/Header';

function App() {
  // Persist user ID across refreshes to keep documents associated correctly
  const [userId] = useState(() => {
    const stored = window.localStorage.getItem('wl_user_id');
    if (stored) return stored;
    const id = `user_${Date.now()}`;
    window.localStorage.setItem('wl_user_id', id);
    return id;
  });
  const [documents, setDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState(new Set());

  const loadDocuments = useCallback(async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/user-documents/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  }, [userId]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  return (
    <div className="App">
      <Header />
      <div className="main-content">
        <DocumentManager 
          userId={userId}
          documents={documents}
          selectedDocuments={selectedDocuments}
          setSelectedDocuments={setSelectedDocuments}
          onDocumentsChange={loadDocuments}
        />
        <ChatInterface 
          userId={userId}
          selectedDocuments={selectedDocuments}
        />
      </div>
    </div>
  );
}

export default App;
