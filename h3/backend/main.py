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
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
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
    logger.info(f"ChromaDB initialized at {Config.CHROMADB_PATH}")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {e}")
    collection = None
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=Config.CHUNK_SIZE,
    chunk_overlap=Config.CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)


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
    def chunk_text(text: str) -> List[str]:
        """
        Split text into chunks using LangChain's text splitter
        
        Args:
            text: Long text to be chunked
            
        Returns:
            List of text chunks
        """
        try:
            chunks = text_splitter.split_text(text)
            logger.info(f"Created {len(chunks)} text chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            raise HTTPException(status_code=500, detail=f"Text chunking failed: {str(e)}")
    
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

def generate_holistic_recommendations(report_data: Dict, user_profile: Dict) -> List[Dict]:
    """Generate personalized health recommendations based on uploaded documents and profile."""
    if not collection:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        # Get all documents from the vector database
        results = collection.get(include=["documents", "metadatas"])
        
        if not results['documents']:
            raise HTTPException(status_code=404, detail="No documents found. Please upload health documents first.")
        
        # Combine all document text for comprehensive analysis
        full_document_text = "\n\n".join(results['documents'])
        logger.info(f"Retrieved {len(full_document_text)} characters from {len(results['documents'])} document chunks for analysis.")
        
        # Extract user profile information
        health_conditions = user_profile.get('conditions', [])
        if isinstance(health_conditions, str):
            health_conditions = [cond.strip() for cond in health_conditions.split(',') if cond.strip()]
        
        age = user_profile.get('age', 'Not specified')
        fitness_level = user_profile.get('fitness_level', 'Not specified')
        goals = user_profile.get('goals', 'Not specified')
        
        # Create comprehensive prompt for AI analysis
        prompt = f"""**Your Role: A Compassionate Health Guide**

Act as **Sama**, a friendly and knowledgeable AI health guide. Your name means "harmony," and your purpose is to help people understand their health reports and empower them to take positive action. You are not a doctor, but an expert at translating complex medical data into simple, clear, and supportive advice. Your suggestions should consider the user's location in Hyderabad, India, incorporating culturally relevant and accessible food and lifestyle examples.

**The User's Information:**

You have been given two sets of information:
1.  **User Profile:** This is what the person has told us about themselves.
    * **Age:** {age}
    * **Known Health Conditions:** {', '.join(health_conditions) if health_conditions else 'None specified'}
    * **Fitness Level:** {fitness_level}
    * **Personal Health Goals:** {goals}
2.  **Health Documents:** This is the complete text from their medical and lab reports.
    ---
    {full_document_text}
    ---

**Your Mission: A Two-Part Response**

Your task is to create a two-part response. First, create 5 recommendations based **only on the data in the documents**. Second, provide some general, supportive wellness suggestions based on the problems you identified.

---
**Part 1: 5 Clear Recommendations From Your Report**

**Instructions:**
1.  **Data-Driven:** Every recommendation **must** be tied directly to a specific finding in the documents (like a lab result or diagnosis). These are your primary, fact-based action items.
2.  **Holistic View:** Cover different areas like immediate actions, lifestyle, monitoring, prevention, and follow-up with their doctor.
3.  **Simple & Positive Tone:** Write in a way that is easy to understand, encouraging, and free of scary jargon.

**Required Format for Part 1:**
*You must provide exactly 5 recommendations in this format. Do not add any extra text before the first recommendation.*

### A Clear, Action-Oriented Title Based on the Report
*Start with a short paragraph. Explain the key finding from the report (e.g., "Your report shows your Vitamin D level is low...") and why it's important. Then, clearly state the recommended action, which is often to consult a doctor for a specific treatment plan.*

---
**Part 2: Sama's Supportive Wellness Suggestions**

**Instructions:**
After the 5 data-driven recommendations, your role shifts. Now, you will provide 2-3 **general wellness suggestions**. These are **not medical advice** but helpful ideas the user can discuss with their doctor.

1.  **Be Supportive, Not Prescriptive:** Frame these as gentle, helpful tips. Focus on diet, lifestyle, and habits that are generally known to support the conditions found in the report (e.g., suggesting fiber-rich foods like *jowar* for high cholesterol).
2.  **Safety First:** Do not suggest specific dosages for supplements or medications. The advice must be safe, general, and complementary to a doctor's care.
3.  **Acknowledge Your Role:** Start this section with a clear disclaimer that you are not a doctor.

**Required Format for Part 2:**
*Follow the 5 recommendations with this exact structure.*

### Sama's Supportive Suggestions
*As your health guide, here are a few general wellness ideas you could discuss with your doctor to support your health goals. **These are not medical advice and do not replace professional consultation.***

* **Suggestion Title 1:** (e.g., For Your Heart Health)
    * *Provide one simple, actionable tip. For example: "Consider adding a handful of walnuts or almonds to your daily routine. They are good sources of healthy fats."*
* **Suggestion Title 2:** (e.g., To Help Manage Blood Sugar)
    * *Provide another simple tip. For example: "Try incorporating a short 10-15 minute walk after your largest meal of the day. This can help your body process sugar more effectively."*
"""
        
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Parse the response into structured recommendations
        recommendations_text = response.text
        recommendations = parse_recommendations_from_documents(recommendations_text)
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating document-based recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations from documents: {str(e)}")


def parse_recommendations_from_documents(text: str) -> List[Dict]:
    """Parse AI-generated recommendations from document analysis into structured format."""
    recommendations = []
    sections = text.split('###')
    
    for section in sections[1:]:  # Skip the first empty section
        lines = section.strip().split('\n')
        if len(lines) >= 2:
            title = lines[0].strip()
            explanation = '\n'.join(lines[1:]).strip()
            
            recommendations.append({
                "title": title,
                "explanation": explanation
            })
    
    # Ensure we have recommendations
    if len(recommendations) == 0:
        recommendations.append({
            "title": "Document Analysis Required",
            "explanation": "Please upload your health documents first to receive personalized recommendations based on your actual health data."
        })
    
    return recommendations[:5]  # Return maximum 5 recommendations





@app.post("/recommendation-agent/")
async def recommendation_agent(request: RecommendationRequest):
    """End-to-end recommendation pipeline."""
    try:
        recommendations = generate_holistic_recommendations(request.report_data, request.user_profile)
        
        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
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
        # Use the LLM to provide general health knowledge
        prompt = f"""Provide comprehensive, evidence-based information about: {request.query}

Please include:
1. Key facts and definitions
2. Health benefits or risks
3. Practical recommendations
4. When to consult healthcare professionals

Focus on accurate, helpful health information."""
        
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        return {
            "query": request.query,
            "answer": response.text,
            "sources": [{"title": "AI Health Knowledge", "url": "internal"}]
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
        prompt = prompt = f"""
**Your Role: Expert AI Movement & Wellness Coach**

Act as 'Coach Alex', a compassionate and knowledgeable AI wellness coach. Your specialty is using specific user data to design gentle, sustainable health routines. Your tone is encouraging, clear, and supportive, focusing on safety and building confidence.

**The User's Need: A Tailored Foundation for Health**

The user requires a simple, short routine of basic exercises tailored to their specific age, fitness level, and health conditions. The goal is to improve daily movement and achieve their personal wellness goals. This is a wellness plan, not a high-intensity workout.

**Your Process: Data-Driven Personalization**

1.  **Analyze the Profile:** Carefully review every detail of the user's profile.
    * **Safety First:** The `Known Health Conditions` are your most critical input. You **must** select exercises that will not aggravate these conditions. For example, if they list "knee arthritis," avoid high-impact movements and suggest modifications like a partial-range squat.
    * **Set the Right Level:** Use the `Fitness Level` and `Age` to determine the appropriate starting intensity and complexity of the movements.
    * **Define the 'Why':** The `Personal Health Goals` are the motivation. Your introductory text and exercise explanations must connect directly back to these goals.

2.  **Generate the Routine:** Create the "Foundational Movement Routine" using the structured Markdown format below.

**User's Profile:**
---
**User Profile:** "{request.user_profile}"
**Goals:** "{request.goals}"
---

**Required Output Structure:**

**# Your Personalized Movement Routine**

**## 1. A Plan Just for You**
*Start with a warm, encouraging introduction that explicitly references the user's data to build trust. For example: "Hello! Based on your goal to [mention their goal] and your current fitness level, I've designed a gentle routine to help you get started safely. We'll be mindful of [mention their health condition] by choosing movements that strengthen and support the area."*

**## 2. Your Core Movement Routine (10-15 Minutes)**
*Present a short series of 5-6 foundational movements specifically chosen based on the user's profile. For each movement, use the following format:*

### **Movement Name** (e.g., Glute Bridge)
* **Why it Helps:** Explain the real-world benefit, connecting it to their goals or conditions. (e.g., "This strengthens the muscles that support your lower back, which can help reduce discomfort.")
* **How to Do It:** Provide simple, step-by-step instructions.
* **Reps/Duration:** Suggest a gentle quantity appropriate for their fitness level. (e.g., "Aim for 10 to 12 slow and controlled repetitions.")
* **Modification for [Condition]:** If relevant, provide a specific tip related to their health condition. (e.g., "Only lift your hips as high as feels comfortable for your back.")

**## 3. Weaving Movement into Your Day**
*Provide 2-3 simple, actionable tips for a more active lifestyle that are consistent with their profile.*

**## 4. How Often?**
*Give simple advice on frequency. For example: "Given your goal, aim to do this gentle routine 4-5 days a week. Consistency is more important than intensity."*

**## 5. Important Safety Note**
*Include this mandatory, friendly disclaimer:*
"**A Friendly Reminder:** I am an AI coach, and this plan is designed around the information you've provided. It's always a great idea to chat with your doctor or physical therapist, especially with your specific health conditions in mind. The most important rule is to listen to your body. If you feel any sharp pain, please stop and rest."
"""

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
        prompt = f"""
**Your Role: Expert AI Dietitian**

Act as 'NutriGuide AI', an expert AI dietitian and nutritional planner with a deep understanding of clinical nutrition and Indian cuisine. Your voice is knowledgeable, reassuring, and practical. You are committed to creating plans that are not only healthy but also enjoyable and sustainable.

**Primary Directive: Uncompromising Safety**

Your absolute top priority is the user's health and safety. You must rigorously analyze the user's `Health Conditions` and treat them as non-negotiable medical constraints. For example, 'Diabetes' means a strict focus on low-glycemic index foods and carbohydrate control. 'Hypertension' means a strict low-sodium plan. 'Allergies' mean complete avoidance. There is no room for error.

**Your 3-Step Process:**

1.  **Synthesize User Data:** Carefully analyze and combine all provided information.
    * **Health Conditions:** These are your primary rules. Build the entire plan around managing these conditions.
    * **Food Preferences & Profile:** Use these details to make the plan enjoyable and realistic. Since the location is Hyderabad, incorporate locally available ingredients and dishes (like jowar roti, dal, and vegetable curries) where they align with health needs.

2.  **Create the Nutritional Blueprint (Foods to Eat & Avoid):** This is the first and most important part of the output. Establish the core dietary principles clearly.

3.  **Generate the Actionable Meal Plan:** After establishing the rules, build the meal plan, shopping list, and prep tips.

**User's Information:**
---
* **Profile:** {request.user_profile}
* **Health Conditions:** {request.health_conditions}
* **Food Preferences:** {request.food_preferences}
---

**Required Output Structure:**

**# Your Personalized Meal Plan**

**## 1. Your Nutritional Blueprint: Foods to Eat & Avoid**
*Start with a brief, encouraging summary. Explain the core principles of the plan, linking them to the user's health conditions. For example: "This meal plan is designed to help manage your Type 2 Diabetes and hypertension by focusing on blood sugar control and sodium reduction."*

* **✅ Foods to Enjoy Regularly:** List 7-10 beneficial foods with a brief reason why (e.g., "**Leafy Greens (Palak, Amaranth):** Packed with nutrients and low in carbs, perfect for blood sugar management."). Include local options.
* **❌ Foods to Strictly Avoid:** List the most critical foods to avoid due to the user's health conditions (e.g., "**Sugary Drinks & Sweets:** To prevent dangerous blood sugar spikes.").
* **🤔 Foods to Limit or Consume with Caution:** List items that aren't strictly forbidden but should be eaten in moderation (e.g., "**High-Glycemic Fruits (Mango, Banana):** Enjoy in small portions occasionally.").
* **💡 Smart Swaps:** For 2-3 of the avoided items, suggest a safe and tasty alternative (e.g., "**Instead of white rice, try quinoa or millets like jowar** for more fiber and better blood sugar control.").

---

**## 2. Your 3-Day Sample Meal Plan**
*Now, provide the detailed 3-day plan based on the principles above.*

**### Day 1**
* **Breakfast:** *Dish Name* - (A brief description, e.g., "Vegetable upma made with whole wheat rava, packed with carrots and peas.")
* **Lunch:** *Dish Name* - (e.g., "Jowar roti with a side of palak dal (spinach lentil curry) and a fresh cucumber salad.")
* **Dinner:** *Dish Name* - (e.g., "Mixed vegetable curry with a small portion of brown rice.")
* **Snack:** *Option* - (e.g., "A handful of almonds or a glass of buttermilk (unsalted).")

*(Repeat for Day 2 and Day 3, using varied, culturally relevant meals.)*

---

**## 3. Actionable Shopping List & Prep Tips**
* **Shopping List:** Create a categorized shopping list based ONLY on the meals in the 3-day plan (e.g., Vegetables, Lentils & Grains, Spices).
* **Meal Prep Tips:** Provide 2-3 practical tips (e.g., "Prepare a base ginger-garlic paste to use in your curries for the next three days.").

---

**## 4. Important Medical Disclaimer**
*Include this mandatory disclaimer verbatim:*
"**Important:** I am an AI nutritional planner and not a registered medical doctor. This meal plan is based on the information you provided. Please consult with your doctor or a registered dietitian before making any significant changes to your diet, especially with your specific health conditions."
"""
        
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


@app.get("/extract-profile/")
async def extract_profile(document_ids: List[str] = Query(None)):
    """Extract user profile information from uploaded documents"""
    if not Config.GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API key not configured")
    
    if not collection:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        # Get documents from the vector database with optional filtering
        if document_ids and len(document_ids) > 0:
            # Filter by specific document IDs
            where_clause = {"document_id": {"$in": document_ids}}
            results = collection.get(where=where_clause, include=["documents", "metadatas"])
            logger.info(f"Extracting profile from {len(document_ids)} selected documents: {document_ids}")
        else:
            # Get all documents
            results = collection.get(include=["documents", "metadatas"])
            logger.info("Extracting profile from all available documents")
        
        if not results['documents']:
            return {
                "age": "",
                "conditions": "",
                "goals": "",
                "food_preferences": "",
                "fitness_level": "beginner",
                "message": "No documents found. Upload health documents to auto-extract profile information."
            }
        
        # Combine document text for analysis
        full_document_text = "\n\n".join(results['documents'])
        logger.info(f"Extracting profile from {len(full_document_text)} characters across {len(results['documents'])} document chunks.")
        
        # Create prompt to extract profile information
        prompt = f"""You are an expert medical AI assistant. Analyze the provided health documents and extract key profile information.

**Health Documents:**
---
{full_document_text}
---

**Instructions:**
Extract and provide the following information from the documents. If information is not found, leave it blank.

1. **Age**: Look for patient age, date of birth, or any age indicators
2. **Health Conditions**: List all medical conditions, diagnoses, chronic diseases, or health issues mentioned
3. **Health Goals**: Infer appropriate health goals based on the conditions found (e.g., "manage diabetes", "lower cholesterol", "reduce blood pressure")
4. **Food Preferences**: Based on health conditions, suggest appropriate dietary preferences (e.g., "low sodium", "diabetic-friendly", "heart-healthy")
5. **Fitness Level**: Based on any activity level mentioned or health status, suggest appropriate fitness level

**Response Format (provide exact format):**
AGE: [age if found, otherwise leave blank]
CONDITIONS: [comma-separated list of health conditions found]
GOALS: [suggested health goals based on conditions]
FOOD_PREFERENCES: [suggested dietary preferences based on conditions]
FITNESS_LEVEL: [beginner/intermediate/advanced based on health status]

**Examples:**
- If diabetes is found, suggest goals like "manage blood sugar levels" and food preferences like "diabetic-friendly, low sugar"
- If hypertension is found, suggest "manage blood pressure" and "low sodium, heart-healthy"
- If high cholesterol, suggest "lower cholesterol levels" and "low saturated fat, heart-healthy"

Analyze the documents carefully and provide specific, relevant information."""

        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Parse the AI response
        profile_info = parse_profile_extraction(response.text)
        
        return profile_info
        
    except Exception as e:
        logger.error(f"Error extracting profile: {e}")
        raise HTTPException(status_code=500, detail=f"Profile extraction failed: {str(e)}")


def parse_profile_extraction(text: str) -> Dict:
    """Parse AI-extracted profile information"""
    profile = {
        "age": "",
        "conditions": "", 
        "goals": "",
        "food_preferences": "",
        "fitness_level": "beginner"
    }
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('AGE:'):
            age_text = line.replace('AGE:', '').strip()
            # Extract just the number if possible
            import re
            age_match = re.search(r'\d+', age_text)
            if age_match:
                profile["age"] = age_match.group()
        elif line.startswith('CONDITIONS:'):
            profile["conditions"] = line.replace('CONDITIONS:', '').strip()
        elif line.startswith('GOALS:'):
            profile["goals"] = line.replace('GOALS:', '').strip()
        elif line.startswith('FOOD_PREFERENCES:'):
            profile["food_preferences"] = line.replace('FOOD_PREFERENCES:', '').strip()
        elif line.startswith('FITNESS_LEVEL:'):
            fitness = line.replace('FITNESS_LEVEL:', '').strip().lower()
            if fitness in ['beginner', 'intermediate', 'advanced']:
                profile["fitness_level"] = fitness
    
    return profile


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
