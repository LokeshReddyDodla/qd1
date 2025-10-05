"""Data models for CGM (Continuous Glucose Monitoring) reports."""

from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator


class CGMRangeStats(BaseModel):
    """CGM time in range statistics."""
    below_54: float = Field(..., description="% time below 54 mg/dL")
    below_70_above_54: float = Field(..., description="% time 54-69 mg/dL")
    in_target_70_180: float = Field(..., description="% time 70-180 mg/dL (target)")
    above_180_below_250: float = Field(..., description="% time 180-249 mg/dL")
    above_250: float = Field(..., description="% time ≥250 mg/dL")


class CGMSummaryStats(BaseModel):
    """CGM summary statistics."""
    average_glucose: float = Field(..., description="Mean glucose (mg/dL)")
    gmi: Optional[float] = Field(None, description="Glucose Management Indicator")
    gmi_mmol: Optional[float] = Field(None, description="GMI in mmol/L")
    glucose_variability: Optional[float] = Field(None, description="Variability %")
    coefficient_of_variation: float = Field(..., description="CV %")
    standard_deviation: float = Field(..., description="SD (mg/dL)")
    highest_glucose: float = Field(..., description="Max glucose (mg/dL)")
    highest_glucose_date: str = Field(..., description="Timestamp of max")
    lowest_glucose: float = Field(..., description="Min glucose (mg/dL)")
    lowest_glucose_date: str = Field(..., description="Timestamp of min")


class TimePeriodStats(BaseModel):
    """Stats for a specific time period (breakfast, lunch, etc)."""
    average_glucose: float = Field(..., description="Mean glucose for period")
    highest_glucose: Optional[float] = Field(None, description="Max glucose")
    lowest_glucose: Optional[float] = Field(None, description="Min glucose")
    out_of_range_percentage: Optional[float] = Field(None, description="% out of target")
    from_time: str = Field(..., description="Period start time (HH:MM:SS)")
    to_time: str = Field(..., description="Period end time (HH:MM:SS)")


class HyperStats(BaseModel):
    """Hyperglycemia event statistics."""
    total_hyper_duration: float = Field(..., description="Total minutes in hyper")
    average_hyper_duration: float = Field(..., description="Average minutes per event")
    hyper_events_count: int = Field(..., description="Number of hyper events")


class HypoStats(BaseModel):
    """Hypoglycemia event statistics."""
    total_hypo_duration: float = Field(..., description="Total minutes in hypo")
    average_hypo_duration: float = Field(..., description="Average minutes per event")
    hypo_events_count: int = Field(..., description="Number of hypo events")


class RecordCounts(BaseModel):
    """Record count metadata."""
    cgm_readings_count: int = Field(0, description="Number of CGM readings")


class CGMInput(BaseModel):
    """CGM report input from MongoDB."""
    
    # Required fields
    patient_id: str = Field(..., description="Patient UUID")
    report_type: Literal["daily", "weekly", "monthly", "custom"] = Field(..., description="Report type")
    start_date: str = Field(..., description="ISO-8601 start date")
    end_date: str = Field(..., description="ISO-8601 end date")
    
    # Core stats (required)
    cgm_range_stats: CGMRangeStats = Field(..., description="Time in range stats")
    cgm_summary_stats: CGMSummaryStats = Field(..., description="Summary statistics")
    
    # Optional stats
    time_period_stats: Optional[Dict[str, TimePeriodStats]] = Field(None, description="Breakfast/lunch/dinner/overnight stats")
    hyper_stats: Optional[HyperStats] = Field(None, description="Hyperglycemia stats")
    hypo_stats: Optional[HypoStats] = Field(None, description="Hypoglycemia stats")
    
    # Metadata
    record_counts: Optional[RecordCounts] = Field(None, description="Record counts")
    created_at: Optional[str] = Field(None, description="ISO-8601 creation timestamp")
    updated_at: Optional[str] = Field(None, description="ISO-8601 update timestamp")
    
    # Optional MongoDB reference
    mongo_id: Optional[str] = Field(None, description="MongoDB document _id for deep linking")
    
    @field_validator("start_date", "end_date")
    @classmethod
    def validate_iso_date(cls, v: str) -> str:
        """Ensure dates are valid ISO-8601 format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Date must be in ISO-8601 format, got: {v}")
        return v


class CGMPayload(BaseModel):
    """Payload stored in Qdrant for CGM reports."""
    
    patient_id: str
    full_name: Optional[str] = None
    report_type: str
    start_date: str
    end_date: str
    
    cgm_range_stats: Dict[str, float]
    cgm_summary_stats: Dict[str, Any]
    time_period_stats: Optional[Dict[str, Dict[str, Any]]] = None
    hyper_stats: Optional[Dict[str, Any]] = None
    hypo_stats: Optional[Dict[str, Any]] = None
    record_counts: Dict[str, int]
    
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    mongo_id: Optional[str] = None
    
    source: str = "cgm"
    version: int = 1
    
    # For display/grounding
    text: str = Field(..., description="Summary text for embedding and display")
