"""
Patient‑onboarding chatbot (FastAPI)

• Three‑stage intake: Basic ➜ Diet/Lifestyle ➜ Medical
• Adaptive prompts (chatty → simpler → ultra‑simple)
• Uses OpenAI `gpt-5-nano` for paraphrasing, simplification, and value extraction
• Returns a single dictionary payload when finished

Run:
    uvicorn main:app --reload
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional

from openai import OpenAI        # pip install openai
from fastapi import FastAPI
# --------------------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware
# --------------------------------------------------------------
from pydantic import BaseModel

# ─────────────────────────  CONFIG  ──────────────────────────
MODEL_ID = "gpt-3.5-turbo"                   # one place to change model
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "demo-key-not-set"))

# ─────────────────────────  DATA CLASSES  ────────────────────
class Stage(Enum):
    BASIC = auto()
    DIET = auto()
    MEDICAL = auto()
    COMPLETE = auto()


class Slot(BaseModel):
    key: str
    prompt: str
    validator_regex: str | None = None

    def validate(self, answer: str) -> bool:
        if self.validator_regex is None:
            return True
        return bool(re.fullmatch(self.validator_regex, answer.strip(), re.IGNORECASE))


# ─────────────────────────  SLOT LISTS  ──────────────────────
BASIC_SLOTS: List[Slot] = [
    Slot(key="full_name",
         prompt="May I have your full name? Please provide both your first name and last name (e.g., 'John Smith')",
         validator_regex=None),  # Custom validation used
    Slot(key="email",
         prompt="What's the best email for you?",
         validator_regex=r"[^@\s]+@[^@\s]+\.[^@\s]+"),
    Slot(key="phone",
         prompt="What's your phone number? (Please enter exactly 10 digits, e.g., 9876543210)",
         validator_regex=r"^\d{10}$"),
    Slot(key="date_of_birth",
         prompt="What's your date of birth? (Format: YYYY-MM-DD, example: 1990-05-15)",
         validator_regex=None),  # Custom validation needed
    Slot(key="gender",
         prompt="Gender? (male / female / other / prefer not to say)",
         validator_regex=r"(male|female|other|prefer not to say)"),
    Slot(key="weight_kg",
         prompt="What's your current weight in kilograms? (e.g., 70 or 65.5)",
         validator_regex=r"^\d{1,3}(\.\d{1,2})?$"),
    Slot(key="height",
         prompt="What's your height? (Please specify in cm like '175' or in feet/inches like '5 ft 8 in')"),
    Slot(key="waist_cm",
         prompt="What's your waist circumference in centimeters? (Measure around your natural waistline, e.g., 85)",
         validator_regex=r"^\d{2,3}$"),
    Slot(key="locale",
         prompt="Which city are you currently living in? (This helps us provide location-specific health advice)")
]

DIET_SLOTS: List[Slot] = [
    Slot(key="activity_level",
         prompt="How would you describe your daily physical activity level? Choose from: little/no exercise, light activity (1-3 days/week), moderate activity (3-5 days/week), hard activity (6-7 days/week), or very hard (2+ times daily)",
         validator_regex=r"(little|no|light|moderate|hard|very hard)"),
    Slot(key="meals_per_day",
         prompt="How many main meals do you typically eat per day? (Please enter a number like 2, 3, or 4)",
         validator_regex=r"^[1-6]$"),
    Slot(key="snacks_per_day",
         prompt="How many snacks do you usually have between meals per day? (Enter 0 if none, or a number like 1, 2, 3)",
         validator_regex=r"^[0-5]$"),
    Slot(key="diet_pref",
         prompt="What's your dietary preference? Choose from: pure vegetarian, mostly vegetarian, non-vegetarian, or eggitarian (vegetarian + eggs)"),
    Slot(key="cuisine_pref",
         prompt="What are your favorite types of cuisine? (Please list them separated by commas, e.g., 'Indian, Italian, Chinese')"),
    Slot(key="alcohol",
         prompt="Do you consume alcohol? If yes, please specify how often and how much (e.g., '2 glasses wine weekly' or 'none')"),
    Slot(key="smoking",
         prompt="What are your smoking habits? Please specify: number of cigarettes per day and for how many years, or simply type 'none' if you don't smoke"),
    Slot(key="sleep_quality",
         prompt="How would you rate your overall sleep quality? Choose from: poor, average, good, or excellent",
         validator_regex=r"(poor|average|good|excellent)"),
    Slot(key="wake_fresh",
         prompt="Do you usually wake up feeling fresh and rested in the morning? (Please answer 'yes' or 'no')",
         validator_regex=r"(yes|no)"),
    Slot(key="drowsy_day",
         prompt="Do you feel drowsy or sleepy during the daytime? (Please answer 'yes' or 'no')",
         validator_regex=r"(yes|no)"),
    Slot(key="sleep_hours",
         prompt="On average, how many hours do you sleep per night? (Enter a number like 7, 7.5, or 8)",
         validator_regex=r"^\d{1,2}(\.\d)?$"),
]

MEDICAL_SLOTS: List[Slot] = [
    Slot(key="diabetes_type",
         prompt="Have you been diagnosed with any type of diabetes? Choose from: type1, type2, pre-diabetes, gestational diabetes, or 'none' if not diagnosed",
         validator_regex=r"(type ?1|type ?2|pre|gestational|none)"),
    Slot(key="medication_photo",
         prompt="Do you currently take any prescription medications? Please list them or type 'none' if you don't take any medications"),
]

STAGE_TO_SLOTS = {
    Stage.BASIC: BASIC_SLOTS,
    Stage.DIET: DIET_SLOTS,
    Stage.MEDICAL: MEDICAL_SLOTS,
}

# ─────────────────────────  SESSION STATE  ───────────────────
class SessionState(BaseModel):
    stage: Stage = Stage.BASIC
    slot_idx: int = 0
    answers: Dict[str, str] = {}
    attempts: Dict[str, int] = {}

    def slot(self) -> Slot:
        return STAGE_TO_SLOTS[self.stage][self.slot_idx]

    def advance(self):
        self.attempts[self.slot().key] = 0
        self.slot_idx += 1
        if self.slot_idx >= len(STAGE_TO_SLOTS[self.stage]):
            self.slot_idx = 0
            self.stage = {
                Stage.BASIC: Stage.DIET,
                Stage.DIET: Stage.MEDICAL,
                Stage.MEDICAL: Stage.COMPLETE,
            }[self.stage]
    
    def get_stage_transition_message(self) -> str:
        """Get transition message when moving to a new stage"""
        if self.stage == Stage.DIET and self.slot_idx == 0:
            return "Great! Now let's move on to understanding your lifestyle and dietary habits. This will help us provide personalized health recommendations."
        elif self.stage == Stage.MEDICAL and self.slot_idx == 0:
            return "Perfect! Finally, let's cover some important medical information to complete your comprehensive health profile."
        return None

    def done(self) -> bool:
        return self.stage is Stage.COMPLETE


# ─────────────────────────  GPT HELPERS  ─────────────────────
SYS_PARAPHRASE = "Rewrite the following intake question into a friendly chat sentence (≤15 words)."
SYS_SIMPLIFY = "Rewrite the question so an 8‑year‑old can understand, one short sentence."
SYS_EXTRACT = "Extract ONLY the required slot value (no extra words)."


def gpt(msgs, max_tokens=30) -> str:
    try:
        resp = client.chat.completions.create(
            model=MODEL_ID,
            messages=msgs,
            temperature=0,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
    except Exception as exc:
        print("[WARN] GPT error:", exc)
        return ""


def paraphrase(text: str) -> str:
    return gpt(
        [{"role": "system", "content": SYS_PARAPHRASE},
         {"role": "user", "content": text}]
    ) or text


def simplify(text: str) -> str:
    return gpt(
        [{"role": "system", "content": SYS_SIMPLIFY},
         {"role": "user", "content": text}]
    ) or text


def validate_full_name(name_str: str) -> bool:
    """Custom validation for full name - requires first and last name"""
    try:
        name_clean = name_str.strip()
        # Check if empty
        if not name_clean:
            return False
            
        # Split by whitespace
        name_parts = name_clean.split()
        
        # Must have exactly 2-4 parts (reasonable range for names)
        if len(name_parts) < 2 or len(name_parts) > 4:
            return False
            
        # Check for common words that indicate this is not a proper name
        common_words = {'my', 'name', 'is', 'i', 'am', 'called', 'the', 'a', 'an'}
        for part in name_parts:
            if part.lower() in common_words:
                return False
                
        # Each part must be at least 2 characters and contain only letters
        for part in name_parts:
            if len(part) < 2 or not part.isalpha():
                return False
                
        # Names should generally be proper nouns, but we'll be lenient on capitalization  
        # The common words check above should catch most invalid patterns
        return True
    except:
        return False


def validate_date_of_birth(date_str: str) -> bool:
    """Custom validation for date of birth"""
    try:
        # Check if it matches the basic format
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str.strip()):
            return False
        
        # Parse the date
        birth_date = datetime.strptime(date_str.strip(), '%Y-%m-%d')
        
        # Check if it's not in the future
        if birth_date > datetime.now():
            return False
            
        # Check if it's reasonable (not older than 120 years)
        if (datetime.now() - birth_date).days > 120 * 365:
            return False
            
        return True
    except ValueError:
        return False


def extract_name_from_text(text: str) -> Optional[str]:
    """Extract name from natural language patterns"""
    text_lower = text.lower().strip()
    
    # Common patterns for name introduction
    patterns = [
        r"my name is (.+)",
        r"i am (.+)",
        r"i'm (.+)",  
        r"call me (.+)",
        r"it's (.+)",
        r"this is (.+)",
        r"name is (.+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            extracted_name = match.group(1).strip()
            # Convert to title case for proper name format
            name_parts = extracted_name.split()
            if name_parts:
                return ' '.join(part.capitalize() for part in name_parts)
    
    return None


def extract_val(user_msg: str, slot: Slot) -> Optional[str]:
    # Custom validation for full name
    if slot.key == "full_name":
        if validate_full_name(user_msg):
            return user_msg.strip()
            
        # Try pattern-based extraction first
        extracted_name = extract_name_from_text(user_msg)
        if extracted_name and validate_full_name(extracted_name):
            return extracted_name
            
        # Fallback to GPT if available
        val = gpt(
            [{"role": "system", "content": SYS_EXTRACT},
             {"role": "user", "content": f"Extract full name (first and last name) from: {user_msg}"}]
        )
        return val if val and validate_full_name(val) else None
    
    # Custom validation for date of birth
    if slot.key == "date_of_birth":
        if validate_date_of_birth(user_msg):
            return user_msg.strip()
        val = gpt(
            [{"role": "system", "content": SYS_EXTRACT},
             {"role": "user", "content": f"Extract date in YYYY-MM-DD format from: {user_msg}"}]
        )
        return val if validate_date_of_birth(val) else None
    
    # Standard validation for other slots
    if slot.validate(user_msg):
        return user_msg.strip()

    val = gpt(
        [{"role": "system", "content": SYS_EXTRACT},
         {"role": "user", "content": f"Slot={slot.key}\nUser={user_msg}"}]
    )
    return val if slot.validate(val) else None


# ─────────────────────────  FASTAPI APP  ─────────────────────
app = FastAPI(title="Patient Onboarding Chatbot")
# --------------------------------------------------------------

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------------------------------------
SESSIONS: Dict[str, SessionState] = {}


class ChatIn(BaseModel):
    session_id: str
    message: Optional[str] = None


class ChatOut(BaseModel):
    bot_reply: str
    complete: bool = False
    payload: Optional[Dict[str, str]] = None


def build_prompt(sess: SessionState) -> str:
    slot = sess.slot()
    tries = sess.attempts.get(slot.key, 0)
    if tries == 0:
        return paraphrase(slot.prompt)
    if tries >= 1:
        return simplify(slot.prompt)
    return f"{slot.key.replace('_', ' ').title()} (one word/number please):"


@app.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn):
    sess = SESSIONS.setdefault(payload.session_id, SessionState())

    # 1. Already finished
    if sess.done():
        return ChatOut(bot_reply="All done ✅", complete=True, payload=sess.answers)

    # 2. First turn or empty → welcome or ask
    if not payload.message:
        # Very first interaction - send welcome message
        if sess.stage == Stage.BASIC and sess.slot_idx == 0 and not sess.answers:
            return ChatOut(bot_reply="👋 Welcome! I'm here to help with your patient onboarding. I'll ask you some questions to get to know you better. Let's start!")
        # Otherwise, just ask the current question
        return ChatOut(bot_reply=build_prompt(sess))

    # 3. Try to extract slot value
    slot = sess.slot()
    value = extract_val(payload.message, slot)
    if value is None:
        sess.attempts[slot.key] = sess.attempts.get(slot.key, 0) + 1
        return ChatOut(bot_reply=build_prompt(sess))

    # 4. Save & move on
    sess.answers[slot.key] = value
    sess.advance()

    if sess.done():
        # split full_name
        answers = sess.answers.copy()
        name_parts = answers.pop("full_name", "").split()
        answers["first_name"] = name_parts[0] if name_parts else ""
        answers["last_name"] = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        return ChatOut(bot_reply="Great, we've got everything 🎉", complete=True, payload=answers)

    # 5. Check for stage transition message
    transition_msg = sess.get_stage_transition_message()
    if transition_msg:
        return ChatOut(bot_reply=transition_msg)
    
    # 6. Ask next
    return ChatOut(bot_reply=build_prompt(sess))
