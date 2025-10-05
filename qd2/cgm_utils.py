"""Utility functions for CGM data processing."""

import hashlib
from typing import Dict, Any
from models_cgm import CGMInput, CGMPayload


def make_cgm_point_id(patient_id: str, report_type: str, start_date: str, end_date: str) -> str:
    """
    Generate deterministic Qdrant point ID for CGM report.
    
    Format:
    - daily/weekly/monthly: sk_cgm_{patient_id}_{report_type}_{YYYYMMDD}
    - custom: sk_cgm_{patient_id}_{report_type}_{sha1_12char}
    
    Args:
        patient_id: Patient UUID
        report_type: daily, weekly, monthly, or custom
        start_date: ISO-8601 start date
        end_date: ISO-8601 end date
        
    Returns:
        Stable point ID string
    """
    if report_type in ["daily", "weekly", "monthly"]:
        # Extract YYYYMMDD from start_date
        date_part = start_date[:10].replace("-", "")
        return f"sk_cgm_{patient_id}_{report_type}_{date_part}"
    else:
        # Custom range - use SHA1 hash of date range
        range_str = f"{start_date}:{end_date}"
        hash_hex = hashlib.sha1(range_str.encode()).hexdigest()[:12]
        return f"sk_cgm_{patient_id}_{report_type}_{hash_hex}"


def render_cgm_summary(cgm: CGMInput) -> str:
    """
    Create a compact, deterministic summary string for embedding.
    
    Args:
        cgm: CGM report input
        
    Returns:
        Summary text string
    """
    lines = []
    
    # Header
    lines.append(
        f"CGM report | patient={cgm.patient_id} | type={cgm.report_type} | "
        f"window={cgm.start_date}→{cgm.end_date}"
    )
    
    # Range percentages
    r = cgm.cgm_range_stats
    lines.append(
        f"Range%: <54={r.below_54:.2f}, 54–69={r.below_70_above_54:.2f}, "
        f"70–180={r.in_target_70_180:.2f}, 180–249={r.above_180_below_250:.2f}, "
        f"≥250={r.above_250:.2f}"
    )
    
    # Summary stats
    s = cgm.cgm_summary_stats
    gmi_str = f"{s.gmi:.2f}" if s.gmi is not None else "N/A"
    var_str = f"{s.glucose_variability:.2f}" if s.glucose_variability is not None else "N/A"
    lines.append(
        f"Summary: avg={s.average_glucose:.2f}, sd={s.standard_deviation:.2f}, "
        f"cv={s.coefficient_of_variation:.2f}, gmi={gmi_str}, var={var_str}"
    )
    
    # Extrema
    lines.append(
        f"Extrema: min={s.lowest_glucose} @ {s.lowest_glucose_date}, "
        f"max={s.highest_glucose} @ {s.highest_glucose_date}"
    )
    
    # Time periods (if available)
    if cgm.time_period_stats:
        period_parts = []
        for period_name in ["breakfast", "lunch", "dinner", "overnight"]:
            period = cgm.time_period_stats.get(period_name)
            if period:
                oor = f"{period.out_of_range_percentage:.1f}%" if period.out_of_range_percentage is not None else "N/A"
                period_parts.append(f"{period_name}={period.average_glucose:.1f}|oor={oor}")
        if period_parts:
            lines.append(f"Periods: {', '.join(period_parts)}")
    
    # Hyper events
    if cgm.hyper_stats:
        h = cgm.hyper_stats
        lines.append(
            f"Hyper: count={h.hyper_events_count}, total_min={h.total_hyper_duration:.1f}, "
            f"avg_min={h.average_hyper_duration:.1f}"
        )
    
    # Hypo events
    if cgm.hypo_stats:
        h = cgm.hypo_stats
        lines.append(
            f"Hypo: count={h.hypo_events_count}, total_min={h.total_hypo_duration:.1f}, "
            f"avg_min={h.average_hypo_duration:.1f}"
        )
    
    # Record counts
    if cgm.record_counts:
        lines.append(f"Readings: {cgm.record_counts.cgm_readings_count} records")
    
    return "\n".join(lines)


def cgm_to_payload(cgm: CGMInput, summary_text: str) -> CGMPayload:
    """
    Convert CGM input to Qdrant payload.
    
    Args:
        cgm: CGM report input
        summary_text: Pre-rendered summary string
        
    Returns:
        CGM payload for Qdrant
    """
    return CGMPayload(
        patient_id=cgm.patient_id,
        full_name=None,  # Will be populated from profile if available
        report_type=cgm.report_type,
        start_date=cgm.start_date,
        end_date=cgm.end_date,
        cgm_range_stats=cgm.cgm_range_stats.model_dump(),
        cgm_summary_stats=cgm.cgm_summary_stats.model_dump(),
        time_period_stats={
            k: v.model_dump() for k, v in cgm.time_period_stats.items()
        } if cgm.time_period_stats else None,
        hyper_stats=cgm.hyper_stats.model_dump() if cgm.hyper_stats else None,
        hypo_stats=cgm.hypo_stats.model_dump() if cgm.hypo_stats else None,
        record_counts=cgm.record_counts.model_dump() if cgm.record_counts else {"cgm_readings_count": 0},
        created_at=cgm.created_at,
        updated_at=cgm.updated_at,
        mongo_id=cgm.mongo_id,
        source="cgm",
        version=1,
        text=summary_text
    )
