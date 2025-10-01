"""Script to populate sample data into Postgres and MongoDB."""

import psycopg2
from pymongo import MongoClient
from config import settings
from test_data import SAMPLE_PROFILES, SAMPLE_MEALS, SAMPLE_FITNESS, SAMPLE_SLEEP
import json


def setup_postgres():
    """Insert sample profiles into Postgres."""
    print("\n=== Setting up PostgreSQL ===")
    
    try:
        conn = psycopg2.connect(settings.postgres_dsn)
        cur = conn.cursor()
        
        # Insert profiles
        for profile in SAMPLE_PROFILES:
            cur.execute("""
                INSERT INTO patients (
                    patient_id, first_name, last_name, dob, gender,
                    height, waist, weight, email, phone_number,
                    locale, created_at, profile_completion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (patient_id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    dob = EXCLUDED.dob,
                    gender = EXCLUDED.gender,
                    height = EXCLUDED.height,
                    waist = EXCLUDED.waist,
                    weight = EXCLUDED.weight,
                    email = EXCLUDED.email,
                    phone_number = EXCLUDED.phone_number,
                    locale = EXCLUDED.locale,
                    profile_completion = EXCLUDED.profile_completion
            """, (
                profile["patient_id"],
                profile["first_name"],
                profile["last_name"],
                profile["dob"],
                profile["gender"],
                profile["height"],
                profile["waist"],
                profile["weight"],
                profile["email"],
                profile["phone_number"],
                profile["locale"],
                profile["created_at"],
                json.dumps(profile["profile_completion"])
            ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✓ Inserted {len(SAMPLE_PROFILES)} profiles into PostgreSQL")
    
    except Exception as e:
        print(f"✗ PostgreSQL setup failed: {str(e)}")


def setup_mongodb():
    """Insert sample health data into MongoDB."""
    print("\n=== Setting up MongoDB ===")
    
    try:
        client = MongoClient(settings.mongo_uri)
        db = client[settings.mongo_db]
        
        # Insert meals
        meals_collection = db["meals"]
        for meal in SAMPLE_MEALS:
            meals_collection.replace_one(
                {"patient_id": meal["patient_id"], "date": meal["date"]},
                meal,
                upsert=True
            )
        print(f"✓ Inserted {len(SAMPLE_MEALS)} meal reports into MongoDB")
        
        # Insert fitness
        fitness_collection = db["fitness"]
        for fitness in SAMPLE_FITNESS:
            fitness_collection.replace_one(
                {
                    "patient_id": fitness["patient_id"],
                    "start_date": fitness["start_date"]
                },
                fitness,
                upsert=True
            )
        print(f"✓ Inserted {len(SAMPLE_FITNESS)} fitness reports into MongoDB")
        
        # Insert sleep
        sleep_collection = db["sleep"]
        for sleep in SAMPLE_SLEEP:
            sleep_collection.replace_one(
                {
                    "patient_id": sleep["patient_id"],
                    "start_date": sleep["start_date"]
                },
                sleep,
                upsert=True
            )
        print(f"✓ Inserted {len(SAMPLE_SLEEP)} sleep reports into MongoDB")
        
        client.close()
    
    except Exception as e:
        print(f"✗ MongoDB setup failed: {str(e)}")


def main():
    """Setup sample data in both databases."""
    print("=" * 60)
    print("DATABASE SETUP")
    print("=" * 60)
    
    setup_postgres()
    setup_mongodb()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print("\nYou can now run the API and ingest this data:")
    print("  python main.py")
    print("  python test_ingestion.py")


if __name__ == "__main__":
    main()

