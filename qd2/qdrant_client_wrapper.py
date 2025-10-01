"""Qdrant client wrapper with collection management."""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue, Range,
    PayloadSchemaType, CreateCollection
)
from models import ProcessedChunk, Source
from config import settings
import structlog
import uuid

logger = structlog.get_logger()


def stable_id_to_uuid(stable_id: str) -> str:
    """
    Convert a stable string ID to a deterministic UUID.
    
    Uses UUID v5 (SHA-1 hashing) to generate a valid UUID from any string.
    Same input always produces the same UUID (idempotent).
    
    Args:
        stable_id: String ID like "meals:patient-id:2025-05-02:summary"
        
    Returns:
        UUID string
    """
    # Use a namespace UUID (can be any valid UUID)
    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
    return str(uuid.uuid5(namespace, stable_id))


class QdrantManager:
    """Manages Qdrant collection and operations."""
    
    def __init__(self):
        """Initialize Qdrant client with extended timeout."""
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            timeout=300  # 5 minutes timeout for large batches
        )
        self.collection_name = settings.qdrant_collection_name
        self.vector_size = settings.qdrant_vector_size
    
    def ensure_collection_exists(self) -> None:
        """
        Create collection if it doesn't exist.
        
        Collection config:
        - Vectors: 1536-dim (OpenAI text-embedding-3-small)
        - Distance: COSINE
        """
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.collection_name not in collection_names:
            logger.info(
                "Creating Qdrant collection",
                collection=self.collection_name,
                vector_size=self.vector_size
            )
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            
            logger.info("Collection created successfully")
        else:
            logger.info("Collection already exists", collection=self.collection_name)
    
    def create_payload_indexes(self) -> None:
        """
        Create payload indexes for performance.
        
        Indexes:
        - patient_id (keyword)
        - source (keyword)
        - report_type (keyword)
        - date (keyword)
        - start_ts, end_ts (integer range)
        - section (keyword)
        """
        indexes = [
            ("patient_id", PayloadSchemaType.KEYWORD),
            ("source", PayloadSchemaType.KEYWORD),
            ("report_type", PayloadSchemaType.KEYWORD),
            ("date", PayloadSchemaType.KEYWORD),
            ("section", PayloadSchemaType.KEYWORD),
            ("start_ts", PayloadSchemaType.INTEGER),
            ("end_ts", PayloadSchemaType.INTEGER),
        ]
        
        for field_name, schema_type in indexes:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=schema_type
                )
                logger.info("Created payload index", field=field_name)
            except Exception as e:
                # Index might already exist
                logger.debug("Payload index creation skipped", field=field_name, error=str(e))
    
    def upsert_chunks(self, chunks: List[ProcessedChunk]) -> int:
        """
        Upsert chunks to Qdrant.
        
        Args:
            chunks: List of ProcessedChunk with vectors
            
        Returns:
            Number of points upserted
        """
        if not chunks:
            return 0
        
        points = []
        for chunk in chunks:
            if chunk.vector is None:
                logger.warning("Skipping chunk without vector", point_id=chunk.point_id)
                continue
            
            # Convert stable string ID to UUID for Qdrant compatibility
            point_uuid = stable_id_to_uuid(chunk.point_id)
            
            # Store original stable_id in payload for reference
            payload = chunk.payload.model_dump(mode="json", exclude_none=False)
            payload['_stable_id'] = chunk.point_id  # Keep original ID for debugging
            
            point = PointStruct(
                id=point_uuid,
                vector=chunk.vector,
                payload=payload
            )
            points.append(point)
        
        if not points:
            return 0
        
        # Batch upsert for large datasets to avoid timeout
        batch_size = 100
        total_upserted = 0
        
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(points) + batch_size - 1) // batch_size
            
            logger.info(
                "Upserting batch to Qdrant",
                batch=f"{batch_num}/{total_batches}",
                points_in_batch=len(batch),
                total_points=len(points)
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            
            total_upserted += len(batch)
            
            logger.info(
                "✓ Batch upserted successfully",
                batch=f"{batch_num}/{total_batches}",
                total_upserted=total_upserted
            )
        
        logger.info("All points upserted to Qdrant", total_count=total_upserted)
        return total_upserted
    
    def search(
        self,
        query_vector: List[float],
        patient_id: Optional[str] = None,
        source: Optional[Source] = None,
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search Qdrant with metadata filters.
        
        Args:
            query_vector: Embedded query vector
            patient_id: Patient UUID (optional - if None, searches all patients)
            source: Optional source filter
            start_ts: Optional start timestamp filter
            end_ts: Optional end timestamp filter
            limit: Number of results
            
        Returns:
            List of search results with score and payload
        """
        # Build filter conditions
        must_conditions = []
        
        # Add patient_id filter only if provided
        if patient_id:
            must_conditions.append(
                FieldCondition(
                    key="patient_id",
                    match=MatchValue(value=patient_id)
                )
            )
        
        if source:
            must_conditions.append(
                FieldCondition(
                    key="source",
                    match=MatchValue(value=source.value)
                )
            )
        
        # Time range filter
        if start_ts is not None and end_ts is not None:
            # Documents where start_ts >= query_start AND end_ts <= query_end
            must_conditions.append(
                FieldCondition(
                    key="start_ts",
                    range=Range(gte=start_ts)
                )
            )
            must_conditions.append(
                FieldCondition(
                    key="end_ts",
                    range=Range(lte=end_ts)
                )
            )
        
        # Only apply filter if there are conditions
        query_filter = Filter(must=must_conditions) if must_conditions else None
        
        # Execute search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "score": result.score,
                "payload": result.payload,
                "id": result.id
            })
        
        logger.info(
            "Search completed",
            results_count=len(formatted_results),
            patient_id=patient_id if patient_id else "all_patients",
            source=source.value if source else None
        )
        
        return formatted_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error("Failed to get collection info", error=str(e))
            return {}
    
    def delete_by_patient(self, patient_id: str) -> None:
        """Delete all points for a patient (useful for re-ingestion)."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="patient_id",
                        match=MatchValue(value=patient_id)
                    )
                ]
            )
        )
        logger.info("Deleted all points for patient", patient_id=patient_id)
    
    def count_by_source(self, patient_id: str, source: Source) -> int:
        """Count points for a patient and source."""
        result = self.client.count(
            collection_name=self.collection_name,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="patient_id",
                        match=MatchValue(value=patient_id)
                    ),
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source.value)
                    )
                ]
            )
        )
        return result.count

