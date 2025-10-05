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
    
    def _is_cross_domain_query(self, question: str) -> bool:
        """
        Detect if question mentions multiple data sources.
        
        Args:
            question: User's question
            
        Returns:
            True if question mentions multiple sources
        """
        question_lower = question.lower()
        
        # Keywords for each source
        source_keywords = {
            'meals': ['meal', 'food', 'eat', 'diet', 'nutrition', 'calorie', 'protein', 'carb', 'fat', 'breakfast', 'lunch', 'dinner', 'snack'],
            'fitness': ['step', 'walk', 'exercise', 'active', 'activity', 'fitness', 'movement', 'physical'],
            'sleep': ['sleep', 'rest', 'wake', 'dream', 'insomnia', 'nap'],
            'profile': ['age', 'height', 'weight', 'bmi', 'gender', 'profile', 'demographic'],
            'cgm': ['glucose', 'blood sugar', 'cgm', 'hyper', 'hypo', 'glycemia', 'gmi', 'time in range', 'tir', 'a1c', 'diabete']
        }
        
        # Count how many sources are mentioned
        sources_found = set()
        for source, keywords in source_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                sources_found.add(source)
        
        return len(sources_found) > 1
    
    def _detect_mentioned_sources(self, question: str) -> List[Source]:
        """
        Detect which specific data sources are mentioned in the question.
        
        Args:
            question: User's question
            
        Returns:
            List of Source enums
        """
        question_lower = question.lower()
        mentioned = []
        
        # Check for meals
        if any(word in question_lower for word in ['meal', 'food', 'eat', 'diet', 'nutrition', 'calorie', 'protein', 'carb', 'fat']):
            mentioned.append(Source.MEALS)
        
        # Check for fitness
        if any(word in question_lower for word in ['step', 'walk', 'exercise', 'active', 'activity', 'fitness', 'movement']):
            mentioned.append(Source.FITNESS)
        
        # Check for sleep
        if any(word in question_lower for word in ['sleep', 'rest', 'wake', 'dream']):
            mentioned.append(Source.SLEEP)
        
        # Check for profile
        if any(word in question_lower for word in ['age', 'height', 'weight', 'bmi', 'gender', 'profile']):
            mentioned.append(Source.PROFILE)
        
        # Check for CGM
        if any(word in question_lower for word in ['glucose', 'blood sugar', 'cgm', 'hyper', 'hypo', 'glycemia', 'gmi', 'time in range', 'tir', 'a1c', 'diabete']):
            mentioned.append(Source.CGM)
        
        return mentioned
    
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
    
    def _extract_patient_id_from_question(self, question: str) -> Optional[str]:
        """
        Extract patient_id (UUID) from question text.
        
        Args:
            question: User's question text
            
        Returns:
            Patient ID if found, None otherwise
        """
        import re
        from utils import is_valid_uuid
        
        # Look for UUID pattern in the question
        # UUID format: 8-4-4-4-12 hexadecimal characters
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        matches = re.findall(uuid_pattern, question.lower())
        
        if matches:
            # Return the first valid UUID found
            for match in matches:
                if is_valid_uuid(match):
                    logger.info(
                        "Extracted patient_id from question",
                        patient_id=match,
                        question=question[:100]
                    )
                    return match
        
        return None
    
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
        logger.info(
            "Query request received",
            person=request.person,
            question=request.question[:100] if request.question else None,
            source=request.source,
            from_time=request.from_time,
            to_time=request.to_time
        )
        
        if request.person:
            patient_id = self.resolve_person_to_patient_id(request.person)
            
            if not patient_id:
                logger.warning(
                    "Person not found",
                    person=request.person,
                    hint="Use exact patient_id (UUID) or check profile data ingestion"
                )
                return QueryResponse(
                    answer=f"Could not find patient '{request.person}'. Please provide the patient_id directly (UUID format), or check that profile data with this name has been ingested.",
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
            # Try to extract patient_id from question text if person field is empty
            extracted_id = self._extract_patient_id_from_question(request.question)
            if extracted_id:
                patient_id = extracted_id
                logger.info(
                    "Using patient_id extracted from question",
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
        # For cross-domain queries (no source filter), detect if question mentions multiple sources
        # and retrieve from each source separately to ensure balanced results
        search_results = []
        
        if not request.source and self._is_cross_domain_query(request.question):
            # Detect which sources are mentioned in the question
            mentioned_sources = self._detect_mentioned_sources(request.question)
            
            if len(mentioned_sources) > 1:
                # Retrieve from each source separately
                logger.info(
                    "Cross-domain query detected",
                    sources=mentioned_sources,
                    strategy="multi-source retrieval"
                )
                
                per_source_limit = max(3, request.top_k // len(mentioned_sources))
                
                for source in mentioned_sources:
                    source_results = self.qdrant_manager.search(
                        query_vector=query_vector,
                        patient_id=patient_id,
                        source=source,
                        start_ts=start_ts,
                        end_ts=end_ts,
                        limit=per_source_limit
                    )
                    search_results.extend(source_results)
                
                # Sort by score and limit to top_k
                search_results.sort(key=lambda x: x["score"], reverse=True)
                search_results = search_results[:request.top_k]
            else:
                # Single domain query - normal search
                search_results = self.qdrant_manager.search(
                    query_vector=query_vector,
                    patient_id=patient_id,
                    source=request.source,
                    start_ts=start_ts,
                    end_ts=end_ts,
                    limit=request.top_k
                )
        else:
            # Source filter specified or not a cross-domain query - normal search
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
        
        # Log evidence retrieval details
        logger.info(
            "Evidence retrieved",
            count=len(evidence),
            sources=[e.payload.get("source") for e in evidence[:5]] if evidence else [],
            dates=[e.payload.get("date") for e in evidence[:5]] if evidence else []
        )
        
        # Step 6: Generate answer
        if not evidence:
            if request.person:
                answer = f"I don't have any data for {request.person} matching your query."
            else:
                answer = "I don't have any data matching your query criteria."
        else:
            person_name = request.person if request.person else "any patient"
            # Use all evidence (up to 50) for LLM to generate comprehensive answer
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
            "results_count": len(evidence),
            "displayed_evidence_count": min(5, len(evidence))
        }
        
        # Return only top 5 evidence items for display, but LLM used all available chunks
        return QueryResponse(
            answer=answer,
            evidence=evidence[:5],  # Display only top 5 evidence items
            query_metadata=query_metadata
        )

