import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

// Define the backend API URL. This is where your FastAPI server is running.
const API_URL = 'http://localhost:8000';

function App() {
    // State for user profile data
    const [userProfile, setUserProfile] = useState({
        age: '35',
        fitness_level: 'beginner',
        conditions: 'Hypertension, High Cholesterol',
        goals: 'Lose weight and improve cardiovascular health',
        food_preferences: 'vegetarian, low sodium'
    });

    // State for document upload
    const [selectedFile, setSelectedFile] = useState(null);
    const [documentName, setDocumentName] = useState('');
    const [uploadProgress, setUploadProgress] = useState(null);
    const [documents, setDocuments] = useState([]);
    const [selectedDocumentId, setSelectedDocumentId] = useState('');

    // State for tool-specific inputs
    const [docQAInput, setDocQAInput] = useState('');
    const [healthSearchInput, setHealthSearchInput] = useState('');

    // State for displaying results and loading status
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);

    // State for document selection in profile extraction
    const [selectedDocumentsForProfile, setSelectedDocumentsForProfile] = useState([]);

    // Auto-extract profile information from uploaded documents
    const autoExtractProfile = async (useSelectedDocs = false) => {
        if (documents.length === 0) {
            alert('Please upload documents first to extract profile information.');
            return;
        }

        if (useSelectedDocs && selectedDocumentsForProfile.length === 0) {
            alert('Please select at least one document to extract profile information from.');
            return;
        }

        setLoading(true);
        try {
            // Build URL with selected document IDs if using selection
            let url = `${API_URL}/extract-profile/`;
            if (useSelectedDocs && selectedDocumentsForProfile.length > 0) {
                const documentParams = selectedDocumentsForProfile.map(id => `document_ids=${id}`).join('&');
                url += `?${documentParams}`;
            }

            const response = await fetch(url);
            if (response.ok) {
                const extractedProfile = await response.json();
                
                if (extractedProfile.message) {
                    alert(extractedProfile.message);
                    return;
                }
                
                // Update profile with extracted information
                setUserProfile(prevProfile => {
                    const updatedProfile = {
                        age: extractedProfile.age || prevProfile.age,
                        fitness_level: extractedProfile.fitness_level || prevProfile.fitness_level,
                        conditions: extractedProfile.conditions || prevProfile.conditions,
                        goals: extractedProfile.goals || prevProfile.goals,
                        food_preferences: extractedProfile.food_preferences || prevProfile.food_preferences
                    };
                    
                    // Show success message with extracted info
                    const extractedFields = [];
                    if (extractedProfile.age) extractedFields.push('age');
                    if (extractedProfile.conditions) extractedFields.push('conditions');
                    if (extractedProfile.goals) extractedFields.push('goals');
                    if (extractedProfile.food_preferences) extractedFields.push('food preferences');
                    
                    const docCount = useSelectedDocs ? selectedDocumentsForProfile.length : documents.length;
                    const docText = docCount === 1 ? 'document' : 'documents';
                    
                    if (extractedFields.length > 0) {
                        alert(`✅ Successfully extracted: ${extractedFields.join(', ')} from ${docCount} ${docText}!`);
                    } else {
                        alert(`ℹ️ No specific profile information could be extracted from the selected ${docText}. You can fill out the form manually.`);
                    }
                    
                    return updatedProfile;
                });
            } else {
                alert('Error extracting profile information. Please try again.');
            }
        } catch (error) {
            console.error('Error extracting profile:', error);
            alert('Error extracting profile information. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    };

    // Handle document deletion
    const handleDeleteDocument = async (documentId, documentName) => {
        if (!window.confirm(`Are you sure you want to delete "${documentName}"? This action cannot be undone.`)) {
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/delete-document/?document_id=${documentId}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                const result = await response.json();
                alert(`✅ ${result.message || `Successfully deleted "${documentName}"`}`);
                // Remove deleted document from selected documents for profile extraction
                setSelectedDocumentsForProfile(prev => prev.filter(id => id !== documentId));
                // Clear selected document for Q&A if it was the deleted one
                if (selectedDocumentId === documentId) {
                    setSelectedDocumentId('');
                }
                // Reload documents list
                await loadDocuments();
            } else {
                const errorData = await response.json();
                alert(`❌ Error deleting document: ${errorData.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error deleting document:', error);
            alert('❌ Error deleting document. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    };

    // Load available documents and auto-extract profile
    const loadDocuments = useCallback(async () => {
        try {
            const response = await fetch(`${API_URL}/documents/`);
            if (response.ok) {
                const data = await response.json();
                setDocuments(data.documents || []);
                
                // Only auto-extract if this is the initial load (not after deletion)
                if (data.documents && data.documents.length > 0 && documents.length === 0) {
                    await autoExtractProfile();
                }
            }
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    }, []);

    // Load documents on component mount
    useEffect(() => {
        loadDocuments();
    }, [loadDocuments]);

    // Handle file upload
    const handleFileUpload = async () => {
        if (!selectedFile) {
            alert('Please select a PDF file to upload.');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);
        if (documentName.trim()) {
            formData.append('document_name', documentName.trim());
        }

        setUploadProgress('Uploading and processing PDF...');
        setLoading(true);

        try {
            const response = await fetch(`${API_URL}/upload-pdf/`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                setUploadProgress(`✅ Success! Processed "${result.document_name}" with ${result.chunks_created} chunks.`);
                setSelectedFile(null);
                setDocumentName('');
                // Reload documents list
                await loadDocuments();
            } else {
                setUploadProgress(`❌ Error: ${result.detail}`);
            }
        } catch (error) {
            setUploadProgress(`❌ Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    // Handler to update user profile state
    const handleProfileChange = (e) => {
        const { name, value } = e.target;
        setUserProfile(prev => ({ ...prev, [name]: value }));
    };

    // Handle document selection for profile extraction
    const handleDocumentSelection = (documentId, isChecked) => {
        setSelectedDocumentsForProfile(prev => {
            if (isChecked) {
                return [...prev, documentId];
            } else {
                return prev.filter(id => id !== documentId);
            }
        });
    };

    // Select/deselect all documents for profile extraction
    const handleSelectAllDocuments = (selectAll) => {
        if (selectAll) {
            setSelectedDocumentsForProfile(documents.map(doc => doc.document_id));
        } else {
            setSelectedDocumentsForProfile([]);
        }
    };

    // Main function to call the backend API
    const callTool = async (toolName) => {
        setLoading(true);
        setResults(null);
        let endpoint = '';
        let requestBody = {};
        let displayTitle = '';

        try {
            // Prepare the request based on which tool was clicked
            switch (toolName) {
                case 'documentQA':
                    if (!docQAInput) throw new Error('Please enter a question for the Document Q&A tool.');
                    // Use the ask endpoint with proper query parameters
                    const queryParams = new URLSearchParams({ query: docQAInput });
                    if (selectedDocumentId) {
                        queryParams.append('document_id', selectedDocumentId);
                    }
                    endpoint = `/ask/?${queryParams.toString()}`;
                    requestBody = {}; // Empty body for POST request with query params
                    displayTitle = `Question: ${docQAInput}`;
                    break;
                
                case 'web_search':
                    if (!healthSearchInput) throw new Error('Please enter a query for the Health Search tool.');
                    endpoint = '/web-search/';
                    requestBody = { query: healthSearchInput };
                    displayTitle = `Search Query: ${healthSearchInput}`;
                    break;

                case 'recommendation_agent':
                    endpoint = '/recommendation-agent/';
                    requestBody = {
                        report_data: { summary: `User has conditions: ${userProfile.conditions}` },
                        user_profile: {
                           age: parseInt(userProfile.age),
                           conditions: userProfile.conditions.split(',').map(s => s.trim()).filter(Boolean),
                           fitness_level: userProfile.fitness_level
                        }
                    };
                    displayTitle = 'Personalized Health Recommendations';
                    break;

                case 'fitness_plan':
                    if (!userProfile.goals) throw new Error('Please enter your goals in the profile section.');
                    endpoint = '/create-fitness-plan/';
                    requestBody = {
                        user_profile: {
                            age: parseInt(userProfile.age),
                            fitness_level: userProfile.fitness_level
                        },
                        goals: userProfile.goals
                    };
                    displayTitle = `Fitness Plan For: ${userProfile.goals}`;
                    break;
                
                case 'meal_planner':
                    if (!userProfile.conditions) throw new Error('Please enter your health conditions in the profile section.');
                    endpoint = '/meal-planner/';
                    requestBody = {
                        user_profile: { age: parseInt(userProfile.age) },
                        health_conditions: userProfile.conditions.split(',').map(s => s.trim()).filter(Boolean),
                        food_preferences: userProfile.food_preferences.split(',').map(s => s.trim()).filter(Boolean)
                    };
                    displayTitle = `Meal Plan For: ${userProfile.conditions}`;
                    break;

                default:
                    throw new Error('Unknown tool');
            }

            // Make the API call to the backend
            const response = await fetch(`${API_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'API request failed');
            }

            const data = await response.json();
            setResults({ toolName, data, displayTitle });

        } catch (error) {
            setResults({ error: error.message });
        } finally {
            setLoading(false);
        }
    };

    // Helper function to render the results in a structured way
    const renderResults = () => {
        if (!results) return null;
        if (results.error) return <div className="answer-container" style={{borderColor: 'red'}}><strong>Error:</strong> {results.error}</div>;

        const { toolName, data, displayTitle } = results;
        let content = '';

        switch (toolName) {
            case 'documentQA':
                content = data.answer;
                // Show sources if available
                if (data.sources && data.sources.length > 0) {
                    content += '\n\n📚 Sources:\n';
                    data.sources.forEach((source, index) => {
                        content += `${index + 1}. ${source.content_preview}\n`;
                    });
                }
                break;
            case 'web_search':
                content = data.answer;
                break;
            case 'recommendation_agent':
                content = data.recommendations.map(r => `### ${r.title}\n${r.explanation}`).join('\n\n');
                break;
            case 'fitness_plan':
                content = data.fitness_plan;
                break;
            case 'meal_planner':
                content = data.meal_plan;
                break;
            default:
                content = JSON.stringify(data, null, 2);
        }

        return (
            <>
                <div className="question">{displayTitle}</div>
                <div className="answer-container">
                    {content}
                </div>
            </>
        );
    };

    return (
        <div className="container">
            <header className="header">
                <h1>AI Health Buddy</h1>
                <p>Upload your health documents and get personalized AI-powered insights.</p>
            </header>

            {/* Document Upload Section */}
            <div className="profile-container">
                <h2>📄 Upload Health Documents</h2>
                <p>Upload PDF documents (medical reports, research papers, etc.) to get personalized health insights.</p>
                
                <div className="upload-section">
                    <div className="form-group">
                        <label htmlFor="fileUpload">Select PDF File</label>
                        <input 
                            type="file" 
                            id="fileUpload"
                            accept=".pdf"
                            onChange={(e) => setSelectedFile(e.target.files[0])}
                        />
                    </div>
                    
                    <div className="form-group">
                        <label htmlFor="documentName">Document Name (Optional)</label>
                        <input 
                            type="text" 
                            id="documentName"
                            value={documentName}
                            onChange={(e) => setDocumentName(e.target.value)}
                            placeholder="Enter a custom name for this document"
                        />
                    </div>
                    
                    <button 
                        onClick={handleFileUpload} 
                        disabled={!selectedFile || loading}
                        className="upload-button"
                    >
                        {loading ? '⏳ Processing...' : '📤 Upload & Process PDF'}
                    </button>
                    
                    {uploadProgress && (
                        <div className={`upload-status ${uploadProgress.includes('Error') ? 'error' : 'success'}`}>
                            {uploadProgress}
                        </div>
                    )}
                </div>

                {/* Document Selection for Q&A */}
                {documents.length > 0 && (
                    <div className="document-selection">
                        <label htmlFor="documentSelect">Select Document for Q&A (Optional)</label>
                        <select 
                            id="documentSelect"
                            value={selectedDocumentId}
                            onChange={(e) => setSelectedDocumentId(e.target.value)}
                        >
                            <option value="">All Documents</option>
                            {documents.map(doc => (
                                <option key={doc.document_id} value={doc.document_id}>
                                    {doc.document_name} ({doc.chunk_count} chunks)
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>

            <div className="profile-container">
                <h2>Your Profile & Goals</h2>
                <p>Fill this out to get personalized results from the AI Health Tools below.</p>
                {documents.length > 0 && (
                    <p style={{color: '#4CAF50', fontSize: '14px', fontStyle: 'italic'}}>
                        📄 Profile information has been automatically extracted from your uploaded documents. You can edit any field or add additional information.
                    </p>
                )}
                
                {/* Document selection for profile extraction */}
                {documents.length > 0 && (
                    <div style={{
                        border: '1px solid #ddd',
                        borderRadius: '8px',
                        padding: '15px',
                        marginBottom: '15px',
                        backgroundColor: '#f9f9f9'
                    }}>
                        <h4 style={{marginTop: '0', marginBottom: '10px', color: '#333'}}>
                            📋 Select Documents for Profile Extraction
                        </h4>
                        
                        <div style={{marginBottom: '10px'}}>
                            <label style={{fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center'}}>
                                <input
                                    type="checkbox"
                                    checked={selectedDocumentsForProfile.length === documents.length && documents.length > 0}
                                    onChange={(e) => handleSelectAllDocuments(e.target.checked)}
                                    style={{marginRight: '8px'}}
                                />
                                <strong>Select All Documents ({documents.length})</strong>
                            </label>
                        </div>
                        
                        <div style={{maxHeight: '150px', overflowY: 'auto'}}>
                            {documents.map(doc => (
                                <div key={doc.document_id} style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                    fontSize: '14px',
                                    padding: '8px 0',
                                    borderBottom: '1px solid #eee'
                                }}>
                                    <label style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        cursor: 'pointer',
                                        flex: 1
                                    }}>
                                        <input
                                            type="checkbox"
                                            checked={selectedDocumentsForProfile.includes(doc.document_id)}
                                            onChange={(e) => handleDocumentSelection(doc.document_id, e.target.checked)}
                                            style={{marginRight: '8px'}}
                                        />
                                        📄 {doc.document_name}
                                        <span style={{color: '#666', marginLeft: '8px', fontSize: '12px'}}>
                                            ({doc.chunk_count} chunks)
                                        </span>
                                    </label>
                                    <button
                                        onClick={() => handleDeleteDocument(doc.document_id, doc.document_name)}
                                        disabled={loading}
                                        style={{
                                            backgroundColor: '#dc3545',
                                            color: 'white',
                                            border: 'none',
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            cursor: loading ? 'not-allowed' : 'pointer',
                                            fontSize: '12px',
                                            marginLeft: '10px',
                                            minWidth: '60px'
                                        }}
                                        title={`Delete ${doc.document_name}`}
                                    >
                                        {loading ? '⏳' : '🗑️ Delete'}
                                    </button>
                                </div>
                            ))}
                        </div>
                        
                        <div style={{marginTop: '12px', display: 'flex', gap: '10px', alignItems: 'center'}}>
                            <button 
                                onClick={() => autoExtractProfile(true)}
                                disabled={loading || selectedDocumentsForProfile.length === 0}
                                style={{
                                    backgroundColor: selectedDocumentsForProfile.length > 0 ? '#4CAF50' : '#ccc',
                                    color: 'white',
                                    border: 'none',
                                    padding: '8px 16px',
                                    borderRadius: '4px',
                                    cursor: (loading || selectedDocumentsForProfile.length === 0) ? 'not-allowed' : 'pointer',
                                    fontSize: '14px'
                                }}
                            >
                                {loading ? '⏳ Extracting...' : `📊 Extract from Selected (${selectedDocumentsForProfile.length})`}
                            </button>
                            
                            <button 
                                onClick={() => autoExtractProfile(false)}
                                disabled={loading}
                                style={{
                                    backgroundColor: '#2196F3',
                                    color: 'white',
                                    border: 'none',
                                    padding: '8px 16px',
                                    borderRadius: '4px',
                                    cursor: loading ? 'not-allowed' : 'pointer',
                                    fontSize: '14px'
                                }}
                            >
                                {loading ? '⏳ Extracting...' : '� Extract from All Documents'}
                            </button>
                        </div>
                        
                        {selectedDocumentsForProfile.length === 0 && (
                            <p style={{color: '#FF9800', fontSize: '12px', fontStyle: 'italic', marginTop: '8px', marginBottom: '0'}}>
                                Select at least one document to extract profile information
                            </p>
                        )}
                    </div>
                )}
                
                {/* Fallback manual extraction button for when no documents */}
                {documents.length === 0 && (
                    <div style={{marginBottom: '15px'}}>
                        <button 
                            onClick={() => autoExtractProfile(false)}
                            disabled={loading}
                            className="extract-profile-button"
                            style={{
                                backgroundColor: '#ccc',
                                color: 'white',
                                border: 'none',
                                padding: '8px 16px',
                                borderRadius: '4px',
                                cursor: 'not-allowed',
                                fontSize: '14px'
                            }}
                        >
                            🔄 Extract Profile from Documents
                        </button>
                        <p style={{color: '#FF9800', fontSize: '12px', fontStyle: 'italic', marginTop: '5px'}}>
                            Upload documents first to enable automatic profile extraction
                        </p>
                    </div>
                )}
                <div className="profile-form">
                    <div className="form-group">
                        <label htmlFor="userAge">Age</label>
                        <input type="number" id="userAge" name="age" value={userProfile.age} onChange={handleProfileChange} />
                    </div>
                    <div className="form-group">
                        <label htmlFor="fitnessLevel">Fitness Level</label>
                        <select id="fitnessLevel" name="fitness_level" value={userProfile.fitness_level} onChange={handleProfileChange}>
                            <option value="beginner">Beginner</option>
                            <option value="intermediate">Intermediate</option>
                            <option value="advanced">Advanced</option>
                        </select>
                    </div>
                    <div className="form-group full-width">
                        <label htmlFor="healthConditions">Health Conditions (comma-separated)</label>
                        <input type="text" id="healthConditions" name="conditions" value={userProfile.conditions} onChange={handleProfileChange} />
                    </div>
                    <div className="form-group full-width">
                        <label htmlFor="userGoals">Primary Health Goals</label>
                        <textarea id="userGoals" name="goals" rows="2" value={userProfile.goals} onChange={handleProfileChange}></textarea>
                    </div>
                    <div className="form-group full-width">
                        <label htmlFor="foodPreferences">Food Preferences (comma-separated)</label>
                        <input type="text" id="foodPreferences" name="food_preferences" value={userProfile.food_preferences} onChange={handleProfileChange} />
                    </div>
                </div>
            </div>

            <div className="chat-container">
                <h2>AI Health Tools</h2>
                <div className="tools-section">
                    <div className="tool-card">
                        <button onClick={() => callTool('documentQA')} className="tool-button" style={{ background: '#667eea' }}>📚 Document Q&A</button>
                        <input type="text" value={docQAInput} onChange={(e) => setDocQAInput(e.target.value)} placeholder="Ask about your documents..." />
                    </div>
                    <div className="tool-card">
                        <button onClick={() => callTool('web_search')} className="tool-button" style={{ background: '#17a2b8' }}>🌐 Health Knowledge Search</button>
                        <input type="text" value={healthSearchInput} onChange={(e) => setHealthSearchInput(e.target.value)} placeholder="Search for exercises, recipes..." />
                    </div>
                    <div className="tool-card">
                        <button onClick={() => callTool('recommendation_agent')} className="tool-button" style={{ background: '#28a745' }}>💡 Get Health Recommendations</button>
                    </div>
                    <div className="tool-card">
                        <button onClick={() => callTool('fitness_plan')} className="tool-button" style={{ background: '#fd7e14' }}>🏃‍♂️ Create Fitness Plan</button>
                    </div>
                    <div className="tool-card">
                        <button onClick={() => callTool('meal_planner')} className="tool-button" style={{ background: '#6f42c1' }}>🥗 Create Meal Plan</button>
                    </div>
                </div>
            </div>

            {loading && <div className="loading">AI Health Buddy is thinking...</div>}
            {results && <div className="results-container">{renderResults()}</div>}
        </div>
    );
}

export default App;
