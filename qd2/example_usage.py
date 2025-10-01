"""
Example usage of the RAG system programmatically.

This demonstrates how to use the system without going through HTTP endpoints.
Useful for embedding the RAG system into other Python applications.
"""

from config import settings
from embedding_service import EmbeddingService
from qdrant_client_wrapper import QdrantManager
from llm_service import LLMService
from ingestion import IngestionPipeline
from retrieval import RetrievalService
from models import (
    ProfileInput, MealInput, FitnessInput, SleepInput, QueryRequest
)


def initialize_services():
    """Initialize all services."""
    print("Initializing services...")
    
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
    
    print("✓ Services initialized\n")
    
    return {
        "embedding": embedding_service,
        "qdrant": qdrant_manager,
        "llm": llm_service,
        "ingestion": ingestion_pipeline,
        "retrieval": retrieval_service
    }


def example_ingest_profile(services):
    """Example: Ingest a patient profile."""
    print("=== Ingesting Profile ===")
    
    profile = ProfileInput(
        patient_id="12345678-1234-1234-1234-123456789abc",
        first_name="John",
        last_name="Doe",
        dob="1980-01-15",
        gender="male",
        height=178.0,
        waist=90,
        weight=82,
        email="john.doe@example.com",
        phone_number="1234567890",
        locale="Asia/Kolkata",
        created_at="2025-09-30T10:00:00Z",
        profile_completion={
            "basic": {"is_complete": True, "is_mandatory": True},
            "lifestyle": {"is_complete": True, "is_mandatory": True},
            "medical_history": {"is_complete": False, "is_mandatory": True}
        }
    )
    
    result = services["ingestion"].ingest_profiles([profile])
    
    print(f"✓ Accepted: {result['accepted']}")
    print(f"✓ Indexed points: {result['indexed_points']}")
    print(f"✓ Errors: {len(result['errors'])}\n")
    
    return result


def example_ingest_meal(services):
    """Example: Ingest a meal report."""
    print("=== Ingesting Meal ===")
    
    meal = MealInput(
        patient_id="12345678-1234-1234-1234-123456789abc",
        report_type="daily",
        date="2025-09-30",
        meal_count=2,
        calories=1200,
        proteins=60,
        carbohydrates=140,
        fats=40,
        fiber=20,
        meals=[
            {
                "id": "breakfast-001",
                "name": "Breakfast",
                "time": "08:00:00",
                "items": [
                    {"name": "Scrambled Eggs", "quantity": "2 eggs"},
                    {"name": "Whole Wheat Toast", "quantity": "2 slices"}
                ],
                "total_macro_nutritional_value": {
                    "calories": 450,
                    "proteins": 25,
                    "carbohydrates": 40,
                    "fats": 18,
                    "fiber": 6
                },
                "feedback": "High protein breakfast to start the day."
            },
            {
                "id": "lunch-001",
                "name": "Lunch",
                "time": "13:00:00",
                "items": [
                    {"name": "Grilled Salmon", "quantity": "150g"},
                    {"name": "Quinoa", "quantity": "1 cup"},
                    {"name": "Steamed Broccoli", "quantity": "1 cup"}
                ],
                "total_macro_nutritional_value": {
                    "calories": 750,
                    "proteins": 35,
                    "carbohydrates": 100,
                    "fats": 22,
                    "fiber": 14
                },
                "feedback": "Balanced lunch with omega-3 and complex carbs."
            }
        ],
        diet_recommendations={
            "total_calories": 2000,
            "proteins": 100,
            "carbohydrates": 230,
            "fats": 65
        }
    )
    
    result = services["ingestion"].ingest_meals([meal])
    
    print(f"✓ Accepted: {result['accepted']}")
    print(f"✓ Indexed points: {result['indexed_points']}")
    print(f"✓ Errors: {len(result['errors'])}\n")
    
    return result


def example_query(services):
    """Example: Query the RAG system."""
    print("=== Querying RAG System ===")
    
    request = QueryRequest(
        person="John Doe",
        question="What did John eat for breakfast today?",
        source="meals",
        **{"from": "2025-09-30T00:00:00Z", "to": "2025-09-30T23:59:59Z"},
        top_k=5
    )
    
    response = services["retrieval"].query(request)
    
    print(f"Question: {request.question}")
    print(f"\nAnswer:\n{response.answer}")
    print(f"\nEvidence chunks: {len(response.evidence)}")
    
    for idx, evidence in enumerate(response.evidence, 1):
        print(f"\n[{idx}] Score: {evidence.score:.4f}")
        print(f"    Source: {evidence.payload['source']}")
        print(f"    Date: {evidence.payload.get('date', 'N/A')}")
        print(f"    Text: {evidence.text[:150]}...")
    
    print(f"\nMetadata: {response.query_metadata}\n")
    
    return response


def example_collection_stats(services):
    """Example: Get collection statistics."""
    print("=== Collection Statistics ===")
    
    info = services["qdrant"].get_collection_info()
    
    print(f"Collection: {info.get('name')}")
    print(f"Points: {info.get('points_count', 0)}")
    print(f"Status: {info.get('status')}\n")
    
    return info


def main():
    """Run all examples."""
    print("=" * 70)
    print("RAG SYSTEM - PROGRAMMATIC USAGE EXAMPLES")
    print("=" * 70)
    print()
    
    # Initialize
    services = initialize_services()
    
    # Example 1: Ingest profile
    example_ingest_profile(services)
    
    # Example 2: Ingest meal
    example_ingest_meal(services)
    
    # Example 3: Check collection stats
    example_collection_stats(services)
    
    # Example 4: Query
    example_query(services)
    
    print("=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()

