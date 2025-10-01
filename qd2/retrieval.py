"""Retrieval workflow for RAG queries."""

from typing import Optional, Dict, Any, List
from models import QueryRequest, QueryResponse, EvidenceItem, Source
from embedding_service import EmbeddingService
from qdrant_client_wrapper import QdrantManager
from llm_service import LLMService
from utils import parse_to_utc_seconds
#import psycopg2
from config import settings
import structlog

logger = structlog.get_logger()


class RetrievalService:
    """Service for executing RAG retrieval workflows."""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        qdrant_manager: QdrantManager,
        llm_service: LLMService
    ):
        """
        Initialize retrieval service.
        
        Args:
            embedding_service: Service for generating embeddings
            qdrant_manager: Qdrant client wrapper
            llm_service: LLM service for answer generation
        """
        self.embedding_service = embedding_service
        self.qdrant_manager = qdrant_manager
        self.llm_service = llm_service
    
    def resolve_person_to_patient_id(self, person: str) -> Optional[str]:
        """
        Resolve person name or patient_id to patient_id.
        
        Tries:
        1. If input looks like UUID, return as-is
        2. (PostgreSQL name lookup disabled - psycopg2 not installed)
        
        Note: Without PostgreSQL, you must provide the patient_id directly (UUID format).
        To enable name resolution, install psycopg2 and uncomment the database code below.
        
        Args:
            person: Person name or patient_id
            
        Returns:
            patient_id UUID string or None
        """
        person = person.strip()
        
        # Check if already a UUID
        from utils import is_valid_uuid
        if is_valid_uuid(person):
            return person
        
        # Search Qdrant for profile data matching the name
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            # Scroll through profile records to find matching name
            results = self.qdrant_manager.client.scroll(
                collection_name=self.qdrant_manager.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source",
                            match=MatchValue(value="profile")
                        )
                    ]
                ),
                limit=1000,  # Get up to 1000 profiles
                with_payload=True,
                with_vectors=False
            )
            
            # Normalize search name for comparison
            search_name = person.lower().strip()
            
            # Search through profile text for matching names
            for point in results[0]:
                payload = point.payload
                text = payload.get("text", "").lower()
                patient_id = payload.get("patient_id")
                
                # Check if the search name appears in the profile text
                # Profile text format: "Profile for {full_name} (ID: {patient_id}):"
                if f"profile for {search_name}" in text:
                    logger.info(
                        "Name resolved to patient_id",
                        person=person,
                        patient_id=patient_id
                    )
                    return patient_id
                
                # Also check if it's a partial match (first name or last name)
                # Extract name from text: "Profile for {name} (ID:"
                if "profile for " in text and " (id:" in text:
                    start = text.find("profile for ") + len("profile for ")
                    end = text.find(" (id:", start)
                    if start < end:
                        full_name = text[start:end].strip()
                        # Check if search name matches any part of the full name
                        name_parts = full_name.split()
                        search_parts = search_name.split()
                        
                        # Match if any search part matches any name part
                        if any(search_part in name_part or name_part in search_part 
                               for search_part in search_parts 
                               for name_part in name_parts):
                            logger.info(
                                "Name partially resolved to patient_id",
                                person=person,
                                matched_name=full_name,
                                patient_id=patient_id
                            )
                            return patient_id
            
            logger.warning(
                "Person not found in profile data",
                person=person,
                hint="Make sure profile data is ingested and name spelling is correct"
            )
            return None
            
        except Exception as e:
            logger.error("Name resolution failed", person=person, error=str(e))
            return None
        
        # === PostgreSQL name lookup code (disabled) ===
        # Uncomment this section after installing psycopg2-binary
        
        # try:
        #     import psycopg2
        #     conn = psycopg2.connect(settings.postgres_dsn)
        #     cur = conn.cursor()
        #     
        #     # Case-insensitive name search
        #     query = """
        #         SELECT patient_id FROM patients
        #         WHERE LOWER(TRIM(first_name) || ' ' || TRIM(last_name)) = LOWER(%s)
        #         OR LOWER(TRIM(first_name)) = LOWER(%s)
        #         OR LOWER(TRIM(last_name)) = LOWER(%s)
        #         LIMIT 1
        #     """
        #     
        #     cur.execute(query, (person, person, person))
        #     result = cur.fetchone()
        #     
        #     cur.close()
        #     conn.close()
        #     
        #     if result:
        #         return str(result[0])
        #     else:
        #         logger.warning("Person not found in database", person=person)
        #         return None
        # 
        # except Exception as e:
        #     logger.error("Person resolution failed", person=person, error=str(e))
        #     return None
    
    def query(self, request: QueryRequest) -> QueryResponse:
        """
        Execute RAG query workflow.
        
        Steps:
        1. Resolve person name to patient_id (optional - if not provided, searches all patients)
        2. Build metadata filter
        3. Embed query
        4. Vector search with filters
        5. Generate LLM answer from evidence
        
        Args:
            request: QueryRequest with question and filters
            
        Returns:
            QueryResponse with answer and evidence
        """
        # Step 1: Resolve person (optional for cross-patient queries)
        patient_id = None
        if request.person:
            patient_id = self.resolve_person_to_patient_id(request.person)
            
            if not patient_id:
                return QueryResponse(
                    answer=f"Could not find patient '{request.person}'. Please provide the patient_id directly (UUID format). Name resolution requires PostgreSQL with psycopg2 installed.",
                    evidence=[],
                    query_metadata={
                        "person": request.person,
                        "resolved_patient_id": None,
                        "error": "Person not found - use patient_id (UUID) directly"
                    }
                )
            
            logger.info(
                "Resolved person to patient_id",
                person=request.person,
                patient_id=patient_id
            )
        else:
            logger.info("Cross-patient query (no person specified)")
        
        # Step 2: Parse time filters
        start_ts = None
        end_ts = None
        
        if request.from_time:
            start_ts = parse_to_utc_seconds(request.from_time)
        if request.to_time:
            end_ts = parse_to_utc_seconds(request.to_time)
        
        # Step 3: Embed query
        try:
            query_vector = self.embedding_service.embed_single(request.question)
        except Exception as e:
            logger.error("Query embedding failed", error=str(e))
            return QueryResponse(
                answer=f"Error processing query: {str(e)}",
                evidence=[],
                query_metadata={
                    "person": request.person,
                    "patient_id": patient_id,
                    "error": "Embedding failed"
                }
            )
        
        # Step 4: Vector search
        search_results = self.qdrant_manager.search(
            query_vector=query_vector,
            patient_id=patient_id,
            source=request.source,
            start_ts=start_ts,
            end_ts=end_ts,
            limit=request.top_k
        )
        
        # Step 5: Format evidence
        evidence = []
        for result in search_results:
            evidence.append(
                EvidenceItem(
                    score=result["score"],
                    payload=result["payload"],
                    text=result["payload"].get("text")
                )
            )
        
        # Step 6: Generate answer
        if not evidence:
            if request.person:
                answer = f"I don't have any data for {request.person} matching your query."
            else:
                answer = "I don't have any data matching your query criteria."
        else:
            person_name = request.person if request.person else "any patient"
            answer = self.llm_service.generate_answer(
                question=request.question,
                evidence=[{"payload": e.payload} for e in evidence],
                person_name=person_name
            )
        
        # Build metadata
        query_metadata = {
            "person": request.person,
            "resolved_patient_id": patient_id,
            "source_filter": request.source.value if request.source else None,
            "time_range": {
                "from": request.from_time,
                "to": request.to_time
            } if request.from_time or request.to_time else None,
            "results_count": len(evidence)
        }
        
        return QueryResponse(
            answer=answer,
            evidence=evidence,
            query_metadata=query_metadata
        )

