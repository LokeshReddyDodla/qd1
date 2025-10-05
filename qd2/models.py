"""Data models and schemas for the RAG system."""

from datetime import datetime, date
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, UUID4
from enum import Enum


# ============================================================================
# Enums for canonical types
# ============================================================================

class Source(str, Enum):
    """Data source types."""
    PROFILE = "profile"
    MEALS = "meals"
    FITNESS = "fitness"
    SLEEP = "sleep"
    CGM = "cgm"


class ReportType(str, Enum):
    """Report frequency types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Section(str, Enum):
    """Chunk section types."""
    SUMMARY = "summary"
    MEAL = "meal"
    RECOMMENDATION = "recommendation"
    HOUR = "hour"
    DISTRIBUTION = "distribution"
    INACTIVE = "inactive"


# ============================================================================
# Core payload model (stored in Qdrant)
# ============================================================================

class ChunkPayload(BaseModel):
    """Canonical payload for all Qdrant points."""
    
    patient_id: str = Field(..., description="Patient UUID")
    full_name: Optional[str] = Field(None, description="Patient full name")
    source: Source = Field(..., description="Data source")
    section: Section = Field(..., description="Chunk section type")
    report_type: Optional[ReportType] = Field(None, description="Report type")
    date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    start_ts: Optional[int] = Field(None, description="Start timestamp (UTC seconds)")
    end_ts: Optional[int] = Field(None, description="End timestamp (UTC seconds)")
    text: str = Field(..., description="Chunk content for embedding and display")
    
    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Ensure date is in YYYY-MM-DD format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}")
        return v
    
    model_config = {"use_enum_values": True}


# ============================================================================
# Input models for ingest endpoints
# ============================================================================

class ProfileInput(BaseModel):
    """Patient profile from Postgres."""
    
    patient_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[str] = None  # Can be date or string
    gender: Optional[str] = None
    height: Optional[float] = None  # cm
    waist: Optional[float] = None   # cm
    weight: Optional[float] = None  # kg
    email: Optional[str] = None
    phone_number: Optional[str] = None
    locale: Optional[str] = "Asia/Kolkata"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    profile_completion: Optional[Dict[str, Any]] = None


class MealInput(BaseModel):
    """Daily meal report from MongoDB."""
    
    patient_id: str
    report_type: Literal["daily"] = "daily"
    date: str  # YYYY-MM-DD
    meal_count: Optional[int] = 0
    calories: Optional[float] = None
    proteins: Optional[float] = None
    carbohydrates: Optional[float] = None
    fats: Optional[float] = None
    fiber: Optional[float] = None
    meals: List[Dict[str, Any]] = Field(default_factory=list)
    diet_recommendations: Optional[Dict[str, Any]] = None
    updated_at: Optional[Any] = None


class FitnessInput(BaseModel):
    """Fitness report (daily/weekly/monthly) from MongoDB."""
    
    patient_id: str
    report_type: Optional[ReportType] = "daily"  # Default to daily if not provided
    start_date: Optional[Any] = None  # Can be ISO string or MongoDB date object
    end_date: Optional[Any] = None    # Can be ISO string or MongoDB date object
    steps: Optional[int] = 0
    active_duration: Optional[int] = 0  # minutes
    peak_activity_time: Optional[Dict[str, Any]] = None
    activity_distribution: Optional[Dict[str, Any]] = None
    hourly_stats: Optional[List[Dict[str, Any]]] = None
    inactive_periods: Optional[List[Dict[str, Any]]] = None
    updated_at: Optional[Any] = None


class SleepInput(BaseModel):
    """Sleep report (daily/weekly/monthly) from MongoDB."""
    
    patient_id: str
    report_type: Optional[ReportType] = "daily"  # Default to daily if not provided
    start_date: Optional[Any] = None
    end_date: Optional[Any] = None
    quality_analysis: Optional[Dict[str, Any]] = None
    updated_at: Optional[Any] = None


# ============================================================================
# Output models for API responses
# ============================================================================

class IngestResponse(BaseModel):
    """Response from ingest endpoints."""
    
    accepted: int = Field(..., description="Number of documents accepted")
    indexed_points: int = Field(..., description="Number of points created in Qdrant")
    skipped: int = Field(0, description="Number of documents skipped")
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    batch_id: str = Field(..., description="Batch timestamp")


class EvidenceItem(BaseModel):
    """Single piece of evidence from vector search."""
    
    score: float = Field(..., description="Similarity score")
    payload: Dict[str, Any] = Field(..., description="Chunk metadata")
    text: Optional[str] = Field(None, description="Chunk text content")


class QueryRequest(BaseModel):
    """Request for RAG query."""
    
    person: Optional[str] = Field(None, description="Person name or patient_id (optional for cross-patient queries)")
    question: str = Field(..., description="Natural language question")
    source: Optional[Source] = Field(None, description="Filter by data source")
    from_time: Optional[str] = Field(None, alias="from", description="Start time (ISO8601)")
    to_time: Optional[str] = Field(None, alias="to", description="End time (ISO8601)")
    top_k: int = Field(10, description="Number of results to retrieve", ge=1, le=50)
    
    model_config = {"populate_by_name": True}


class QueryResponse(BaseModel):
    """Response from RAG query."""
    
    answer: str = Field(..., description="LLM-generated answer")
    evidence: List[EvidenceItem] = Field(..., description="Supporting evidence chunks")
    query_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Query execution metadata"
    )


# ============================================================================
# Internal processing models
# ============================================================================

class ProcessedChunk(BaseModel):
    """Internal representation of a chunk ready for embedding."""
    
    point_id: str = Field(..., description="Stable Qdrant point ID")
    payload: ChunkPayload = Field(..., description="Chunk metadata")
    vector: Optional[List[float]] = Field(None, description="Embedding vector")


class IngestionError(BaseModel):
    """Error during ingestion."""
    
    doc_index: int
    patient_id: Optional[str] = None
    reason: str
    source: Optional[Source] = None

