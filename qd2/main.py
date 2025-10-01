"""FastAPI application for RAG over patient data."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
import structlog
from pathlib import Path

from config import settings
from models import (
    ProfileInput, MealInput, FitnessInput, SleepInput,
    IngestResponse, QueryRequest, QueryResponse
)
from embedding_service import EmbeddingService
from qdrant_client_wrapper import QdrantManager
from llm_service import LLMService
from ingestion import IngestionPipeline
from retrieval import RetrievalService

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Patient Data RAG API",
    description="Retrieval-Augmented Generation over patient health data using Qdrant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy initialization on first request)
embedding_service = None
qdrant_manager = None
llm_service = None
ingestion_pipeline = None
retrieval_service = None


def get_services():
    """Initialize services if not already done."""
    global embedding_service, qdrant_manager, llm_service, ingestion_pipeline, retrieval_service
    
    if embedding_service is None:
        logger.info("Initializing services...")
        
        embedding_service = EmbeddingService()
        qdrant_manager = QdrantManager()
        llm_service = LLMService()
        
        # Ensure collection exists
        qdrant_manager.ensure_collection_exists()
        qdrant_manager.create_payload_indexes()
        
        ingestion_pipeline = IngestionPipeline(
            embedding_service=embedding_service,
            qdrant_manager=qdrant_manager
        )
        
        retrieval_service = RetrievalService(
            embedding_service=embedding_service,
            qdrant_manager=qdrant_manager,
            llm_service=llm_service
        )
        
        logger.info("Services initialized successfully")
    
    return {
        "embedding": embedding_service,
        "qdrant": qdrant_manager,
        "llm": llm_service,
        "ingestion": ingestion_pipeline,
        "retrieval": retrieval_service
    }


# ============================================================================
# Health and Info Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Serve the frontend HTML interface."""
    frontend_path = Path(__file__).parent / "frontend.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    else:
        return {
            "name": "Patient Data RAG API",
            "version": "1.0.0",
            "status": "running",
            "environment": settings.environment,
            "docs": "/docs",
            "frontend": "frontend.html not found"
        }


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "Patient Data RAG API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        services = get_services()
        qdrant_info = services["qdrant"].get_collection_info()
        
        return {
            "status": "healthy",
            "qdrant": {
                "connected": True,
                "collection": qdrant_info.get("name"),
                "points_count": qdrant_info.get("points_count", 0)
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.get("/collection/info")
async def collection_info():
    """Get Qdrant collection information."""
    try:
        services = get_services()
        info = services["qdrant"].get_collection_info()
        return info
    except Exception as e:
        logger.error("Failed to get collection info", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# Ingestion Endpoints
# ============================================================================

@app.post("/ingest/profile", response_model=IngestResponse)
async def ingest_profiles(profiles: List[ProfileInput]):
    """
    Ingest patient profiles from Postgres.
    
    Creates one chunk per patient with profile information.
    """
    if not profiles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty profiles list"
        )
    
    try:
        services = get_services()
        result = services["ingestion"].ingest_profiles(profiles)
        return result
    except Exception as e:
        logger.error("Profile ingestion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@app.post("/ingest/meals", response_model=IngestResponse)
async def ingest_meals(meals: List[MealInput]):
    """
    Ingest daily meal reports.
    
    Creates:
    - 1 summary chunk per day
    - 1 chunk per meal
    - 1 recommendations chunk (if present)
    """
    if not meals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty meals list"
        )
    
    try:
        services = get_services()
        result = services["ingestion"].ingest_meals(meals)
        return result
    except Exception as e:
        logger.error("Meals ingestion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@app.post("/ingest/fitness", response_model=IngestResponse)
async def ingest_fitness(
    fitness_reports: List[FitnessInput],
    include_hourly: bool = False
):
    """
    Ingest fitness reports (daily/weekly/monthly).
    
    Creates summary chunks. Optionally creates hourly chunks if include_hourly=true.
    
    Note: Hourly chunks disabled by default to reduce index size.
    """
    if not fitness_reports:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty fitness reports list"
        )
    
    try:
        services = get_services()
        result = services["ingestion"].ingest_fitness(
            fitness_reports,
            include_hourly=include_hourly
        )
        return result
    except Exception as e:
        logger.error("Fitness ingestion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@app.post("/ingest/sleep", response_model=IngestResponse)
async def ingest_sleep(sleep_reports: List[SleepInput]):
    """
    Ingest sleep reports (daily/weekly/monthly).
    
    Creates one summary chunk per report.
    """
    if not sleep_reports:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty sleep reports list"
        )
    
    try:
        services = get_services()
        result = services["ingestion"].ingest_sleep(sleep_reports)
        return result
    except Exception as e:
        logger.error("Sleep ingestion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


# ============================================================================
# Query Endpoint (RAG)
# ============================================================================

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Execute RAG query over patient data.
    
    Workflow:
    1. Resolve person name to patient_id
    2. Embed query
    3. Vector search with metadata filters (patient_id, source, time range)
    4. Generate LLM answer from evidence
    
    Example:
    ```json
    {
      "person": "Raju",
      "question": "What did he eat on 2025-05-02?",
      "source": "meals",
      "from": "2025-05-02T00:00:00Z",
      "to": "2025-05-02T23:59:59Z",
      "top_k": 8
    }
    ```
    """
    try:
        services = get_services()
        result = services["retrieval"].query(request)
        return result
    except Exception as e:
        logger.error("Query execution failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


# ============================================================================
# Management Endpoints
# ============================================================================

@app.delete("/patient/{patient_id}")
async def delete_patient_data(patient_id: str):
    """
    Delete all data for a specific patient.
    
    Useful for re-ingestion or GDPR compliance.
    """
    try:
        services = get_services()
        services["qdrant"].delete_by_patient(patient_id)
        return {
            "status": "success",
            "message": f"Deleted all data for patient {patient_id}"
        }
    except Exception as e:
        logger.error("Patient deletion failed", patient_id=patient_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=1531,
        reload=True,
        log_level=settings.log_level.lower()
    )

