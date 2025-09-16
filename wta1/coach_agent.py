# coach_agent.py
import os, json, base64
from typing import Dict, Any, List, Optional
from agents import Agent, Runner, SQLiteSession  # OpenAI Agents SDK
from agents.tool import function_tool
from openai import OpenAI                        # For vision + chat calls
from dataclasses import dataclass

# ---- OpenAI Clients ----
OAI = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- Vector store (ChromaDB implementation) ----
from vector_store import vector_store

# ---- Light in-process caches (persist in Postgres via db.py) ----
INBODY_CACHE: Dict[str, dict] = {}
PROFILE: Dict[str, dict] = {}
FACTS_CACHE: Dict[str, dict] = {}
SELECTED_DOCS: Dict[str, List[str]] = {}
# Track the most recently active user from the frontend session
CURRENT_USER_ID: Optional[str] = None

# Robust resolver to map SDK-passed user_id to the active app user
def _resolve_user_id(passed: str) -> str:
    if passed in SELECTED_DOCS or passed in PROFILE or passed in INBODY_CACHE or passed in FACTS_CACHE:
        return passed
    if CURRENT_USER_ID is not None:
        return CURRENT_USER_ID
    if len(SELECTED_DOCS) == 1:
        return list(SELECTED_DOCS.keys())[0]
    return passed

# ---------------- Normalizers for InBody ----------------
_INBODY_KEYS = {
  "weight_kg": None, "target_weight_kg": None, "bmi": None,
  "pbf_pct": None, "bfm_kg": None, "smm_kg": None, "total_body_water_l": None,
  "bmr_kcal": None, "ecw_ratio": None, "phase_angle_deg": None,
  "smi_kg_m2": None, "inbody_score_100": None,
  "weight_control_delta_kg": None, "fat_control_delta_kg": None, "muscle_control_delta_kg": None,
  "waist_hip_ratio": None, "visceral_fat_level": None,
  "overall_health_score": None, "raw_text": None
}

def _num(x):
    if x is None: return None
    if isinstance(x, (int, float)): return float(x)
    s = str(x).strip()
    for t in ["kg/m²","kg/m2","kg","kcal","L","%","°","points"]:
        s = s.replace(t, "")
    s = s.replace("−","-").strip()
    out, dot, sign = "", False, True
    for ch in s:
        if ch.isdigit(): out += ch
        elif ch in "+-" and sign: out += ch; sign = False
        elif ch == "." and not dot: out += ch; dot = True; sign = False
        else: break
    try: return float(out) if out not in ("","+","-",".") else None
    except: return None

def _normalize_inbody(d: dict) -> dict:
    out = dict(_INBODY_KEYS)
    for k in out: 
        if k in d: out[k] = _num(d[k])
    if out["overall_health_score"] is None and out["inbody_score_100"] is not None:
        out["overall_health_score"] = out["inbody_score_100"]
    if isinstance(d.get("raw_text"), str):
        out["raw_text"] = d["raw_text"]
    return out

# ---------------- Tools (Agents SDK) ----------------
@function_tool
def save_profile(user_id: str, exercise_pref: Optional[str] = None,
                 target_weight_kg: Optional[float] = None,
                 baseline_weight_kg: Optional[float] = None) -> dict:
    """Persist simple profile fields in memory (also persist to Postgres in api layer)."""
    p = PROFILE.get(user_id, {})
    if exercise_pref is not None: p["exercise_pref"] = exercise_pref
    if target_weight_kg is not None: p["target_weight_kg"] = target_weight_kg
    if baseline_weight_kg is not None: p["baseline_weight_kg"] = baseline_weight_kg
    PROFILE[user_id] = p
    return {"ok": True, "profile": p}

@function_tool
def parse_inbody_vision(user_id: str, file_b64: str) -> dict:
    """Parse an InBody image/PDF via vision and cache it."""
    data_url = f"data:image/jpeg;base64,{file_b64}"
    system = (
        "You are a precise OCR+parser for InBody reports. "
        "Extract ONLY numeric values following the target JSON keys. "
        "If missing, return null. Return JSON, no prose."
    )
    user_prompt = f"Return JSON with keys exactly:\n{json.dumps(_INBODY_KEYS)}"
    resp = OAI.chat.completions.create(
        model="gpt-4o",                                 # vision-capable
        response_format={"type": "json_object"},
        temperature=0.0,
        messages=[
            {"role":"system","content":system},
            {"role":"user","content":[
                {"type":"text","text":user_prompt},
                {"type":"image_url","image_url":{"url":data_url}}
            ]}
        ]
    )
    raw = json.loads(resp.choices[0].message.content)
    parsed = _normalize_inbody(raw)
    INBODY_CACHE[user_id] = parsed
    # set baseline/target when first seen
    p = PROFILE.get(user_id, {})
    if parsed.get("weight_kg") and not p.get("baseline_weight_kg"):
        p["baseline_weight_kg"] = parsed["weight_kg"]
    if parsed.get("target_weight_kg"): p["target_weight_kg"] = parsed["target_weight_kg"]
    PROFILE[user_id] = p
    return {"ok": True, "inbody": parsed}

@function_tool
def facts_from_rag(user_id: str) -> dict:
    """Normalize health facts from your pre-indexed RAG store (SMBG, vitals, etc.)."""
    actual_user_id = _resolve_user_id(user_id)
    if actual_user_id in FACTS_CACHE: return FACTS_CACHE[actual_user_id]
    ctx = vector_store.get_context(actual_user_id, "Most recent vitals, SMBG, labs, constraints, injuries, meds.", 6)
    prompt = f"""Return JSON only with keys:
glucose: {{ fasting_mgdl, postprandial_mgdl, hba1c_pct }}
bp: {{ systolic, diastolic }}
hr_rest
sleep_hours
steps_per_day
lipids: {{ ldl, hdl, tg }}
injuries: []
contraindications: []
meds: []
notes: []
Use null if missing. Be conservative. Context:\n{ctx[:6000]}"""
    res = OAI.chat.completions.create(model="gpt-4o-mini",
                                      response_format={"type":"json_object"},
                                      temperature=0,
                                      messages=[{"role":"user","content":prompt}])
    facts = json.loads(res.choices[0].message.content)
    FACTS_CACHE[actual_user_id] = facts
    return facts

@function_tool
def inbody_from_rag(user_id: str) -> dict:
    """Extract InBody analysis data from vector database for personalized fitness recommendations."""
    actual_user_id = _resolve_user_id(user_id)
    
    selected_docs = SELECTED_DOCS.get(actual_user_id, [])
    
    if selected_docs:
        # Use selected documents for RAG
        ctx = vector_store.get_selected_documents_context(actual_user_id, selected_docs, 8)
        source_type = "selected_documents"
    else:
        # Fall back to automatic InBody detection
        ctx = vector_store.get_inbody_context(actual_user_id, 8)
        source_type = "automatic_detection"

    if not ctx or ctx.strip() == "":
        if selected_docs:
            return {
                "available": False,
                "message": f"No InBody data found in your {len(selected_docs)} selected document(s). Please ensure you've selected InBody reports for analysis."
            }
        else:
            return {
                "available": False,
                "message": "No InBody data found in your uploaded documents. Please upload your InBody report and select it for analysis."
            }

    prompt = f"""Extract InBody analysis data from the following context. Return JSON with these specific keys:

Core Measurements:
- weight_kg: Current body weight
- target_weight_kg: Target weight if specified
- bmi: Body Mass Index
- pbf_pct: Body Fat Percentage
- bfm_kg: Body Fat Mass (kg)
- smm_kg: Skeletal Muscle Mass (kg)
- tbw_l: Total Body Water (Liters)
- ecw_ratio: Extracellular Water Ratio
- phase_angle_deg: Phase Angle (degrees)
- smi_kg_m2: Skeletal Muscle Index

Health Scores:
- inbody_score_100: Overall InBody Score (0-100)
- overall_health_score: Health Assessment Score

Control Data:
- weight_control_delta_kg: Weight control recommendation
- fat_control_delta_kg: Fat control recommendation
- muscle_control_delta_kg: Muscle control recommendation

Additional Metrics:
- waist_hip_ratio: Waist-to-Hip Ratio
- visceral_fat_level: Visceral Fat Level
- bmr_kcal: Basal Metabolic Rate (kcal/day)

Analysis:
- body_balance: Left/Right balance assessment
- segment_analysis: Segment-by-segment analysis
- recommendations: Any recommendations from the report

Notes:
- raw_text: Original text from the report
- assessment_date: Date of the assessment if available

Use null for missing values. Be precise and extract only factual data from the context.

Context from uploaded documents:
{ctx[:8000]}"""

    try:
        res = OAI.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )
        inbody_data = json.loads(res.choices[0].message.content)

        # Add metadata
        inbody_data["available"] = True
        inbody_data["source"] = "vector_database"
        inbody_data["source_type"] = source_type
        inbody_data["query_timestamp"] = "latest"

        # Automatically set baseline weight from InBody data if not already set
        if inbody_data.get("weight_kg") is not None:
            profile = PROFILE.get(actual_user_id, {})
            if "baseline_weight_kg" not in profile:
                profile["baseline_weight_kg"] = inbody_data["weight_kg"]
                PROFILE[actual_user_id] = profile

        return inbody_data

    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "message": "Error processing InBody data from vector database"
        }

@function_tool
def exercise_plan(user_id: str, exercise_pref: Optional[str] = None) -> dict:
    """
    Return a 1-day plan (list of steps) generated by LLM, but ONLY after preference is known.
    Behavior:
    - If no valid preference is known, ask for it and DO NOT generate a plan.
    - If a preference is provided or stored, confirm it and then generate the plan.
    Tool output contract:
    - If asking: {"ask_preference": true, "message": "..."}
    - If generating: {"ask_preference": false, "confirmed_pref": "<pref>", "plan": [...]}
    """
    try:
        # 1) Resolve/validate preference
        actual_user_id = _resolve_user_id(user_id)
        p = PROFILE.get(actual_user_id, {})
        pref = (exercise_pref or p.get("exercise_pref") or "").strip().lower()

        # Normalize common variants and handle combinations
        alias = {"home": "basic", "at home": "basic", "bodyweight": "basic"}
        if pref in alias:
            pref = alias[pref]

        # Handle combination preferences (e.g., "gym+cardio", "basic+cardio")
        if "+" in pref or " and " in pref or "&" in pref:
            # Parse combination preferences
            combo_parts = pref.replace(" and ", "+").replace("&", "+").split("+")
            combo_parts = [part.strip() for part in combo_parts]
            # Normalize each part
            normalized_parts = []
            for part in combo_parts:
                if part in alias:
                    part = alias[part]
                normalized_parts.append(part)
            pref = "+".join(normalized_parts)

        # Valid single preferences and combinations
        valid_single = {"basic", "gym", "cardio"}
        valid_combos = {"basic+cardio", "gym+cardio", "basic+gym"}
        all_valid = valid_single.union(valid_combos)
        
        if pref not in all_valid:
            # No valid preference → ask first (do not create a plan)
            return {
                "ask_preference": True,
                "message": (
                    "Before I plan your workout, what's your preference?\n"
                    "**Single Options:**\n"
                    "• basic/home - Bodyweight exercises at home\n"
                    "• gym - Weight training with equipment\n"
                    "• cardio - Cardiovascular focused workout\n\n"
                    "**Combination Options:**\n"
                    "• basic+cardio - Home exercises with cardio\n"
                    "• gym+cardio - Weight training with cardio\n"
                    "• basic+gym - Mix of bodyweight and gym exercises\n\n"
                    "Reply with your choice (e.g., 'gym+cardio' or 'basic')."
                )
            }

        # 2) Persist confirmed preference if not already stored
        if p.get("exercise_pref") != pref:
            p["exercise_pref"] = pref
            PROFILE[actual_user_id] = p

        # 3) Use cached health context (tools should have been called by agent already)
        inbody = INBODY_CACHE.get(actual_user_id, {})
        facts = FACTS_CACHE.get(actual_user_id, {})
        
        # Note: We can't call other function tools from within a function tool
        # The agent should call inbody_from_rag and facts_from_rag before calling this tool

        # 4) Ask LLM to generate the plan (JSON)
        schema = {"plan": ["exercise with sets/reps/duration"]}
        
        # Create detailed prompt based on preference type
        if "+" in pref:
            # Combination preference
            parts = pref.split("+")
            combo_instructions = f"""
Create a COMBINATION workout plan for {pref.upper()} preference.
Structure the workout to include BOTH {parts[0].upper()} and {parts[1].upper()} components:

COMBINATION WORKOUT GUIDELINES:
- Split time between both preferences (e.g., 60% {parts[0]}, 40% {parts[1]})
- Provide specific exercise names, sets, reps, and durations
- Include proper warm-up and cool-down
- Balance strength and cardiovascular elements
- Give EXACT exercise instructions (not just "do cardio")

EXAMPLE FORMAT:
"Warm-up: 5 minutes light jogging in place"
"Squats: 3 sets of 12 reps"
"Jumping Jacks: 2 minutes continuous"
"Push-ups: 3 sets of 8-10 reps"
"""
        else:
            # Single preference
            combo_instructions = f"""
Create a focused {pref.upper()} workout plan.
Provide specific exercise names, sets, reps, and durations for each exercise.
Include proper warm-up and cool-down phases.

EXAMPLE FORMAT:
"Warm-up: 5 minutes dynamic stretching"
"Exercise Name: X sets of Y reps"
"Cardio Exercise: Z minutes at moderate intensity"
"""

        prompt = f"""You are an expert fitness coach. Create a comprehensive 1-day exercise plan (5-8 specific exercises) for preference={pref}.

{combo_instructions}

EXERCISE SPECIFICITY REQUIREMENTS:
- Name EXACT exercises (e.g., "Push-ups", "Dumbbell Bench Press", "Treadmill Running")
- Include specific sets, reps, or duration for each exercise
- Provide intensity levels (light, moderate, vigorous)
- Consider user's current fitness level from InBody data
- Avoid exercises contraindicated by health conditions

PERSONALIZATION based on InBody Analysis:
- BMI {inbody.get('bmi', 'unknown')}: Adjust intensity accordingly
- Body Fat {inbody.get('pbf_pct', 'unknown')}%: Focus on fat-burning if high
- Muscle Mass {inbody.get('smm_kg', 'unknown')} kg: Include strength training if low
- Consider any health constraints from facts

SAFETY CONSIDERATIONS:
- Avoid exercises if user has injuries or medical conditions
- Start with beginner-friendly modifications if BMI > 30
- Include rest periods between sets
- Emphasize proper form over intensity

Return JSON with detailed, actionable exercise plan: {json.dumps(schema)}

InBody Data: {json.dumps(inbody)}
Health Facts: {json.dumps(facts)}"""

        res = OAI.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(res.choices[0].message.content)
        steps = data.get("plan", [])

        if not steps:
            return {
                "ask_preference": False,
                "confirmed_pref": pref,
                "plan": [],
                "message": "I couldn't generate a plan right now. Please try again."
            }

        return {
            "ask_preference": False,
            "confirmed_pref": pref,
            "plan": steps
        }
    except Exception as e:
        return {
            "ask_preference": False,
            "confirmed_pref": exercise_pref or "basic",
            "plan": [],
            "message": f"Error generating exercise plan: {str(e)}"
        }

@function_tool
def abnormalities(user_id: str) -> dict:
    """Return concise abnormalities as list of strings (present vs typical)."""
    actual_user_id = _resolve_user_id(user_id)
    
    # Use cached health context (tools should have been called by agent already)
    inbody = INBODY_CACHE.get(actual_user_id, {})
    facts = FACTS_CACHE.get(actual_user_id, {})
    
    # If no cached data, try to get it from vector store directly
    if not inbody.get("available", False):
        selected_docs = SELECTED_DOCS.get(actual_user_id, [])
        if selected_docs:
            ctx = vector_store.get_selected_documents_context(actual_user_id, selected_docs, 8)
        else:
            ctx = vector_store.get_inbody_context(actual_user_id, 8)
        
        if ctx and ctx.strip():
            # Parse the context to extract InBody data
            prompt = f"""Extract InBody metrics from this data and return as JSON:
{_INBODY_KEYS}
Context: {ctx[:3000]}"""
            res = OAI.chat.completions.create(model="gpt-4o-mini",
                                              response_format={"type":"json_object"},
                                              temperature=0,
                                              messages=[{"role":"user","content":prompt}])
            inbody = json.loads(res.choices[0].message.content)
            inbody["available"] = True
            INBODY_CACHE[actual_user_id] = inbody

    schema = {"abnormalities": ["one-line finding"]}
    prompt = f"""Analyze the InBody data and compare to typical adult ranges.

Focus on:
- BMI classification and body fat percentage ranges
- Skeletal muscle mass and muscle balance
- Metabolic health indicators (BMR, phase angle)
- Body water distribution and ratios
- Visceral fat levels and waist-hip ratio

Return 2–6 one-line flags (≤20 words each) for any abnormalities or concerns.
Use 'No clear abnormalities detected.' if values are within normal ranges.

Consider the user's specific body composition metrics from the InBody analysis.

JSON only: {json.dumps(schema)}

InBody Data: {json.dumps(inbody)}
Additional Health Facts: {json.dumps(facts)}"""
    res = OAI.chat.completions.create(model="gpt-4o-mini",
                                      response_format={"type":"json_object"},
                                      temperature=0,
                                      messages=[{"role":"user","content":prompt}])
    return json.loads(res.choices[0].message.content)

@function_tool
def urgent_recs(user_id: str) -> dict:
    """Return EXACTLY TWO high-impact actions for next 7 days."""
    actual_user_id = _resolve_user_id(user_id)
    
    # Use cached health context (tools should have been called by agent already)
    inbody = INBODY_CACHE.get(actual_user_id, {})
    facts = FACTS_CACHE.get(actual_user_id, {})
    
    # Note: We can't call other function tools from within a function tool
    # The agent should call inbody_from_rag and facts_from_rag before calling this tool

    schema = {"recommendations": ["action 1","action 2"]}
    prompt = f"""Based on the user's InBody analysis and health data, provide EXACTLY TWO urgent, high-impact actions for the next 7 days.

Consider:
- Body composition metrics (BMI, body fat %, muscle mass)
- Metabolic health indicators
- Any specific recommendations from the InBody analysis
- User's current health status and constraints

Each action should be ≤15 words and focused on immediate, measurable improvements.
Be safe, evidence-based, and avoid medical diagnosis.

JSON only: {json.dumps(schema)}

InBody Data: {json.dumps(inbody)}
Additional Health Facts: {json.dumps(facts)}"""
    res = OAI.chat.completions.create(model="gpt-4o-mini",
                                      response_format={"type":"json_object"},
                                      temperature=0,
                                      messages=[{"role":"user","content":prompt}])
    return json.loads(res.choices[0].message.content)

@function_tool
def progress(user_id: str, current_weight_kg: Optional[float] = None) -> dict:
    """Compute progress; ask for current if missing."""
    actual_user_id = _resolve_user_id(user_id)
    base = PROFILE.get(actual_user_id, {}).get("baseline_weight_kg")
    if base is None:
        return {"error": "Baseline missing. Upload InBody first."}
    if current_weight_kg is None:
        return {"question": "What is your current weight (kg)?"}
    delta = round(current_weight_kg - base, 2)
    pct = round((delta/base)*100.0, 2)
    return {"baseline": base, "current": current_weight_kg, "delta_kg": delta, "percent_change": pct}

# ---------------- The Agent (single) ----------------
COACH = Agent(
    name="FitCoach",
    instructions=(
        "You are an AI weight-loss coach with access to InBody analysis data from uploaded documents. "
        "WORKFLOW: "
        "1) For NEW exercise plans: call inbody_from_rag(), then exercise_plan with user preference "
        "2) For exercise MODIFICATIONS/alternatives: provide directly without calling tools (user wants simpler/harder variations) "
        "3) For abnormalities analysis: call inbody_from_rag(), then abnormalities() "
        "4) For health suggestions: call inbody_from_rag(), then urgent_recs() "
        "5) For body composition questions: call inbody_from_rag() to get data "
        "6) For PROGRESS TRACKING: call inbody_from_rag() first to set baseline, then progress() with user's current weight "
        "7) If exercise_plan returns ask_preference=true, ask user to choose from single options (basic/home, gym, cardio) or combinations (basic+cardio, gym+cardio, basic+gym) "
        "8) COMBINATION PREFERENCES: Support mixed workout types like 'gym+cardio' or 'basic+cardio' for comprehensive fitness plans "
        "CONTEXT AWARENESS: If user is asking for modifications to exercises (easier/harder/different), provide alternatives directly. "
        "Only call inbody_from_rag() when you need fresh health data, not for exercise variations. "
        "Use facts_from_rag() for additional health context when needed. "
        "Avoid medical diagnosis; suggest clinician review for concerning indicators. "
        "Be encouraging, concise, and evidence-based."
    ),
    tools=[save_profile, parse_inbody_vision, facts_from_rag, inbody_from_rag,
           exercise_plan, abnormalities, urgent_recs, progress],
    model="gpt-4o-mini"  # used for the agent loop itself
)

# Helper for FastAPI
async def run_agent(user_id: str, message: str,
              selected_document_ids: Optional[List[str]]=None,
              inbody_b64: Optional[str]=None,
              exercise_pref: Optional[str]=None,
              current_weight_kg: Optional[float]=None,
              session_id: Optional[str]=None) -> str:
    """Single entrypoint. Uses Agents SDK session so the loop has short-term memory."""
    sess = SQLiteSession(session_id=session_id or user_id)  # one session per user
    
    # Track the active user for this invocation (used to resolve SDK-renamed IDs)
    global CURRENT_USER_ID
    CURRENT_USER_ID = user_id
    
    # Store selected documents for this user session
    if selected_document_ids is not None:
        SELECTED_DOCS[user_id] = selected_document_ids
    
    # Pre-baked tool invocations if the SPA passed inputs:
    pre = []
    if inbody_b64:
        pre.append({"tool": "parse_inbody_vision", "args": {"user_id": user_id, "file_b64": inbody_b64}})
    if exercise_pref:
        pre.append({"tool": "save_profile", "args": {"user_id": user_id, "exercise_pref": exercise_pref}})
    
    # If selected documents are provided, ensure InBody data is retrieved
    if selected_document_ids:
        # Create a message that will trigger the agent to call inbody_from_rag
        message = f"User has selected documents for analysis. {message}"
    
    for t in pre:
        await Runner.run(COACH, [t], session=None)  # Disable session for tool calls

    # Main turn - use string input for session compatibility
    result = await Runner.run(COACH, message, session=sess)
    return result.final_output or "OK"
