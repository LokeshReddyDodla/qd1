"""Ingestion pipeline for processing and indexing data."""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
from models import (
    ProfileInput, MealInput, FitnessInput, SleepInput,
    ProcessedChunk, IngestionError, Source
)
from models_cgm import CGMInput, CGMPayload
from cgm_utils import make_cgm_point_id, render_cgm_summary, cgm_to_payload
from chunkers import chunk_profile, chunk_meals, chunk_fitness, chunk_sleep
from embedding_service import EmbeddingService
from qdrant_client_wrapper import QdrantManager
from utils import is_valid_uuid
import structlog

logger = structlog.get_logger()


class IngestionPipeline:
    """Pipeline for ingesting and indexing patient data."""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        qdrant_manager: QdrantManager
    ):
        """
        Initialize ingestion pipeline.
        
        Args:
            embedding_service: Service for generating embeddings
            qdrant_manager: Qdrant client wrapper
        """
        self.embedding_service = embedding_service
        self.qdrant_manager = qdrant_manager
    
    def _validate_patient_id(self, patient_id: str, doc_index: int, source: Source) -> Tuple[bool, IngestionError | None]:
        """Validate patient_id format."""
        if not patient_id:
            return False, IngestionError(
                doc_index=doc_index,
                patient_id=None,
                reason="Missing patient_id",
                source=source
            )
        
        if not is_valid_uuid(patient_id):
            return False, IngestionError(
                doc_index=doc_index,
                patient_id=patient_id,
                reason=f"Invalid UUID format: {patient_id}",
                source=source
            )
        
        return True, None
    
    def ingest_profiles(self, profiles: List[ProfileInput]) -> Dict[str, Any]:
        """
        Ingest patient profiles.
        
        Args:
            profiles: List of ProfileInput models
            
        Returns:
            Ingestion report with counts and errors
        """
        logger.info("Starting profile ingestion", count=len(profiles))
        
        all_chunks: List[ProcessedChunk] = []
        errors: List[IngestionError] = []
        skipped = 0
        
        for idx, profile in enumerate(profiles):
            # Validate patient_id
            valid, error = self._validate_patient_id(
                profile.patient_id,
                idx,
                Source.PROFILE
            )
            if not valid:
                errors.append(error)
                skipped += 1
                continue
            
            try:
                # Chunk
                chunks = chunk_profile(profile)
                if not chunks:
                    skipped += 1
                    continue
                
                all_chunks.extend(chunks)
            
            except Exception as e:
                logger.error(
                    "Profile chunking failed",
                    doc_index=idx,
                    patient_id=profile.patient_id,
                    error=str(e)
                )
                errors.append(IngestionError(
                    doc_index=idx,
                    patient_id=profile.patient_id,
                    reason=f"Chunking error: {str(e)}",
                    source=Source.PROFILE
                ))
                skipped += 1
        
        # Embed and upsert
        indexed_points = self._embed_and_upsert(all_chunks, Source.PROFILE, errors)
        
        return {
            "accepted": len(profiles) - skipped,
            "indexed_points": indexed_points,
            "skipped": skipped,
            "errors": [err.model_dump() for err in errors],
            "batch_id": datetime.now(timezone.utc).isoformat()
        }
    
    def ingest_meals(self, meals: List[MealInput]) -> Dict[str, Any]:
        """
        Ingest meal reports.
        
        Args:
            meals: List of MealInput models
            
        Returns:
            Ingestion report
        """
        logger.info("Starting meals ingestion", count=len(meals))
        
        all_chunks: List[ProcessedChunk] = []
        errors: List[IngestionError] = []
        skipped = 0
        
        for idx, meal_data in enumerate(meals):
            valid, error = self._validate_patient_id(
                meal_data.patient_id,
                idx,
                Source.MEALS
            )
            if not valid:
                errors.append(error)
                skipped += 1
                continue
            
            try:
                chunks = chunk_meals(meal_data)
                if not chunks:
                    logger.warning(
                        "No chunks generated for meal",
                        doc_index=idx,
                        patient_id=meal_data.patient_id,
                        date=meal_data.date
                    )
                    skipped += 1
                    continue
                
                all_chunks.extend(chunks)
            
            except Exception as e:
                logger.error(
                    "Meal chunking failed",
                    doc_index=idx,
                    patient_id=meal_data.patient_id,
                    error=str(e)
                )
                errors.append(IngestionError(
                    doc_index=idx,
                    patient_id=meal_data.patient_id,
                    reason=f"Chunking error: {str(e)}",
                    source=Source.MEALS
                ))
                skipped += 1
        
        indexed_points = self._embed_and_upsert(all_chunks, Source.MEALS, errors)
        
        return {
            "accepted": len(meals) - skipped,
            "indexed_points": indexed_points,
            "skipped": skipped,
            "errors": [err.model_dump() for err in errors],
            "batch_id": datetime.now(timezone.utc).isoformat()
        }
    
    def ingest_fitness(
        self,
        fitness_reports: List[FitnessInput],
        include_hourly: bool = False
    ) -> Dict[str, Any]:
        """
        Ingest fitness reports.
        
        Args:
            fitness_reports: List of FitnessInput models
            include_hourly: Whether to create hourly chunks
            
        Returns:
            Ingestion report
        """
        logger.info(
            "Starting fitness ingestion",
            count=len(fitness_reports),
            include_hourly=include_hourly
        )
        
        all_chunks: List[ProcessedChunk] = []
        errors: List[IngestionError] = []
        skipped = 0
        
        for idx, fitness in enumerate(fitness_reports):
            valid, error = self._validate_patient_id(
                fitness.patient_id,
                idx,
                Source.FITNESS
            )
            if not valid:
                errors.append(error)
                skipped += 1
                continue
            
            try:
                chunks = chunk_fitness(fitness, include_hourly=include_hourly)
                if not chunks:
                    logger.warning(
                        "No chunks generated for fitness",
                        doc_index=idx,
                        patient_id=fitness.patient_id
                    )
                    skipped += 1
                    continue
                
                all_chunks.extend(chunks)
            
            except Exception as e:
                logger.error(
                    "Fitness chunking failed",
                    doc_index=idx,
                    patient_id=fitness.patient_id,
                    error=str(e)
                )
                errors.append(IngestionError(
                    doc_index=idx,
                    patient_id=fitness.patient_id,
                    reason=f"Chunking error: {str(e)}",
                    source=Source.FITNESS
                ))
                skipped += 1
        
        indexed_points = self._embed_and_upsert(all_chunks, Source.FITNESS, errors)
        
        return {
            "accepted": len(fitness_reports) - skipped,
            "indexed_points": indexed_points,
            "skipped": skipped,
            "errors": [err.model_dump() for err in errors],
            "batch_id": datetime.now(timezone.utc).isoformat()
        }
    
    def ingest_sleep(self, sleep_reports: List[SleepInput]) -> Dict[str, Any]:
        """
        Ingest sleep reports.
        
        Args:
            sleep_reports: List of SleepInput models
            
        Returns:
            Ingestion report
        """
        logger.info("Starting sleep ingestion", count=len(sleep_reports))
        
        all_chunks: List[ProcessedChunk] = []
        errors: List[IngestionError] = []
        skipped = 0
        
        for idx, sleep in enumerate(sleep_reports):
            valid, error = self._validate_patient_id(
                sleep.patient_id,
                idx,
                Source.SLEEP
            )
            if not valid:
                errors.append(error)
                skipped += 1
                continue
            
            try:
                chunks = chunk_sleep(sleep)
                if not chunks:
                    logger.warning(
                        "No chunks generated for sleep",
                        doc_index=idx,
                        patient_id=sleep.patient_id
                    )
                    skipped += 1
                    continue
                
                all_chunks.extend(chunks)
            
            except Exception as e:
                logger.error(
                    "Sleep chunking failed",
                    doc_index=idx,
                    patient_id=sleep.patient_id,
                    error=str(e)
                )
                errors.append(IngestionError(
                    doc_index=idx,
                    patient_id=sleep.patient_id,
                    reason=f"Chunking error: {str(e)}",
                    source=Source.SLEEP
                ))
                skipped += 1
        
        indexed_points = self._embed_and_upsert(all_chunks, Source.SLEEP, errors)
        
        return {
            "accepted": len(sleep_reports) - skipped,
            "indexed_points": indexed_points,
            "skipped": skipped,
            "errors": [err.model_dump() for err in errors],
            "batch_id": datetime.now(timezone.utc).isoformat()
        }
    
    def ingest_cgm(self, cgm_reports: List[CGMInput]) -> Dict[str, Any]:
        """
        Ingest CGM (Continuous Glucose Monitoring) reports.
        
        Args:
            cgm_reports: List of CGMInput models
            
        Returns:
            Ingestion report
        """
        logger.info("Starting CGM ingestion", count=len(cgm_reports))
        
        errors: List[IngestionError] = []
        skipped = 0
        point_ids = []
        
        for idx, cgm in enumerate(cgm_reports):
            # Validate patient_id
            valid, error = self._validate_patient_id(
                cgm.patient_id,
                idx,
                Source.CGM
            )
            if not valid:
                errors.append(error)
                skipped += 1
                continue
            
            try:
                # Generate point ID
                point_id = make_cgm_point_id(
                    cgm.patient_id,
                    cgm.report_type,
                    cgm.start_date,
                    cgm.end_date
                )
                
                # Render summary text
                summary_text = render_cgm_summary(cgm)
                
                # Create payload
                payload = cgm_to_payload(cgm, summary_text)
                
                # Embed summary
                try:
                    vector = self.embedding_service.embed_single(summary_text)
                except Exception as e:
                    logger.error(
                        "CGM embedding failed",
                        doc_index=idx,
                        patient_id=cgm.patient_id,
                        error=str(e)
                    )
                    errors.append(IngestionError(
                        doc_index=idx,
                        patient_id=cgm.patient_id,
                        reason=f"Embedding error: {str(e)}",
                        source=Source.CGM
                    ))
                    skipped += 1
                    continue
                
                # Upsert to Qdrant
                self.qdrant_manager.upsert_cgm_point(
                    point_id=point_id,
                    vector=vector,
                    payload=payload.model_dump(mode="json", exclude_none=False)
                )
                
                point_ids.append(point_id)
                
                logger.info(
                    "CGM report ingested",
                    doc_index=idx,
                    patient_id=cgm.patient_id,
                    point_id=point_id,
                    report_type=cgm.report_type
                )
            
            except Exception as e:
                logger.error(
                    "CGM ingestion failed",
                    doc_index=idx,
                    patient_id=cgm.patient_id,
                    error=str(e)
                )
                errors.append(IngestionError(
                    doc_index=idx,
                    patient_id=cgm.patient_id,
                    reason=f"Ingestion error: {str(e)}",
                    source=Source.CGM
                ))
                skipped += 1
        
        return {
            "accepted": len(cgm_reports) - skipped,
            "indexed_points": len(point_ids),
            "skipped": skipped,
            "errors": [err.model_dump() for err in errors],
            "batch_id": datetime.now(timezone.utc).isoformat(),
            "point_ids": point_ids[:10]  # Return first 10 for reference
        }
    
    def _embed_and_upsert(
        self,
        chunks: List[ProcessedChunk],
        source: Source,
        errors: List[IngestionError]
    ) -> int:
        """
        Embed chunk texts and upsert to Qdrant.
        
        Args:
            chunks: List of chunks to process
            source: Data source
            errors: List to append embedding errors to
            
        Returns:
            Number of points indexed
        """
        if not chunks:
            return 0
        
        try:
            # Extract texts for embedding
            texts = [chunk.payload.text for chunk in chunks]
            
            logger.info(
                "Starting embedding generation",
                source=source.value,
                total_chunks=len(texts),
                estimated_batches=(len(texts) + 31) // 32
            )
            
            # Generate embeddings (this may take a while for large datasets)
            vectors = self.embedding_service.embed_texts(texts)
            
            if len(vectors) != len(chunks):
                logger.error(
                    "Embedding count mismatch",
                    expected=len(chunks),
                    received=len(vectors)
                )
                errors.append(IngestionError(
                    doc_index=-1,
                    patient_id=None,
                    reason=f"Embedding count mismatch: expected {len(chunks)}, got {len(vectors)}",
                    source=source
                ))
                return 0
            
            logger.info("All embeddings generated successfully", total=len(vectors))
            
            # Attach vectors to chunks
            for chunk, vector in zip(chunks, vectors):
                chunk.vector = vector
            
            logger.info("Upserting to Qdrant", chunks_count=len(chunks))
            
            # Upsert to Qdrant
            indexed = self.qdrant_manager.upsert_chunks(chunks)
            
            logger.info(
                "Successfully indexed chunks",
                source=source.value,
                indexed=indexed
            )
            
            return indexed
        
        except Exception as e:
            logger.error(
                "Embedding/upsert failed",
                source=source.value,
                error=str(e)
            )
            errors.append(IngestionError(
                doc_index=-1,
                patient_id=None,
                reason=f"Embedding/upsert error: {str(e)}",
                source=source
            ))
            return 0

