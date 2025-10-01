"""Embedding service using OpenAI."""

from typing import List
from openai import OpenAI
from config import settings
import structlog

logger = structlog.get_logger()


class EmbeddingService:
    """Service for generating embeddings using OpenAI."""
    
    def __init__(self):
        """Initialize OpenAI client with extended timeout."""
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=120.0,  # 2 minutes timeout
            max_retries=3   # Retry 3 times on failure
        )
        self.model = settings.openai_embedding_model
        self.batch_size = settings.embedding_batch_size
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Automatically batches requests if texts exceed batch_size.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If embedding generation fails
        """
        if not texts:
            return []
        
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        
        # Process in batches
        for batch_num, i in enumerate(range(0, len(texts), self.batch_size), 1):
            batch = texts[i:i + self.batch_size]
            
            try:
                logger.info(
                    "Generating embeddings",
                    batch=f"{batch_num}/{total_batches}",
                    texts_in_batch=len(batch),
                    total_texts=len(texts)
                )
                
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model,
                    timeout=120.0  # 2 minutes per batch
                )
                
                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(
                    "✓ Embeddings generated successfully",
                    batch=f"{batch_num}/{total_batches}",
                    batch_size=len(batch),
                    total_processed=len(all_embeddings)
                )
            
            except Exception as e:
                logger.error(
                    "Embedding generation failed",
                    batch_start=i,
                    batch_size=len(batch),
                    error=str(e)
                )
                raise
        
        return all_embeddings
    
    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []

