"""Test script for ingestion pipeline."""

import httpx
import json
from test_data import SAMPLE_PROFILES, SAMPLE_MEALS, SAMPLE_FITNESS, SAMPLE_SLEEP

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    response = httpx.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_ingest_profiles():
    """Test profile ingestion."""
    print("\n=== Testing Profile Ingestion ===")
    response = httpx.post(
        f"{BASE_URL}/ingest/profile",
        json=SAMPLE_PROFILES
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200


def test_ingest_meals():
    """Test meals ingestion."""
    print("\n=== Testing Meals Ingestion ===")
    response = httpx.post(
        f"{BASE_URL}/ingest/meals",
        json=SAMPLE_MEALS
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200


def test_ingest_fitness():
    """Test fitness ingestion."""
    print("\n=== Testing Fitness Ingestion ===")
    response = httpx.post(
        f"{BASE_URL}/ingest/fitness",
        json=SAMPLE_FITNESS,
        params={"include_hourly": False}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200


def test_ingest_sleep():
    """Test sleep ingestion."""
    print("\n=== Testing Sleep Ingestion ===")
    response = httpx.post(
        f"{BASE_URL}/ingest/sleep",
        json=SAMPLE_SLEEP
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200


def test_collection_info():
    """Test collection info endpoint."""
    print("\n=== Testing Collection Info ===")
    response = httpx.get(f"{BASE_URL}/collection/info")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return response.status_code == 200


def main():
    """Run all ingestion tests."""
    print("=" * 60)
    print("INGESTION TESTS")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Profile Ingestion", test_ingest_profiles),
        ("Meals Ingestion", test_ingest_meals),
        ("Fitness Ingestion", test_ingest_fitness),
        ("Sleep Ingestion", test_ingest_sleep),
        ("Collection Info", test_collection_info),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            success = test_func()
            results[name] = "PASS" if success else "FAIL"
        except Exception as e:
            print(f"Error in {name}: {str(e)}")
            results[name] = "ERROR"
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, result in results.items():
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {name}: {result}")
    
    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)
    print(f"\nPassed: {passed}/{total}")


if __name__ == "__main__":
    main()

