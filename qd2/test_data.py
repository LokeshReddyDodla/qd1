"""Sample test data for validating the RAG system."""

# Sample patient profiles
SAMPLE_PROFILES = [
    {
        "patient_id": "00df6b5c-193b-47ce-a9b5-46d4975d9820",
        "first_name": "Vibha",
        "last_name": "Pai",
        "dob": "1992-05-28",
        "gender": "female",
        "height": 170.2,
        "waist": 106,
        "weight": 80,
        "email": "vibhapai92@gmail.com",
        "phone_number": "918296066561",
        "locale": "Asia/Kolkata",
        "created_at": "2025-06-27T08:39:07.107865Z",
        "profile_completion": {
            "basic": {"is_complete": True, "is_mandatory": True},
            "lifestyle": {"is_complete": False, "is_mandatory": True},
            "medical_history": {"is_complete": True, "is_mandatory": True}
        }
    },
    {
        "patient_id": "7538e5a0-da8b-4745-95d5-ac1ceefd2c76",
        "first_name": "Raju",
        "last_name": "Kumar",
        "dob": "1985-03-15",
        "gender": "male",
        "height": 175.0,
        "waist": 95,
        "weight": 85,
        "email": "raju.kumar@example.com",
        "phone_number": "919876543210",
        "locale": "Asia/Kolkata",
        "created_at": "2025-05-01T10:00:00Z",
        "profile_completion": {
            "basic": {"is_complete": True, "is_mandatory": True},
            "lifestyle": {"is_complete": True, "is_mandatory": True},
            "medical_history": {"is_complete": True, "is_mandatory": True}
        }
    }
]

# Sample meal data
SAMPLE_MEALS = [
    {
        "patient_id": "7538e5a0-da8b-4745-95d5-ac1ceefd2c76",
        "report_type": "daily",
        "date": "2025-05-02",
        "meal_count": 3,
        "calories": 1850,
        "proteins": 95,
        "carbohydrates": 210,
        "fats": 65,
        "fiber": 28,
        "meals": [
            {
                "id": "meal-001",
                "name": "Breakfast",
                "time": "08:30:00",
                "items": [
                    {"name": "Oatmeal", "quantity": "1 bowl"},
                    {"name": "Banana", "quantity": "1 medium"}
                ],
                "total_macro_nutritional_value": {
                    "calories": 350,
                    "proteins": 12,
                    "carbohydrates": 65,
                    "fats": 8,
                    "fiber": 10
                },
                "feedback": "Great start to the day with complex carbs and fiber."
            },
            {
                "id": "meal-002",
                "name": "Lunch",
                "time": "13:00:00",
                "items": [
                    {"name": "Grilled Chicken", "quantity": "200g"},
                    {"name": "Brown Rice", "quantity": "1 cup"},
                    {"name": "Mixed Vegetables", "quantity": "1 bowl"}
                ],
                "total_macro_nutritional_value": {
                    "calories": 650,
                    "proteins": 45,
                    "carbohydrates": 70,
                    "fats": 15,
                    "fiber": 12
                },
                "feedback": "Balanced meal with good protein and fiber content."
            },
            {
                "id": "4b41d7ad-fd9b-409d-8aad-b89404b8d0a2",
                "name": "Evening Snack",
                "time": "16:59:17",
                "items": [
                    {"name": "Steamed Broccoli", "quantity": "1 bowl"},
                    {"name": "Grilled Fish", "quantity": "1 plate"}
                ],
                "total_macro_nutritional_value": {
                    "calories": 255,
                    "proteins": 29,
                    "carbohydrates": 11,
                    "fats": 12.5,
                    "fiber": 5
                },
                "total_micro_nutritional_value": {
                    "calcium_mg": 82,
                    "iron_mg": 2,
                    "zinc_mg": 1.2,
                    "magnesium_mg": 49
                },
                "feedback": "This is a nutritious snack with excellent protein quality."
            }
        ],
        "diet_recommendations": {
            "total_calories": 2000,
            "proteins": 100,
            "carbohydrates": 220,
            "fats": 70
        }
    }
]

# Sample fitness data
SAMPLE_FITNESS = [
    {
        "patient_id": "495bfd5a-1662-42be-9713-ac1395bb23af",
        "report_type": "daily",
        "start_date": {"$date": "2025-08-06T00:00:00Z"},
        "end_date": {"$date": "2025-08-06T23:59:59Z"},
        "steps": 3367,
        "active_duration": 171,
        "peak_activity_time": {
            "hour": "2025-08-06 20:00:00",
            "max_steps": 507
        },
        "activity_distribution": {
            "morning": {"steps": 894, "active_duration": 42},
            "afternoon": {"steps": 1501, "active_duration": 72},
            "evening": {"steps": 972, "active_duration": 57}
        },
        "inactive_periods": [
            {"start": "2025-08-06 14:00:00", "end": "2025-08-06 15:43:00", "duration": 103}
        ]
    },
    {
        "patient_id": "7538e5a0-da8b-4745-95d5-ac1ceefd2c76",
        "report_type": "daily",
        "start_date": "2025-05-02T00:00:00Z",
        "end_date": "2025-05-02T23:59:59Z",
        "steps": 8500,
        "active_duration": 95,
        "peak_activity_time": {
            "hour": "2025-05-02 18:00:00",
            "max_steps": 1200
        },
        "activity_distribution": {
            "morning": {"steps": 2500, "active_duration": 30},
            "afternoon": {"steps": 3000, "active_duration": 35},
            "evening": {"steps": 3000, "active_duration": 30}
        }
    }
]

# Sample sleep data
SAMPLE_SLEEP = [
    {
        "patient_id": "57dc647f-7988-418f-a404-05d2c6feab6d",
        "report_type": "daily",
        "start_date": {"$date": "2025-08-03T00:00:00Z"},
        "end_date": {"$date": "2025-08-03T23:59:59Z"},
        "quality_analysis": {
            "sleep_quality": "very poor",
            "deep_sleep_percentage": 0,
            "rem_sleep_percentage": 0,
            "awake_time_percentage": 0
        }
    },
    {
        "patient_id": "7538e5a0-da8b-4745-95d5-ac1ceefd2c76",
        "report_type": "daily",
        "start_date": "2025-05-02T00:00:00Z",
        "end_date": "2025-05-02T23:59:59Z",
        "quality_analysis": {
            "sleep_quality": "good",
            "deep_sleep_percentage": 22,
            "rem_sleep_percentage": 25,
            "awake_time_percentage": 5
        }
    }
]

