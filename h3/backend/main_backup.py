"""
AI Health Buddy Backend
======================

This application provides a complete pipeline for:
- PDF upload and text extraction
- Text chunking and vectorization
- AI-powered health recommendations
- Document Q&A system

Features:
- PDF upload via web interface
- Text extraction from PDFs
- Intelligent text chunking
- Vector embedding generation
- Vector storage in ChromaDB
- AI health tools and recommendations
- RESTful API endpoints with CORS support

Usage:
1. Set up environment variables (GOOGLE_API_KEY in .env)
2. Install dependencies: pip install -r requirements.txt
3. Run the application: python main.py
4. Upload PDFs and use AI health tools
"""

import os
import shutil
import tempfile
import uuid
from typing import List, Dict, Optional

import pypdf
import chromadb
import google.generativeai as genai
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import logging
from pydantic import BaseModel

# --- Pydantic Models ---
class WebSearchRequest(BaseModel):
    query: str
class FitnessPlanRequest(BaseModel):
    user_profile: Dict
    goals: str
class MealPlannerRequest(BaseModel):
    user_profile: Dict
    health_conditions: List[str]
    food_preferences: List[str]
class RecommendationRequest(BaseModel):
    report_data: Dict
    user_profile: Dict

# --- Basic Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI Health Buddy Backend",
    description="Provides API endpoints for the Health Buddy application.",
    version="2.0.0"
)

# --- CORS Middleware ---
# This allows your React frontend (running on localhost:3000) to communicate with the backend.
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration & Initialization ---
# (Your Config class, genai.configure, chromadb.PersistentClient, and text_splitter go here)
class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    CHROMADB_PATH = os.getenv("CHROMADB_PATH", "./vector_db")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "pdf_documents")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Health Assistant defaults
    DEFAULT_USER_AGE = int(os.getenv("DEFAULT_USER_AGE", "35"))
    DEFAULT_ACTIVITY_LEVEL = os.getenv("DEFAULT_ACTIVITY_LEVEL", "moderate")
    DEFAULT_FITNESS_LEVEL = os.getenv("DEFAULT_FITNESS_LEVEL", "beginner")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GOOGLE_API_KEY or cls.GOOGLE_API_KEY == "your_google_api_key_here":
            logger.warning("GOOGLE_API_KEY not properly set. Please update your .env file with a valid Google AI API key.")
            logger.warning("Get your API key from: https://aistudio.google.com/app/apikey")
        return True

# Initialize configuration
Config.validate()
    
if Config.GOOGLE_API_KEY:
    genai.configure(api_key=Config.GOOGLE_API_KEY)
try:
    client = chromadb.PersistentClient(path=Config.CHROMADB_PATH)
    collection = client.get_or_create_collection(name="pdf_documents")
except Exception as e:
    collection = None
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)


# --- DocumentProcessor Class ---
# (Your complete DocumentProcessor class goes here, unchanged)
class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract text from PDF using pypdf
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            full_text = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    full_text += f"\n--- Page {page_num + 1} ---\n{text}"
            
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise HTTPException(status_code=500, detail=f"PDF text extraction failed: {str(e)}")
    
    @staticmethod
    def generate_embeddings(chunks: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks using Google's embedding model
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of embedding vectors
        """
        if not Config.GOOGLE_API_KEY:
            raise HTTPException(
                status_code=500, 
                detail="Google API key not configured. Cannot generate embeddings."
            )
        
        try:
            embeddings = []
            
            # Process chunks in batches to avoid API limits
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=batch,
                    task_type="RETRIEVAL_DOCUMENT"
                )
                
                # Handle both single and batch embeddings
                if isinstance(result['embedding'][0], list):
                    embeddings.extend(result['embedding'])
                else:
                    embeddings.append(result['embedding'])
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")
    
    @staticmethod
    def store_vectors(chunks: List[str], embeddings: List[List[float]], document_id: str, document_name: str = None) -> Dict:
        """
        Store vectors and text in ChromaDB
        
        Args:
            chunks: List of text chunks
            embeddings: List of embedding vectors
            document_id: Unique identifier for the document
            document_name: Human-readable name for the document
            
        Returns:
            Storage result information
        """
        if not collection:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        try:
            # Generate unique IDs for each chunk
            chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            
            # Prepare metadata
            metadatas = [{"document_id": document_id, "chunk_index": i, "document_name": document_name or "Unnamed Document"} for i in range(len(chunks))]
            
            # Store in ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            result = {
                "document_id": document_id,
                "chunks_stored": len(chunks),
                "embeddings_stored": len(embeddings)
            }
            
            logger.info(f"Stored {len(chunks)} vectors for document {document_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error storing vectors: {e}")
            raise HTTPException(status_code=500, detail=f"Vector storage failed: {str(e)}")
    
    @classmethod
    def process_pdf(cls, pdf_path: str, document_id: str, document_name: str = None) -> Dict:
        """
        Complete PDF processing pipeline
        
        Args:
            pdf_path: Path to PDF file
            document_id: Unique document identifier
            document_name: Human-readable name for the document
            
        Returns:
            Processing result summary
        """
        try:
            # Step 1: Extract text from PDF
            text = cls.extract_text_from_pdf(pdf_path)
            
            # Step 2: Chunk the text
            chunks = cls.chunk_text(text)
            
            # Step 3: Generate embeddings
            embeddings = cls.generate_embeddings(chunks)
            
            # Step 4: Store vectors
            storage_result = cls.store_vectors(chunks, embeddings, document_id, document_name)
            
            # Cleanup temporary file
            try:
                os.remove(pdf_path)
            except:
                pass
            
            return {
                "status": "success",
                "document_id": document_id,
                "document_name": document_name or "Unnamed Document",
                "text_length": len(text),
                "chunks_created": len(chunks),
                "embeddings_generated": len(embeddings),
                "storage_result": storage_result
            }
            
        except Exception as e:
            # Cleanup on error
            try:
                os.remove(pdf_path)
            except:
                pass
            raise e
        


# --- API Endpoints ---
@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "AI Health Buddy API is running"}
@app.post("/upload-pdf/")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), document_name: Optional[str] = None):
    """
    Upload and process a PDF document with optional custom name
    
    Args:
        file: PDF file to process
        document_name: Optional custom name for the document (defaults to filename)
        
    Returns:
        Processing result with document info
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate unique document ID
    document_id = str(uuid.uuid4())
    
    # Use custom name if provided, otherwise use filename
    display_name = document_name.strip() if document_name else file.filename
    
    # Save uploaded file temporarily
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"{document_id}_{file.filename}")
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the PDF (this runs synchronously for now)
        result = DocumentProcessor.process_pdf(temp_path, document_id, display_name)
        
        return result
        
    except Exception as e:
        # Cleanup on error
        try:
            os.remove(temp_path)
        except:
            pass
        raise e


@app.get("/search/")
async def search_documents(query: str, limit: int = 5):
    """
    Search for similar documents using vector similarity
    
    Args:
        query: Search query text
        limit: Maximum number of results to return
        
    Returns:
        List of similar document chunks
    """
    if not Config.GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    if not collection:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        # Generate embedding for the query
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="RETRIEVAL_QUERY"
        )
        query_embedding = result['embedding']
        
        # Search for similar documents
        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        # Format results
        formatted_results = []
        for i in range(len(search_results['documents'][0])):
            formatted_results.append({
                "document": search_results['documents'][0][i],
                "metadata": search_results['metadatas'][0][i],
                "distance": search_results['distances'][0][i]
            })
        
        return {
            "query": query,
            "results": formatted_results
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/ask/")
async def ask_question(query: str, document_id: Optional[str] = None, limit: int = 5):
    """
    Ask a question and get an AI-generated answer based on document content
    
    Args:
        query: Question to ask
        document_id: Optional specific document ID to search in
        limit: Maximum number of context chunks to use
        
    Returns:
        AI-generated answer with sources
    """
    if not Config.GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    if not collection:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        # Generate embedding for the query
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="RETRIEVAL_QUERY"
        )
        query_embedding = result['embedding']
        
        # Build search filter for specific document if provided
        where_filter = {}
        if document_id:
            where_filter = {"document_id": document_id}
        
        # Search for similar documents
        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_filter if where_filter else None
        )
        
        if not search_results['documents'][0]:
            return {
                "query": query,
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "sources": [],
                "document_id": document_id
            }
        
        # Combine top results as context
        context_chunks = search_results['documents'][0]
        context = "\n\n".join(context_chunks)
        
        # Generate answer using Gemini with improved prompt
        prompt = f"""You are a helpful assistant that provides specific, practical, and actionable answers based on the given context.

INSTRUCTIONS:
- Use the CONTEXT below to answer the QUESTION
- Give specific examples, recommendations, or steps when possible
- If the context mentions general concepts, provide concrete practical applications
- For health/exercise questions, suggest specific activities or routines
- For technical questions, provide step-by-step guidance
- If you don't know the answer based on the context, say so clearly
- Be conversational but informative

CONTEXT: {context}

QUESTION: {query}

Please provide a helpful, specific answer with practical recommendations based on the context above:"""

        # Generate response using Gemini
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Format sources
        sources = []
        for i, doc in enumerate(context_chunks):
            metadata = search_results['metadatas'][0][i] if i < len(search_results['metadatas'][0]) else {}
            sources.append({
                "chunk_index": i,
                "content_preview": doc[:200] + "..." if len(doc) > 200 else doc,
                "metadata": metadata,
                "relevance_score": 1 - search_results['distances'][0][i] if i < len(search_results['distances'][0]) else 0
            })
        
        return {
            "query": query,
            "answer": response.text,
            "sources": sources,
            "document_id": document_id,
            "total_sources": len(sources)
        }
        
    except Exception as e:
        logger.error(f"Question answering error: {e}")
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")

def retrieve_relevant_recommendations(report_data: Dict, user_profile: Dict) -> List[Dict]:
    """Retrieve personalized health recommendations based on report and profile."""
    if not collection:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    # Extract key health indicators from report data and user profile
    health_context = f"Report: {report_data.get('summary', '')} Profile: {user_profile.get('conditions', '')}"
    
    try:
        # Generate embedding for health context
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=health_context,
            task_type="RETRIEVAL_QUERY"
        )
        query_embedding = result['embedding']
        
        # Search for relevant health recommendations in vectorized documents
        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        # Return structured recommendations
        recommendations = []
        for i, doc in enumerate(search_results['documents'][0]):
            recommendations.append({
                "title": f"Recommendation {i+1}",
                "advice": doc[:200] + "...",
                "details": search_results['metadatas'][0][i] if i < len(search_results['metadatas'][0]) else {},
                "metadata": {"source": "vector_db", "relevance": 1 - search_results['distances'][0][i]}
            })
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error retrieving recommendations: {e}")
        # Fallback to basic recommendations
        return [
            {"title": "Stay Hydrated", "advice": "Drink at least 2 liters of water daily.", "details": "Essential for health.", "metadata": {"source": "default"}},
            {"title": "Regular Exercise", "advice": "30 minutes of moderate activity daily.", "details": "Improves overall health.", "metadata": {"source": "default"}}
        ]


def generate_recommendation_cards(recommendations: List[Dict]) -> List[Dict]:
    """Format recommendations into cards using LLM for explanation."""
    if not Config.GOOGLE_API_KEY:
        return recommendations  # Return basic recommendations without LLM enhancement
    
    cards = []
    for rec in recommendations:
        try:
            prompt = f"""Create a personalized health recommendation card based on this advice:
            
Title: {rec['title']}
Advice: {rec['advice']}
Details: {rec['details']}

Please provide:
1. A clear explanation of why this recommendation is important
2. Specific, actionable steps to implement it
3. Expected benefits

Keep it concise but informative."""
            
            model = genai.GenerativeModel(Config.GEMINI_MODEL)
            response = model.generate_content(prompt)
            
            cards.append({
                "title": rec['title'],
                "explanation": response.text,
                "metadata": rec.get('metadata', {})
            })
        except Exception as e:
            logger.error(f"Error generating recommendation card: {e}")
            # Fallback to original recommendation
            cards.append(rec)
    
    return cards


@app.post("/recommendation-agent/")
async def recommendation_agent(request: RecommendationRequest):
    """End-to-end recommendation pipeline."""
    try:
        recommendations = retrieve_relevant_recommendations(request.report_data, request.user_profile)
        recommendation_cards = generate_recommendation_cards(recommendations)
        
        return {
            "recommendations": recommendation_cards,
            "total_recommendations": len(recommendation_cards)
        }
    except Exception as e:
        logger.error(f"Recommendation agent error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")


@app.post("/web-search/")
async def web_search(request: WebSearchRequest):
    """Search the web for general health knowledge."""
    if not Config.GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    try:
        # For now, we'll use the LLM to provide general health knowledge
        # In a full implementation, you would integrate with a web search API
        prompt = f"""Provide comprehensive, evidence-based information about: {request.query}

Please include:
1. Key facts and definitions
2. Health benefits or risks
3. Practical recommendations
4. When to consult healthcare professionals

Focus on accurate, helpful health information."""
        
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Simulate web search results structure
        sources = [
            {"title": "Health Knowledge Base", "snippet": "AI-generated health information", "url": "internal"},
            {"title": "Medical Guidelines", "snippet": "Evidence-based recommendations", "url": "internal"}
        ]
        
        return {
            "query": request.query,
            "answer": response.text,
            "sources": sources
        }
        
    except Exception as e:
        logger.error(f"Web search error: {e}")
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")


@app.post("/create-fitness-plan/")
async def create_fitness_plan(request: FitnessPlanRequest):
    """Generate a personalized fitness plan."""
    if not Config.GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    try:
        prompt = f"""Create a detailed, personalized fitness plan based on:

User Profile: {request.user_profile}
Goals: {request.goals}

Please provide:
1. Weekly workout schedule
2. Specific exercises with sets/reps
3. Progression plan
4. Safety considerations
5. Equipment needed
6. Time commitment per session

Make it practical and achievable for the user's level and goals."""
        
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        return {
            "user_profile": request.user_profile,
            "goals": request.goals,
            "fitness_plan": response.text
        }
        
    except Exception as e:
        logger.error(f"Fitness plan generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Fitness plan generation failed: {str(e)}")


@app.post("/meal-planner/")
async def meal_planner(request: MealPlannerRequest):
    """Suggest safe foods and create a diet plan."""
    if not Config.GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    try:
        prompt = f"""Create a comprehensive meal plan based on:

User Profile: {request.user_profile}
Health Conditions: {request.health_conditions}
Food Preferences: {request.food_preferences}

Please provide:
1. Daily meal plan (breakfast, lunch, dinner, snacks)
2. Foods to avoid based on health conditions
3. Safe food alternatives
4. Nutritional guidelines
5. Shopping list suggestions
6. Meal prep tips

Focus on foods that support the user's health conditions and preferences."""
        
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        return {
            "user_profile": request.user_profile,
            "health_conditions": request.health_conditions,
            "food_preferences": request.food_preferences,
            "meal_plan": response.text
        }
        
    except Exception as e:
        logger.error(f"Meal planning error: {e}")
        raise HTTPException(status_code=500, detail=f"Meal planning failed: {str(e)}")
# (All your other API endpoints go here, unchanged)
# @app.post("/upload-pdf/")
# async def upload_pdf(...)

# @app.post("/ask/")
# async def ask_question(...)

# @app.post("/recommendation-agent/")
# async def recommendation_agent(...)

# @app.post("/web-search/")
# async def web_search(...)

# @app.post("/create-fitness-plan/")
# async def create_fitness_plan(...)

# @app.post("/meal-planner/")
# async def meal_planner(...)

# (Your other utility endpoints like /documents, /delete-document, etc. go here)
@app.get("/documents/")
async def list_documents():
    """Get list of all uploaded documents"""
    if not collection:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        # Get all documents
        results = collection.get()
        
        # Extract unique document IDs
        document_ids = set()
        document_info = {}
        
        if results['metadatas']:
            for metadata in results['metadatas']:
                if 'document_id' in metadata:
                    doc_id = metadata['document_id']
                    document_name = metadata.get('document_name', 'Unnamed Document')
                    document_ids.add(doc_id)
                    
                    if doc_id not in document_info:
                        document_info[doc_id] = {
                            "document_id": doc_id,
                            "document_name": document_name,
                            "chunk_count": 0
                        }
                    
                    document_info[doc_id]["chunk_count"] += 1
        
        documents_list = list(document_info.values())
        documents_list.sort(key=lambda x: x['document_id'])
        
        return {
            "documents": documents_list,
            "total_documents": len(documents_list),
            "total_chunks": len(results['ids']) if results['ids'] else 0
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.post("/rename-document/")
async def rename_document(document_id: str, new_name: str):
    """
    Rename an existing document
    
    Args:
        document_id: ID of the document to rename
        new_name: New name for the document
        
    Returns:
        Success confirmation
    """
    if not collection:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    if not new_name.strip():
        raise HTTPException(status_code=400, detail="Document name cannot be empty")
    
    try:
        # Get all chunks for this document
        results = collection.get(where={"document_id": document_id})
        
        if not results['ids']:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update metadata for all chunks
        updated_metadatas = []
        for metadata in results['metadatas']:
            metadata['document_name'] = new_name.strip()
            updated_metadatas.append(metadata)
        
        # Update in ChromaDB
        collection.update(
            ids=results['ids'],
            metadatas=updated_metadatas
        )
        
        return {
            "status": "success",
            "document_id": document_id,
            "new_name": new_name.strip(),
            "chunks_updated": len(results['ids'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error renaming document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rename document: {str(e)}")


@app.delete("/delete-document/")
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks from the vector database
    
    Args:
        document_id: ID of the document to delete
        
    Returns:
        Deletion confirmation with count of removed chunks
    """
    if not collection:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        # Get all chunks for this document
        results = collection.get(where={"document_id": document_id})
        
        if not results['ids']:
            raise HTTPException(status_code=404, detail="Document not found")
        
        chunk_count = len(results['ids'])
        document_name = results['metadatas'][0].get('document_name', 'Unknown Document') if results['metadatas'] else 'Unknown Document'
        
        # Delete all chunks for this document
        collection.delete(where={"document_id": document_id})
        
        logger.info(f"Deleted document {document_id} ({document_name}) with {chunk_count} chunks")
        
        return {
            "status": "success",
            "document_id": document_id,
            "document_name": document_name,
            "chunks_deleted": chunk_count,
            "message": f"Successfully deleted '{document_name}' and all its data"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@app.get("/status/")
async def get_status():
    """Get system status and configuration"""
    return {
        "status": "running",
        "google_api_configured": bool(Config.GOOGLE_API_KEY),
        "api_key_length": len(Config.GOOGLE_API_KEY) if Config.GOOGLE_API_KEY else 0,
        "api_key_preview": Config.GOOGLE_API_KEY[:10] + "..." if Config.GOOGLE_API_KEY and len(Config.GOOGLE_API_KEY) > 10 else "Not set",
        "chromadb_configured": collection is not None,
        "collection_name": Config.COLLECTION_NAME,
        "chunk_size": Config.CHUNK_SIZE,
        "chunk_overlap": Config.CHUNK_OVERLAP,
        "total_documents": collection.count() if collection else 0
    }


@app.get("/health/")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
