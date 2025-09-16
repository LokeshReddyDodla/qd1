# api_main.py

# Load environment variables FIRST before any other imports
import os
from dotenv import load_dotenv
load_dotenv()

# Now import everything else
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from coach_agent import run_agent
from vector_store import process_base64_image_for_user, vector_store
import shutil
import tempfile

app = FastAPI(title="WeightLoss Coach API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# Mount static files from React build
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Serve the React frontend"""
    try:
        with open("frontend/build/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>React frontend not found. Please run 'npm run build' in the frontend directory.</h1>", status_code=404)

class ChatIn(BaseModel):
    user_id: str
    message: str
    selected_document_ids: Optional[List[str]] = None
    inbody_file_b64: Optional[str] = None
    exercise_pref: Optional[str] = None
    current_weight_kg: Optional[float] = None

class ChatOut(BaseModel):
    answer: str

class DocumentUploadOut(BaseModel):
    success: bool
    message: str
    chunks_added: Optional[int] = None

class Base64ImageIn(BaseModel):
    user_id: str
    image_b64: str
    image_format: Optional[str] = "jpeg"
    metadata: Optional[dict] = None

@app.post("/chat", response_model=ChatOut)
async def chat(inp: ChatIn):
    answer = await run_agent(
        user_id=inp.user_id,
        message=inp.message,
        selected_document_ids=inp.selected_document_ids,
        inbody_b64=inp.inbody_file_b64,
        exercise_pref=inp.exercise_pref,
        current_weight_kg=inp.current_weight_kg,
        session_id=inp.user_id
    )
    return ChatOut(answer=answer)

@app.post("/upload-document", response_model=DocumentUploadOut)
async def upload_document(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    custom_filename: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None)
):
    """
    Upload and process a PDF or image document for vectorization.
    """
    try:
        # Parse metadata if provided
        meta_dict = {}
        if metadata:
            try:
                meta_dict = eval(metadata)  # Simple eval for JSON-like string
            except:
                meta_dict = {"description": metadata}

        # Determine filename to use
        if custom_filename:
            # Create filename with custom name but keep original extension
            original_ext = os.path.splitext(file.filename)[1]
            display_filename = f"{custom_filename}{original_ext}"
        else:
            display_filename = file.filename

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{display_filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        try:
            # Add custom filename to metadata for vector store
            if custom_filename:
                meta_dict = meta_dict or {}
                meta_dict["custom_filename"] = custom_filename
                meta_dict["original_filename"] = file.filename

            # Process the document
            success = vector_store.add_document(temp_path, user_id, meta_dict)

            if success:
                # Get number of chunks added (approximate)
                docs = vector_store.list_user_documents(user_id)
                # Use display filename for matching
                chunks_count = len([d for d in docs if d.get("file_name") == display_filename])

                return DocumentUploadOut(
                    success=True,
                    message=f"Document '{display_filename}' processed successfully",
                    chunks_added=chunks_count
                )
            else:
                return DocumentUploadOut(
                    success=False,
                    message="Failed to process document"
                )

        finally:
            # Clean up temporary file
            os.unlink(temp_path)

    except Exception as e:
        return DocumentUploadOut(
            success=False,
            message=f"Error processing document: {str(e)}"
        )

@app.post("/process-image", response_model=DocumentUploadOut)
def process_base64_image(inp: Base64ImageIn):
    """
    Process a base64 encoded image for vectorization.
    """
    try:
        success = process_base64_image_for_user(
            inp.image_b64,
            inp.user_id,
            inp.image_format,
            inp.metadata
        )

        if success:
            return DocumentUploadOut(
                success=True,
                message="Image processed successfully"
            )
        else:
            return DocumentUploadOut(
                success=False,
                message="Failed to process image"
            )

    except Exception as e:
        return DocumentUploadOut(
            success=False,
            message=f"Error processing image: {str(e)}"
        )

@app.get("/user-documents/{user_id}")
def get_user_documents(user_id: str):
    """
    Get list of documents for a user.
    """
    try:
        documents = vector_store.list_user_documents(user_id)
        return {"success": True, "documents": documents}
    except Exception as e:
        return {"success": False, "error": str(e), "documents": []}

@app.delete("/user-documents/{user_id}")
def delete_user_documents(user_id: str):
    """
    Delete all documents for a user.
    """
    try:
        success = vector_store.delete_user_documents(user_id)
        return {"success": success, "message": "Documents deleted successfully" if success else "Failed to delete documents"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/debug/selected-docs/{user_id}")
def get_selected_docs_debug(user_id: str):
    """
    Debug endpoint to see what documents are selected for a user.
    """
    from coach_agent import SELECTED_DOCS
    return {
        "user_id": user_id,
        "selected_docs": SELECTED_DOCS.get(user_id, []),
        "all_selected": dict(SELECTED_DOCS)
    }

@app.delete("/user-documents/{user_id}/{document_id}")
def delete_specific_document(user_id: str, document_id: str):
    """
    Delete a specific document for a user.
    """
    try:
        # Delete documents with the specific ID pattern
        vector_store.collection.delete(where={"user_id": user_id, "id": {"$regex": f"{document_id}.*"}})
        return {"success": True, "message": "Document deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/select-document/{user_id}")
def select_document_for_analysis(user_id: str, document_data: dict):
    """
    Mark a document as selected for analysis.
    """
    try:
        document_id = document_data.get("document_id")
        selected = document_data.get("selected", True)

        if not document_id:
            return {"success": False, "error": "Document ID is required"}

        # Update document metadata to mark as selected
        # Note: ChromaDB doesn't support direct updates, so we'll handle this in the agent logic
        return {"success": True, "message": f"Document {document_id} {'selected' if selected else 'deselected'} for analysis"}
    except Exception as e:
        return {"success": False, "error": str(e)}