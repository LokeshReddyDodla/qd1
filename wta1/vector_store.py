# vector_store.py
import os
import base64
import chromadb
from chromadb.config import Settings
import fitz  # PyMuPDF for PDF processing
import numpy as np
from typing import List, Dict, Any, Optional
from openai import OpenAI
from PIL import Image
import io
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VectorStore:
    """
    Vector store implementation using ChromaDB for storing and retrieving
    vectorized content from PDFs and images for RAG functionality.
    """

    def __init__(self, collection_name: str = "fitness_docs", persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client and collection.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the database
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Ensure persist directory exists
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(name=collection_name)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using OpenAI's vision model.

        Args:
            image_path: Path to the image file

        Returns:
            Extracted text content
        """
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Use OpenAI vision model to extract text
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all the text content from this image. Return only the text, no explanations."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error extracting text from image {image_path}: {e}")
            return ""

    def extract_text_from_base64_image(self, base64_string: str, image_format: str = "jpeg") -> str:
        """
        Extract text from a base64 encoded image.

        Args:
            base64_string: Base64 encoded image data
            image_format: Image format (jpeg, png, etc.)

        Returns:
            Extracted text content
        """
        try:
            # Use OpenAI vision model to extract text
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all the text content from this image. Return only the text, no explanations."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/{image_format};base64,{base64_string}"}
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error extracting text from base64 image: {e}")
            return ""

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for text using OpenAI's embedding model.

        Args:
            text: Text to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks for better retrieval.

        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # If we're not at the end, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence endings
                sentence_endings = ['. ', '! ', '? ', '\n\n']
                best_break = end

                for ending in sentence_endings:
                    last_ending = text.rfind(ending, start, end)
                    if last_ending != -1 and last_ending > best_break - 100:
                        best_break = last_ending + len(ending)
                        break

                # If no good sentence break, look for word boundaries
                if best_break == end:
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1:
                        best_break = last_space + 1

                end = best_break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap
            if start >= len(text):
                break

        return chunks

    def add_document(self, file_path: str, user_id: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Process and add a document (PDF or image) to the vector store.

        Args:
            file_path: Path to the file to process
            user_id: User identifier for the document
            metadata: Additional metadata for the document

        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine file type and extract text
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.pdf':
                text = self.extract_text_from_pdf(file_path)
                doc_type = "pdf"
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                text = self.extract_text_from_image(file_path)
                doc_type = "image"
            else:
                print(f"Unsupported file type: {file_extension}")
                return False

            if not text:
                print(f"No text extracted from {file_path}")
                return False

            # Chunk the text
            chunks = self.chunk_text(text)

            if not chunks:
                print("No chunks generated from text")
                return False

            # Generate embeddings and add to collection
            ids = []
            embeddings = []
            documents = []
            metadatas = []

            # Detect InBody documents for better indexing
            is_inbody = False
            if doc_type == "pdf":
                # Check if filename suggests InBody report
                filename_lower = os.path.basename(file_path).lower()
                if any(keyword in filename_lower for keyword in ['inbody', 'body', 'composition', 'analysis', 'assessment']):
                    is_inbody = True
            elif doc_type == "image":
                # For images, we'll assume they might be InBody unless specified otherwise
                is_inbody = True

            # Determine the display filename
            if metadata and metadata.get("custom_filename"):
                display_filename = f"{metadata['custom_filename']}{os.path.splitext(os.path.basename(file_path))[1]}"
            else:
                display_filename = os.path.basename(file_path)

            base_metadata = {
                "user_id": user_id,
                "doc_type": doc_type,
                "file_path": file_path,
                "file_name": display_filename,
                "original_filename": os.path.basename(file_path) if metadata and metadata.get("custom_filename") else None,
                "is_inbody_report": is_inbody,
                "document_category": "inbody_analysis" if is_inbody else "general_health",
                "upload_date": datetime.now().isoformat(),
                **(metadata or {})
            }

            for i, chunk in enumerate(chunks):
                # Create unique ID for each chunk using display filename
                safe_filename = display_filename.replace(' ', '_').replace('.', '_')
                chunk_id = f"{user_id}_{safe_filename}_{i}_{hashlib.md5(chunk.encode()).hexdigest()[:8]}"

                # Generate embedding
                embedding = self.get_embedding(chunk)
                if not embedding:
                    continue

                ids.append(chunk_id)
                embeddings.append(embedding)
                documents.append(chunk)
                metadatas.append({
                    **base_metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })

            if ids:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"Successfully added {len(ids)} chunks from {file_path}")
                return True
            else:
                print("No valid embeddings generated")
                return False

        except Exception as e:
            print(f"Error adding document {file_path}: {e}")
            return False

    def add_base64_image(self, base64_string: str, user_id: str, image_format: str = "jpeg",
                        metadata: Dict[str, Any] = None) -> bool:
        """
        Process and add a base64 encoded image to the vector store.

        Args:
            base64_string: Base64 encoded image data
            user_id: User identifier
            image_format: Image format (jpeg, png, etc.)
            metadata: Additional metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract text from base64 image
            text = self.extract_text_from_base64_image(base64_string, image_format)

            if not text:
                print("No text extracted from base64 image")
                return False

            # Chunk the text
            chunks = self.chunk_text(text)

            if not chunks:
                print("No chunks generated from image text")
                return False

            # Generate embeddings and add to collection
            ids = []
            embeddings = []
            documents = []
            metadatas = []

            base_metadata = {
                "user_id": user_id,
                "doc_type": "image_base64",
                "image_format": image_format,
                **(metadata or {})
            }

            for i, chunk in enumerate(chunks):
                # Create unique ID for each chunk
                chunk_id = f"{user_id}_base64_image_{i}_{hashlib.md5(chunk.encode()).hexdigest()[:8]}"

                # Generate embedding
                embedding = self.get_embedding(chunk)
                if not embedding:
                    continue

                ids.append(chunk_id)
                embeddings.append(embedding)
                documents.append(chunk)
                metadatas.append({
                    **base_metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })

            if ids:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                print(f"Successfully added {len(ids)} chunks from base64 image")
                return True
            else:
                print("No valid embeddings generated from base64 image")
                return False

        except Exception as e:
            print(f"Error adding base64 image: {e}")
            return False

    def search_similar(self, query: str, user_id: str = None, n_results: int = 5,
                      metadata_filter: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search for similar documents using vector similarity.

        Args:
            query: Search query
            user_id: Filter by user ID (optional)
            n_results: Number of results to return
            metadata_filter: Additional metadata filters

        Returns:
            Dictionary containing search results
        """
        try:
            # Generate embedding for query
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return {"documents": [], "metadatas": [], "distances": []}

            # Build where clause for filtering
            where_clause = {}
            if user_id:
                where_clause["user_id"] = user_id
            if metadata_filter:
                where_clause.update(metadata_filter)

            # Search the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None
            )

            return results

        except Exception as e:
            print(f"Error searching documents: {e}")
            return {"documents": [], "metadatas": [], "distances": []}

    def get_context(self, user_id: str, query: str, k: int = 6) -> str:
        """
        Get relevant context for a query (used by the coach agent).

        Args:
            user_id: User identifier
            query: Search query
            k: Number of results to retrieve

        Returns:
            Concatenated context from similar documents
        """
        results = self.search_similar(query, user_id, k)

        if not results["documents"]:
            return ""

        # Combine the most relevant chunks
        context_parts = []
        for doc in results["documents"][0]:
            context_parts.append(doc)

        return "\n\n".join(context_parts)

    def get_inbody_context(self, user_id: str, k: int = 8) -> str:
        """
        Get InBody-specific context from uploaded documents.

        Args:
            user_id: User identifier
            k: Number of results to retrieve

        Returns:
            Concatenated InBody-related context
        """
        try:
            # Query specifically for InBody content
            inbody_query = "InBody analysis body composition BMI body fat percentage muscle mass metabolic rate body water waist-hip ratio visceral fat phase angle skeletal muscle mass health score fitness assessment"

            # Generate embedding for query
            query_embedding = self.get_embedding(inbody_query)
            if not query_embedding:
                return ""

            # Search for InBody documents - ChromaDB doesn't support complex $or queries
            # First try to find InBody-specific documents using AND condition
            inbody_where = {
                "$and": [
                    {"user_id": {"$eq": user_id}},
                    {"is_inbody_report": {"$eq": True}}
                ]
            }
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=inbody_where
            )

            # If no InBody-specific results, try category-based search
            if not results["documents"] or len(results["documents"][0]) == 0:
                category_where = {
                    "$and": [
                        {"user_id": {"$eq": user_id}},
                        {"document_category": {"$eq": "inbody_analysis"}}
                    ]
                }
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    where=category_where
                )

            # If still no results, try broader search
            if not results["documents"] or len(results["documents"][0]) == 0:
                broader_where = {"user_id": user_id}
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    where=broader_where
                )

            if not results["documents"]:
                return ""

            # Combine the most relevant chunks
            context_parts = []
            for doc in results["documents"][0]:
                context_parts.append(doc)

            return "\n\n".join(context_parts)

        except Exception as e:
            print(f"Error getting InBody context: {e}")
            return ""

    def get_selected_documents_context(self, user_id: str, selected_doc_ids: list, k: int = 8) -> str:
        """
        Get context from specifically selected documents.

        Args:
            user_id: User identifier
            selected_doc_ids: List of selected document IDs
            k: Number of results to retrieve

        Returns:
            Concatenated context from selected documents
        """
        try:
            if not selected_doc_ids:
                return ""
            
            # Query for general analysis content from selected documents
            query = "health analysis medical data body composition fitness assessment"

            # Generate embedding for query
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return ""

            # Get chunks from all selected documents
            all_chunks = []
            for doc_id in selected_doc_ids:
                # Extract the file_name from the document_id
                # document_id format is: {user_id}_{safe_filename}
                if doc_id.startswith(f"{user_id}_"):
                    # Remove user_id prefix and convert back to filename
                    safe_filename = doc_id[len(f"{user_id}_"):]
                    # Convert safe filename back to display filename (approximate)
                    file_name_parts = safe_filename.split('_')
                    
                    # Try to find chunks that belong to this document
                    # We'll search for chunks that have this document's filename pattern
                    doc_chunks = self.collection.get(
                        where={"user_id": user_id}
                    )
                    
                    if doc_chunks["metadatas"]:
                        for i, metadata in enumerate(doc_chunks["metadatas"]):
                            # Check if this chunk belongs to the selected document
                            if metadata.get("file_name") and doc_id in doc_chunks["ids"][i]:
                                all_chunks.append(doc_chunks["documents"][i])

            if not all_chunks:
                # Fallback: if we can't match by ID, try semantic search on user's documents
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    where={"user_id": user_id}
                )
                
                if results["documents"] and results["documents"][0]:
                    all_chunks = results["documents"][0]

            if not all_chunks:
                return ""

            # Limit to k results
            return "\n\n".join(all_chunks[:k])

        except Exception as e:
            print(f"Error getting selected documents context: {e}")
            return ""

    def delete_user_documents(self, user_id: str) -> bool:
        """
        Delete all documents for a specific user.

        Args:
            user_id: User identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(where={"user_id": user_id})
            print(f"Deleted all documents for user {user_id}")
            return True
        except Exception as e:
            print(f"Error deleting documents for user {user_id}: {e}")
            return False

    def list_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all documents for a specific user, aggregated by file.

        Args:
            user_id: User identifier

        Returns:
            List of document metadata aggregated by file
        """
        try:
            results = self.collection.get(where={"user_id": user_id})
            metadatas = results["metadatas"] if results["metadatas"] else []
            
            if not metadatas:
                return []
            
            # Group chunks by file_name to aggregate documents
            documents_map = {}
            for metadata in metadatas:
                file_name = metadata.get("file_name", "Unknown")
                
                if file_name not in documents_map:
                    # Create unique document_id based on user_id and file_name
                    safe_filename = file_name.replace(' ', '_').replace('.', '_')
                    document_id = f"{user_id}_{safe_filename}"
                    
                    documents_map[file_name] = {
                        "document_id": document_id,
                        "file_name": file_name,
                        "doc_type": metadata.get("doc_type", "unknown"),
                        "upload_date": metadata.get("upload_date"),
                        "is_inbody_report": metadata.get("is_inbody_report", False),
                        "document_category": metadata.get("document_category", "general"),
                        "chunk_count": 0
                    }
                
                # Increment chunk count
                documents_map[file_name]["chunk_count"] += 1
            
            return list(documents_map.values())
            
        except Exception as e:
            print(f"Error listing documents for user {user_id}: {e}")
            return []


# Global instance for easy access
vector_store = VectorStore()


def process_file_for_user(file_path: str, user_id: str, metadata: Dict[str, Any] = None) -> bool:
    """
    Convenience function to process a file for a user.

    Args:
        file_path: Path to the file
        user_id: User identifier
        metadata: Additional metadata

    Returns:
        True if successful, False otherwise
    """
    return vector_store.add_document(file_path, user_id, metadata)


def process_base64_image_for_user(base64_string: str, user_id: str,
                                image_format: str = "jpeg",
                                metadata: Dict[str, Any] = None) -> bool:
    """
    Convenience function to process a base64 image for a user.

    Args:
        base64_string: Base64 encoded image
        user_id: User identifier
        image_format: Image format
        metadata: Additional metadata

    Returns:
        True if successful, False otherwise
    """
    return vector_store.add_base64_image(base64_string, user_id, image_format, metadata)
