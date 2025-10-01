"""Test script for RAG query functionality."""

import httpx
import json

BASE_URL = "http://localhost:8000"


def test_query(person: str, question: str, **kwargs):
    """
    Test a RAG query.
    
    Args:
        person: Person name or patient_id
        question: Natural language question
        **kwargs: Additional query parameters (source, from, to, top_k)
    """
    print(f"\n{'='*60}")
    print(f"QUERY: {question}")
    print(f"PERSON: {person}")
    print(f"{'='*60}")
    
    payload = {
        "person": person,
        "question": question,
        **kwargs
    }
    
    print(f"\nRequest payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = httpx.post(
            f"{BASE_URL}/query",
            json=payload,
            timeout=30.0
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n--- ANSWER ---")
            print(result["answer"])
            
            print(f"\n--- EVIDENCE ({len(result['evidence'])} chunks) ---")
            for idx, evidence in enumerate(result["evidence"], 1):
                print(f"\n[{idx}] Score: {evidence['score']:.4f}")
                print(f"    Source: {evidence['payload']['source']}")
                print(f"    Date: {evidence['payload'].get('date', 'N/A')}")
                print(f"    Section: {evidence['payload']['section']}")
                print(f"    Text: {evidence['text'][:200]}...")
            
            print(f"\n--- METADATA ---")
            print(json.dumps(result["query_metadata"], indent=2))
        else:
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"Request failed: {str(e)}")


def main():
    """Run test queries."""
    print("=" * 60)
    print("RAG QUERY TESTS")
    print("=" * 60)
    
    # Test 1: Query meals for Raju on specific date
    test_query(
        person="Raju Kumar",
        question="What did Raju eat on 2025-05-02?",
        source="meals",
        **{"from": "2025-05-02T00:00:00Z", "to": "2025-05-02T23:59:59Z"},
        top_k=10
    )
    
    # Test 2: Query fitness for Raju
    test_query(
        person="Raju Kumar",
        question="How many steps did Raju take on May 2nd, 2025?",
        source="fitness",
        **{"from": "2025-05-02T00:00:00Z", "to": "2025-05-02T23:59:59Z"},
        top_k=5
    )
    
    # Test 3: Query sleep for Raju
    test_query(
        person="Raju Kumar",
        question="How was Raju's sleep quality on 2025-05-02?",
        source="sleep",
        **{"from": "2025-05-02T00:00:00Z", "to": "2025-05-02T23:59:59Z"},
        top_k=5
    )
    
    # Test 4: General profile query for Vibha
    test_query(
        person="Vibha Pai",
        question="Tell me about Vibha Pai's profile and health metrics",
        source="profile",
        top_k=3
    )
    
    # Test 5: Combined query without source filter
    test_query(
        person="Raju Kumar",
        question="Summarize Raju's health data for May 2nd, 2025",
        **{"from": "2025-05-02T00:00:00Z", "to": "2025-05-02T23:59:59Z"},
        top_k=15
    )
    
    print("\n" + "=" * 60)
    print("QUERY TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()

