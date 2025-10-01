"""Utility functions for data normalization and processing."""

from datetime import datetime, timezone
from dateutil import parser
from typing import Any, Optional, Tuple
import re


# ============================================================================
# Time utilities
# ============================================================================

def parse_to_utc_seconds(dt_input: Any) -> Optional[int]:
    """
    Parse various datetime formats to UTC epoch seconds.
    
    Handles:
    - ISO strings (with or without TZ)
    - MongoDB date objects ({"$date": "..."})
    - datetime objects
    - None values
    
    Args:
        dt_input: DateTime input in various formats
        
    Returns:
        UTC epoch seconds as integer, or None if invalid
    """
    if dt_input is None:
        return None
    
    try:
        # Handle MongoDB date objects
        if isinstance(dt_input, dict) and "$date" in dt_input:
            dt_input = dt_input["$date"]
        
        # Handle string inputs
        if isinstance(dt_input, str):
            dt = parser.isoparse(dt_input)
        # Handle datetime objects
        elif isinstance(dt_input, datetime):
            dt = dt_input
        else:
            return None
        
        # Convert to UTC if timezone-aware
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc)
        else:
            # Assume UTC if no timezone
            dt = dt.replace(tzinfo=timezone.utc)
        
        return int(dt.timestamp())
    
    except (ValueError, TypeError, AttributeError):
        return None


def date_to_day_range(date_str: str) -> Tuple[int, int]:
    """
    Convert YYYY-MM-DD date to start/end timestamps for that day (UTC).
    
    Args:
        date_str: Date in YYYY-MM-DD format
        
    Returns:
        Tuple of (start_ts, end_ts) for 00:00:00 to 23:59:59
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        start_dt = dt.replace(hour=0, minute=0, second=0, tzinfo=timezone.utc)
        end_dt = dt.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        return int(start_dt.timestamp()), int(end_dt.timestamp())
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}, expected YYYY-MM-DD")


def extract_date_from_timestamp(ts: Optional[int]) -> Optional[str]:
    """
    Extract YYYY-MM-DD date from UTC epoch seconds.
    
    Args:
        ts: UTC epoch seconds
        
    Returns:
        Date string in YYYY-MM-DD format, or None
    """
    if ts is None:
        return None
    
    try:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, OSError):
        return None


# ============================================================================
# Name normalization
# ============================================================================

def normalize_name(name: Optional[str]) -> Optional[str]:
    """
    Normalize name by stripping whitespace and handling None.
    
    Args:
        name: Input name string
        
    Returns:
        Normalized name or None
    """
    if name is None:
        return None
    
    normalized = name.strip()
    return normalized if normalized else None


def build_full_name(first_name: Optional[str], last_name: Optional[str]) -> Optional[str]:
    """
    Build full name from first and last names.
    
    Args:
        first_name: First name
        last_name: Last name
        
    Returns:
        Full name or None if both are empty
    """
    first = normalize_name(first_name)
    last = normalize_name(last_name)
    
    if first and last:
        return f"{first} {last}"
    elif first:
        return first
    elif last:
        return last
    else:
        return None


# ============================================================================
# Health metrics
# ============================================================================

def calculate_bmi(height_cm: Optional[float], weight_kg: Optional[float]) -> Optional[float]:
    """
    Calculate BMI from height and weight with outlier guards.
    
    BMI = weight (kg) / (height (m))^2
    
    Outlier guards:
    - Height: 50-250 cm
    - Weight: 2-500 kg
    
    Args:
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        
    Returns:
        BMI rounded to 1 decimal, or None if invalid
    """
    if height_cm is None or weight_kg is None:
        return None
    
    # Guard outliers
    if not (50 <= height_cm <= 250):
        return None
    if not (2 <= weight_kg <= 500):
        return None
    
    try:
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 1)
    except (ZeroDivisionError, ValueError):
        return None


# ============================================================================
# Stable ID generation
# ============================================================================

def generate_profile_id(patient_id: str) -> str:
    """Generate stable ID for profile chunk."""
    return f"profile:{patient_id}"


def generate_meal_summary_id(patient_id: str, date: str) -> str:
    """Generate stable ID for meal day summary."""
    return f"meals:{patient_id}:{date}:summary"


def generate_meal_id(patient_id: str, date: str, meal_id: str) -> str:
    """Generate stable ID for individual meal."""
    return f"meals:{patient_id}:{date}:meal:{meal_id}"


def generate_meal_recommendation_id(patient_id: str, date: str) -> str:
    """Generate stable ID for meal recommendations."""
    return f"meals:{patient_id}:{date}:recommendation"


def generate_fitness_summary_id(patient_id: str, report_type: str, start_ts: int) -> str:
    """Generate stable ID for fitness summary."""
    return f"fitness:{patient_id}:{report_type}:{start_ts}:summary"


def generate_fitness_hour_id(patient_id: str, report_type: str, start_ts: int, hour: int) -> str:
    """Generate stable ID for fitness hourly chunk."""
    return f"fitness:{patient_id}:{report_type}:{start_ts}:hour:{hour:02d}"


def generate_sleep_summary_id(patient_id: str, report_type: str, start_ts: int) -> str:
    """Generate stable ID for sleep summary."""
    return f"sleep:{patient_id}:{report_type}:{start_ts}:summary"


# ============================================================================
# Text formatting
# ============================================================================

def format_profile_completion(completion: Optional[Any]) -> str:
    """
    Format profile completion JSON to readable text.
    
    Args:
        completion: Profile completion dict or JSON
        
    Returns:
        Formatted string like "basic ✓, lifestyle ✗, medical_history ✓"
    """
    if completion is None:
        return "unknown"
    
    # Handle string JSON
    if isinstance(completion, str):
        import json
        try:
            completion = json.loads(completion)
        except json.JSONDecodeError:
            return "unknown"
    
    if not isinstance(completion, dict):
        return "unknown"
    
    parts = []
    for key, value in completion.items():
        if isinstance(value, dict) and "is_complete" in value:
            check = "✓" if value["is_complete"] else "✗"
            parts.append(f"{key} {check}")
    
    return ", ".join(parts) if parts else "unknown"


def safe_str(value: Any, default: str = "N/A") -> str:
    """Safely convert value to string with default."""
    if value is None:
        return default
    return str(value)


# ============================================================================
# Validation
# ============================================================================

def is_valid_uuid(value: str) -> bool:
    """Check if string is a valid UUID."""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(value))


def validate_required_fields(data: dict, required: list, source: str) -> Optional[str]:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Data dictionary to validate
        required: List of required field names
        source: Source name for error messages
        
    Returns:
        Error message if validation fails, None otherwise
    """
    missing = [field for field in required if field not in data or data[field] is None]
    
    if missing:
        return f"Missing required fields for {source}: {', '.join(missing)}"
    
    return None

