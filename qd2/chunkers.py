"""Chunking strategies for each data source."""

from typing import List, Optional
from models import (
    ProcessedChunk, ChunkPayload, Source, Section, ReportType,
    ProfileInput, MealInput, FitnessInput, SleepInput
)
from utils import (
    normalize_name, build_full_name, calculate_bmi,
    parse_to_utc_seconds, extract_date_from_timestamp, date_to_day_range,
    format_profile_completion, safe_str,
    generate_profile_id, generate_meal_summary_id, generate_meal_id,
    generate_meal_recommendation_id, generate_fitness_summary_id,
    generate_fitness_hour_id, generate_sleep_summary_id
)


# ============================================================================
# Profile chunker
# ============================================================================

def chunk_profile(profile: ProfileInput) -> List[ProcessedChunk]:
    """
    Create profile summary chunk from patient data.
    
    Template:
        Profile for {full_name} (ID: {patient_id}):
        DOB: {dob}, Gender: {gender}.
        Anthro: height {height} cm, weight {weight} kg, waist {waist} cm[, BMI {bmi}].
        Contact: {email}, {phone}.
        Profile completion: {completion}.
        Locale: {locale}; Created: {created_at}.
    
    Args:
        profile: ProfileInput model
        
    Returns:
        List containing single profile chunk
    """
    # Normalize names
    first = normalize_name(profile.first_name)
    last = normalize_name(profile.last_name)
    full_name = build_full_name(first, last)
    
    # Calculate BMI
    bmi = calculate_bmi(profile.height, profile.weight)
    
    # Build text
    text_parts = [
        f"Profile for {full_name or 'Unknown'} (ID: {profile.patient_id}):"
    ]
    
    if profile.dob or profile.gender:
        text_parts.append(
            f"DOB: {safe_str(profile.dob)}, Gender: {safe_str(profile.gender)}."
        )
    
    # Anthropometrics
    anthro_parts = []
    if profile.height:
        anthro_parts.append(f"height {profile.height} cm")
    if profile.weight:
        anthro_parts.append(f"weight {profile.weight} kg")
    if profile.waist:
        anthro_parts.append(f"waist {profile.waist} cm")
    if bmi:
        anthro_parts.append(f"BMI {bmi}")
    
    if anthro_parts:
        text_parts.append(f"Anthro: {', '.join(anthro_parts)}.")
    
    # Contact
    if profile.email or profile.phone_number:
        text_parts.append(
            f"Contact: {safe_str(profile.email)}, {safe_str(profile.phone_number)}."
        )
    
    # Profile completion
    completion_str = format_profile_completion(profile.profile_completion)
    text_parts.append(f"Profile completion: {completion_str}.")
    
    # Locale and created
    text_parts.append(
        f"Locale: {safe_str(profile.locale, 'Unknown')}; "
        f"Created: {safe_str(profile.created_at)}."
    )
    
    text = " ".join(text_parts)
    
    # Build payload
    payload = ChunkPayload(
        patient_id=profile.patient_id,
        full_name=full_name,
        source=Source.PROFILE,
        section=Section.SUMMARY,
        report_type=None,
        date=None,
        start_ts=None,
        end_ts=None,
        text=text
    )
    
    point_id = generate_profile_id(profile.patient_id)
    
    return [ProcessedChunk(point_id=point_id, payload=payload)]


# ============================================================================
# Meals chunker
# ============================================================================

def chunk_meals(meal_data: MealInput) -> List[ProcessedChunk]:
    """
    Create chunks for daily meal data.
    
    Creates:
    - 1 day summary chunk
    - 1 chunk per meal
    - 1 recommendations chunk (if present)
    
    Args:
        meal_data: MealInput model
        
    Returns:
        List of meal chunks
    """
    chunks: List[ProcessedChunk] = []
    
    # Parse date to timestamps
    try:
        start_ts, end_ts = date_to_day_range(meal_data.date)
    except ValueError:
        return []  # Skip if date is invalid
    
    # === Day summary chunk ===
    summary_parts = [
        f"Meals summary for {meal_data.date}:"
    ]
    
    if meal_data.meal_count > 0:
        summary_parts.append(f"{meal_data.meal_count} meal(s) logged.")
    else:
        summary_parts.append("No meals logged.")
    
    # Daily totals
    totals = []
    if meal_data.calories:
        totals.append(f"{meal_data.calories} kcal")
    if meal_data.proteins:
        totals.append(f"P {meal_data.proteins}g")
    if meal_data.carbohydrates:
        totals.append(f"C {meal_data.carbohydrates}g")
    if meal_data.fats:
        totals.append(f"F {meal_data.fats}g")
    if meal_data.fiber:
        totals.append(f"Fiber {meal_data.fiber}g")
    
    if totals:
        summary_parts.append(f"Daily totals: {', '.join(totals)}.")
    
    summary_text = " ".join(summary_parts)
    
    summary_payload = ChunkPayload(
        patient_id=meal_data.patient_id,
        full_name=None,
        source=Source.MEALS,
        section=Section.SUMMARY,
        report_type=ReportType.DAILY,
        date=meal_data.date,
        start_ts=start_ts,
        end_ts=end_ts,
        text=summary_text
    )
    
    summary_id = generate_meal_summary_id(meal_data.patient_id, meal_data.date)
    chunks.append(ProcessedChunk(point_id=summary_id, payload=summary_payload))
    
    # === Per-meal chunks ===
    for meal in meal_data.meals:
        meal_id = meal.get("id") or meal.get("_id")
        if not meal_id:
            continue  # Skip meals without ID
        
        meal_text_parts = [
            f"Meal ({safe_str(meal.get('name'), 'Unknown')}) on {meal_data.date}"
        ]
        
        if "time" in meal:
            meal_text_parts[0] += f" {meal['time']}"
        meal_text_parts[0] += ":"
        
        # Items
        items = meal.get("items", [])
        if items:
            item_strs = []
            for item in items:
                item_name = item.get("name", "Unknown item")
                item_qty = item.get("quantity", "")
                item_strs.append(f"{item_name} ({item_qty})".strip())
            meal_text_parts.append(f"Items: {', '.join(item_strs)}.")
        
        # Macros
        macros = meal.get("total_macro_nutritional_value", {})
        if macros:
            macro_parts = []
            if "calories" in macros:
                macro_parts.append(f"{macros['calories']} kcal")
            if "proteins" in macros:
                macro_parts.append(f"P {macros['proteins']}g")
            if "carbohydrates" in macros:
                macro_parts.append(f"C {macros['carbohydrates']}g")
            if "fats" in macros:
                macro_parts.append(f"F {macros['fats']}g")
            if "fiber" in macros:
                macro_parts.append(f"Fiber {macros['fiber']}g")
            
            if macro_parts:
                meal_text_parts.append(f"Macros: {', '.join(macro_parts)}.")
        
        # Micros
        micros = meal.get("total_micro_nutritional_value", {})
        if micros:
            micro_parts = []
            for key, value in micros.items():
                if value and key != "_id":
                    # Format key nicely (calcium_mg -> Ca)
                    display_key = key.replace("_mg", "").replace("_", " ").title()
                    micro_parts.append(f"{display_key} {value}mg")
            
            if micro_parts:
                meal_text_parts.append(f"Micros: {', '.join(micro_parts[:6])}.")  # Limit length
        
        # Feedback
        if "feedback" in meal and meal["feedback"]:
            feedback = meal["feedback"]
            if len(feedback) > 200:
                feedback = feedback[:197] + "..."
            meal_text_parts.append(f"Feedback: {feedback}")
        
        meal_text = " ".join(meal_text_parts)
        
        meal_payload = ChunkPayload(
            patient_id=meal_data.patient_id,
            full_name=None,
            source=Source.MEALS,
            section=Section.MEAL,
            report_type=ReportType.DAILY,
            date=meal_data.date,
            start_ts=start_ts,
            end_ts=end_ts,
            text=meal_text
        )
        
        meal_point_id = generate_meal_id(meal_data.patient_id, meal_data.date, str(meal_id))
        chunks.append(ProcessedChunk(point_id=meal_point_id, payload=meal_payload))
    
    # === Recommendations chunk ===
    if meal_data.diet_recommendations:
        rec = meal_data.diet_recommendations
        rec_parts = [f"Diet recommendations for {meal_data.date}:"]
        
        if "total_calories" in rec:
            rec_parts.append(f"Target calories: {rec['total_calories']} kcal.")
        if "proteins" in rec:
            rec_parts.append(f"Target proteins: {rec['proteins']}g.")
        if "carbohydrates" in rec:
            rec_parts.append(f"Target carbs: {rec['carbohydrates']}g.")
        if "fats" in rec:
            rec_parts.append(f"Target fats: {rec['fats']}g.")
        
        rec_text = " ".join(rec_parts)
        
        rec_payload = ChunkPayload(
            patient_id=meal_data.patient_id,
            full_name=None,
            source=Source.MEALS,
            section=Section.RECOMMENDATION,
            report_type=ReportType.DAILY,
            date=meal_data.date,
            start_ts=start_ts,
            end_ts=end_ts,
            text=rec_text
        )
        
        rec_id = generate_meal_recommendation_id(meal_data.patient_id, meal_data.date)
        chunks.append(ProcessedChunk(point_id=rec_id, payload=rec_payload))
    
    return chunks


# ============================================================================
# Fitness chunker
# ============================================================================

def chunk_fitness(fitness: FitnessInput, include_hourly: bool = False) -> List[ProcessedChunk]:
    """
    Create chunks for fitness data.
    
    Always creates summary chunk.
    Optionally creates hourly chunks (disabled by default to reduce index size).
    
    Args:
        fitness: FitnessInput model
        include_hourly: Whether to create hourly chunks
        
    Returns:
        List of fitness chunks
    """
    chunks: List[ProcessedChunk] = []
    
    # Skip if missing required data
    if not fitness.start_date or not fitness.end_date:
        return []  # Skip if dates missing
    
    # Parse timestamps
    start_ts = parse_to_utc_seconds(fitness.start_date)
    end_ts = parse_to_utc_seconds(fitness.end_date)
    
    if start_ts is None or end_ts is None:
        return []  # Skip if dates invalid
    
    # Derive canonical date
    date = extract_date_from_timestamp(start_ts)
    
    # Get report type safely
    report_type_str = fitness.report_type.value if fitness.report_type else "daily"
    
    # === Summary chunk ===
    summary_parts = [
        f"Fitness {report_type_str} summary for {date}:"
    ]
    
    summary_parts.append(f"Steps: {fitness.steps or 0}.")
    summary_parts.append(f"Active duration: {fitness.active_duration or 0} min.")
    
    # Peak activity
    if fitness.peak_activity_time:
        peak = fitness.peak_activity_time
        peak_hour = safe_str(peak.get("hour"), "Unknown")
        peak_steps = safe_str(peak.get("max_steps"), "0")
        summary_parts.append(f"Peak hour: {peak_hour} with {peak_steps} steps.")
    
    # Activity distribution
    if fitness.activity_distribution:
        dist = fitness.activity_distribution
        dist_parts = []
        for period in ["morning", "afternoon", "evening"]:
            if period in dist:
                data = dist[period]
                steps = data.get("steps", 0)
                duration = data.get("active_duration", 0)
                dist_parts.append(f"{period.title()}: {steps} steps ({duration}m)")
        
        if dist_parts:
            summary_parts.append(f"Distribution — {', '.join(dist_parts)}.")
    
    # Inactive periods
    if fitness.inactive_periods and len(fitness.inactive_periods) > 0:
        longest = max(fitness.inactive_periods, key=lambda x: x.get("duration", 0))
        duration = longest.get("duration", 0)
        summary_parts.append(f"Longest inactive: {duration} min.")
    
    summary_text = " ".join(summary_parts)
    
    summary_payload = ChunkPayload(
        patient_id=fitness.patient_id,
        full_name=None,
        source=Source.FITNESS,
        section=Section.SUMMARY,
        report_type=fitness.report_type if fitness.report_type else ReportType.DAILY,
        date=date,
        start_ts=start_ts,
        end_ts=end_ts,
        text=summary_text
    )
    
    summary_id = generate_fitness_summary_id(
        fitness.patient_id,
        report_type_str,
        start_ts
    )
    chunks.append(ProcessedChunk(point_id=summary_id, payload=summary_payload))
    
    # === Hourly chunks (optional) ===
    if include_hourly and fitness.hourly_stats:
        for hour_data in fitness.hourly_stats:
            hour = hour_data.get("hour")
            if hour is None:
                continue
            
            hour_text = f"Fitness hour {hour} on {date}: "
            hour_parts = []
            
            if "steps" in hour_data:
                hour_parts.append(f"{hour_data['steps']} steps")
            if "active_duration" in hour_data:
                hour_parts.append(f"{hour_data['active_duration']} min active")
            
            hour_text += ", ".join(hour_parts) + "."
            
            hour_payload = ChunkPayload(
                patient_id=fitness.patient_id,
                full_name=None,
                source=Source.FITNESS,
                section=Section.HOUR,
                report_type=fitness.report_type if fitness.report_type else ReportType.DAILY,
                date=date,
                start_ts=start_ts,
                end_ts=end_ts,
                text=hour_text
            )
            
            hour_id = generate_fitness_hour_id(
                fitness.patient_id,
                report_type_str,
                start_ts,
                hour
            )
            chunks.append(ProcessedChunk(point_id=hour_id, payload=hour_payload))
    
    return chunks


# ============================================================================
# Sleep chunker
# ============================================================================

def chunk_sleep(sleep: SleepInput) -> List[ProcessedChunk]:
    """
    Create summary chunk for sleep data.
    
    Even with zero data, creates explicit chunk saying "no sleep records".
    
    Args:
        sleep: SleepInput model
        
    Returns:
        List containing single sleep summary chunk
    """
    # Skip if missing required data
    if not sleep.start_date or not sleep.end_date:
        return []  # Skip if dates missing
    
    # Parse timestamps
    start_ts = parse_to_utc_seconds(sleep.start_date)
    end_ts = parse_to_utc_seconds(sleep.end_date)
    
    if start_ts is None or end_ts is None:
        return []
    
    date = extract_date_from_timestamp(start_ts)
    
    # Get report type safely
    report_type_str = sleep.report_type.value if sleep.report_type else "daily"
    
    # Build text
    text_parts = [f"Sleep {report_type_str} report for {date}:"]
    
    if sleep.quality_analysis:
        qa = sleep.quality_analysis
        quality = qa.get("sleep_quality", "unknown")
        deep = qa.get("deep_sleep_percentage", 0)
        rem = qa.get("rem_sleep_percentage", 0)
        awake = qa.get("awake_time_percentage", 0)
        
        text_parts.append(
            f"quality {quality}, deep {deep}%, REM {rem}%, awake {awake}%."
        )
        
        # Check for zero data
        if deep == 0 and rem == 0 and awake == 0:
            text_parts.append("Total duration unavailable or zero.")
    else:
        text_parts.append("No sleep records available.")
    
    text = " ".join(text_parts)
    
    payload = ChunkPayload(
        patient_id=sleep.patient_id,
        full_name=None,
        source=Source.SLEEP,
        section=Section.SUMMARY,
        report_type=sleep.report_type if sleep.report_type else ReportType.DAILY,
        date=date,
        start_ts=start_ts,
        end_ts=end_ts,
        text=text
    )
    
    point_id = generate_sleep_summary_id(
        sleep.patient_id,
        report_type_str,
        start_ts
    )
    
    return [ProcessedChunk(point_id=point_id, payload=payload)]

