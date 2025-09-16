import React, { useState, useRef } from 'react';

const DocumentManager = ({ 
  userId, 
  documents, 
  selectedDocuments, 
  setSelectedDocuments, 
  onDocumentsChange 
}) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [fileNames, setFileNames] = useState({});
  const [showRenameSection, setShowRenameSection] = useState(false);
  const [status, setStatus] = useState({ message: '', type: '' });
  const fileInputRef = useRef(null);

  const showStatus = (message, type = 'info') => {
    setStatus({ message, type });
    setTimeout(() => setStatus({ message: '', type: '' }), 3000);
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    handleFiles(files);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    const files = Array.from(event.dataTransfer.files);
    handleFiles(files);
  };

  const handleFiles = (files) => {
    const validFiles = files.filter(file => {
      const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
      return validTypes.includes(file.type);
    });

    if (validFiles.length !== files.length) {
      showStatus('Some files were skipped. Only JPG, PNG, and PDF files are allowed.', 'warning');
    }

    if (validFiles.length > 0) {
      setUploadedFiles(validFiles);
      setShowRenameSection(true);
      showStatus(`${validFiles.length} file(s) ready for upload`, 'success');
    }
  };

  const updateFileName = (index, customName) => {
    setFileNames(prev => ({
      ...prev,
      [index]: customName
    }));
  };

  const uploadFiles = async () => {
    if (uploadedFiles.length === 0) return;

    for (let i = 0; i < uploadedFiles.length; i++) {
      await uploadFile(uploadedFiles[i], i);
    }

    setUploadedFiles([]);
    setFileNames({});
    setShowRenameSection(false);
    onDocumentsChange();
  };

  const uploadFile = async (file, index) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('file', file);

    if (fileNames[index]) {
      formData.append('custom_filename', fileNames[index]);
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/upload-document', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        showStatus(`Successfully uploaded: ${result.file_name}`, 'success');
      } else {
        const error = await response.json();
        showStatus(`Failed to upload ${file.name}: ${error.detail}`, 'error');
      }
    } catch (error) {
      showStatus(`Error uploading ${file.name}: ${error.message}`, 'error');
    }
  };

  const toggleDocumentSelection = (docId) => {
    const newSelected = new Set(selectedDocuments);
    if (newSelected.has(docId)) {
      newSelected.delete(docId);
      showStatus('Document deselected for analysis', 'info');
    } else {
      newSelected.add(docId);
      showStatus('Document selected for analysis', 'success');
    }
    setSelectedDocuments(newSelected);
  };

  const deleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;

    try {
      const response = await fetch(`http://127.0.0.1:8000/user-documents/${userId}/${docId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        showStatus('Document deleted successfully', 'success');
        onDocumentsChange();
        // Remove from selected if it was selected
        if (selectedDocuments.has(docId)) {
          const newSelected = new Set(selectedDocuments);
          newSelected.delete(docId);
          setSelectedDocuments(newSelected);
        }
      } else {
        const error = await response.json();
        showStatus(`Failed to delete document: ${error.detail}`, 'error');
      }
    } catch (error) {
      showStatus(`Error deleting document: ${error.message}`, 'error');
    }
  };

  return (
    <div className="sidebar">
      <h3>📋 Document Management</h3>
      
      {status.message && (
        <div className={`status-message ${status.type}`}>
          {status.message}
        </div>
      )}
      
      <div className="upload-section">
        <div 
          className="upload-area"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-icon">📁</div>
          <p>Drop files here or click to browse</p>
          <small>Supports: JPG, PNG, PDF</small>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        
        {showRenameSection && (
          <div className="file-rename-section show">
            <h4>Rename Files (Optional)</h4>
            {uploadedFiles.map((file, index) => (
              <div key={index} className="rename-input">
                <label>{file.name}:</label>
                <input
                  type="text"
                  placeholder="Enter custom name..."
                  value={fileNames[index] || ''}
                  onChange={(e) => updateFileName(index, e.target.value)}
                />
              </div>
            ))}
            <button className="upload-btn" onClick={uploadFiles}>
              📤 Upload Files
            </button>
          </div>
        )}
      </div>
      
      <div className="documents-section">
        <h4>Your Documents ({documents.length})</h4>
        <div className="documents-list">
          {documents.length === 0 ? (
            <p className="no-documents">No documents uploaded yet</p>
          ) : (
            documents.map((doc) => {
              const docId = doc.document_id;
              const isSelected = selectedDocuments.has(docId);
              
              return (
                <div key={docId} className="document-item">
                  <div className="document-info">
                    <strong>{doc.file_name || 'Document'}</strong><br />
                    <small>
                      Uploaded: {doc.upload_date ? new Date(doc.upload_date).toLocaleString() : 'Unknown'}<br />
                      Chunks: {doc.chunk_count}
                    </small>
                  </div>
                  <div className="document-actions">
                    <button
                      className={`select-btn ${isSelected ? 'selected' : ''}`}
                      onClick={() => toggleDocumentSelection(docId)}
                      title={isSelected ? 'Deselect document' : 'Select document for analysis'}
                    >
                      {isSelected ? '✓ Selected' : 'Select'}
                    </button>
                    <button
                      className="delete-btn"
                      onClick={() => deleteDocument(docId)}
                      title="Delete document"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
        
        {selectedDocuments.size > 0 && (
          <div className="selected-summary">
            <strong>Selected for Analysis: {selectedDocuments.size}</strong>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentManager;
