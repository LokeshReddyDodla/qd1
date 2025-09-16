import React, { useState, useRef, useEffect } from 'react';

const ChatInterface = ({ userId, selectedDocuments }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const requestBody = {
        user_id: userId,
        message: inputMessage,
        selected_document_ids: Array.from(selectedDocuments)
      };

      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage = {
          role: 'assistant',
          content: data.answer,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        let errorContent = `HTTP ${response.status}: Failed to get response`;
        try {
          const error = await response.json();
          if (error.detail) {
            if (typeof error.detail === 'string') {
              errorContent = `Error: ${error.detail}`;
            } else if (Array.isArray(error.detail)) {
              errorContent = `Validation Error: ${error.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')}`;
            } else {
              errorContent = `Error: ${JSON.stringify(error.detail)}`;
            }
          } else {
            errorContent = `Error: ${JSON.stringify(error)}`;
          }
        } catch (parseError) {
          errorContent = `HTTP ${response.status}: Could not parse error response`;
        }
        
        const errorMessage = {
          role: 'error',
          content: errorContent,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: `Network error: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="chat-section">
      <div className="chat-header">
        <h3>💬 Chat with Your AI Coach</h3>
        {selectedDocuments.size > 0 && (
          <div className="selected-docs-indicator">
            📊 Analyzing {selectedDocuments.size} selected document(s)
          </div>
        )}
        <button className="clear-chat-btn" onClick={clearChat}>
          🗑️ Clear Chat
        </button>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-icon">🤖</div>
            <h4>Welcome to your AI Weight Loss Coach!</h4>
            <p>I can help you with:</p>
            <ul>
              <li>📊 Analyzing your InBody reports</li>
              <li>🏋️‍♀️ Creating personalized exercise plans</li>
              <li>🥗 Nutrition recommendations</li>
              <li>📈 Tracking your progress</li>
              <li>⚠️ Health insights and recommendations</li>
            </ul>
            <p><strong>Start by uploading your documents and asking me anything!</strong></p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <div className="message-text">
                  {message.content.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                </div>
                <div className="message-time">{message.timestamp}</div>
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me about your fitness goals, nutrition, or upload documents for analysis..."
          rows="3"
          disabled={isLoading}
        />
        <button 
          onClick={sendMessage} 
          disabled={!inputMessage.trim() || isLoading}
          className="send-btn"
        >
          {isLoading ? '⏳' : '📤'} Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
