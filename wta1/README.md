# WeightLoss Coach API

A FastAPI application that provides AI-powered weight loss coaching using OpenAI's GPT models and Agents SDK.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install fastapi uvicorn pydantic openai openai-agents chromadb PyMuPDF Pillow python-dotenv
   ```

2. **Configure environment variables:**
   - The `.env` file is already created with placeholder values
   - Replace `YOUR_ACTUAL_OPENAI_API_KEY_HERE` with your actual OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Run the application:**
   ```bash
   # Quick start with demo
   python demo.py

   # Or run directly
   uvicorn api_main:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Access the application:**
   - 🌐 **Chat Interface (Frontend):** http://127.0.0.1:8000/
   - 📚 **API Documentation:** http://127.0.0.1:8000/docs

## API Usage

### Environment Setup
Before running the application, make sure to set your OpenAI API key in the `.env` file:
```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### Chat Endpoint
The main chat endpoint `/chat` accepts POST requests with the following JSON structure:

```json
{
  "user_id": "unique_user_identifier",
  "message": "User's message or question",
  "inbody_file_b64": "base64_encoded_inbody_image", // optional
  "exercise_pref": "preferred_exercise_type", // optional
  "current_weight_kg": 75.5 // optional
}
```

### Example chat request:
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Help me create a weight loss plan"
  }'
```

### Document Processing Endpoints

#### Upload Document (PDF/Image)
Upload and process a PDF or image file for vectorization:

```bash
curl -X POST "http://127.0.0.1:8000/upload-document" \
  -F "user_id=user123" \
  -F "file=@/path/to/document.pdf" \
  -F "metadata={\"type\": \"medical_report\", \"date\": \"2024-01-01\"}"
```

#### Process Base64 Image
Process a base64 encoded image:

```bash
curl -X POST "http://127.0.0.1:8000/process-image" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "image_b64": "base64_encoded_image_data",
    "image_format": "jpeg",
    "metadata": {"type": "inbody_scan", "date": "2024-01-01"}
  }'
```

#### Get User Documents
List all documents for a user:

```bash
curl -X GET "http://127.0.0.1:8000/user-documents/user123"
```

#### Delete User Documents
Delete all documents for a user:

```bash
curl -X DELETE "http://127.0.0.1:8000/user-documents/user123"
```

## Features

### 🤖 AI Coach Features
- **AI Coach**: Uses OpenAI's GPT models to provide personalized weight loss advice
- **InBody Analysis**: Can process InBody scan images using vision models
- **Exercise Planning**: Generates customized exercise plans based on user preferences
- **Health Monitoring**: Tracks progress and provides health insights
- **Session Memory**: Maintains conversation context across interactions

### 📄 Document Processing
- **Document Vectorization**: Converts PDFs and images to vector embeddings for RAG
- **ChromaDB Integration**: Persistent vector storage for efficient document retrieval
- **Multi-format Support**: Processes both PDF documents and image files (JPG, PNG, etc.)
- **Smart Chunking**: Automatically splits documents into optimal chunks for better retrieval
- **User-specific Storage**: Isolated document collections per user for privacy
- **Vision Processing**: Uses OpenAI Vision to extract text from images and documents

### 🎨 Frontend Interface
- **Modern Chat Interface**: Beautiful, responsive web interface
- **Drag & Drop Uploads**: Easy document and image upload functionality
- **Real-time Chat**: Instant responses from the AI coach
- **Document Management**: View and manage uploaded documents
- **Responsive Design**: Works on desktop and mobile devices
- **Status Updates**: Real-time feedback on document processing

### 🔧 Technical Features
- **Async Processing**: Fast, non-blocking operations
- **RESTful API**: Clean, documented endpoints
- **Error Handling**: Robust error handling and user feedback
- **Session Management**: SQLite-based session storage
- **Environment Configuration**: Secure API key management

## Security

- Never commit your `.env` file or API keys to version control
- The `.gitignore` file is configured to exclude sensitive files
- Use environment variables for all sensitive configuration

## Development

The application consists of two main files:
- `api_main.py`: FastAPI application with CORS middleware and endpoints
- `coach_agent.py`: OpenAI Agents SDK implementation with various tools for fitness coaching
