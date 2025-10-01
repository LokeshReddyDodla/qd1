"""LLM service for RAG answer generation."""

from typing import List, Dict, Any
from openai import OpenAI
from config import settings
import structlog

logger = structlog.get_logger()


class LLMService:
    """Service for generating RAG answers using LLM."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_llm_model
        self.temperature = settings.openai_llm_temperature
        self.max_tokens = settings.openai_llm_max_tokens
    
    def generate_answer(
        self,
        question: str,
        evidence: List[Dict[str, Any]],
        person_name: str
    ) -> str:
        """
        Generate answer from question and retrieved evidence.
        
        Args:
            question: User's natural language question
            evidence: List of evidence chunks from vector search
            person_name: Name of the person being queried
            
        Returns:
            LLM-generated answer grounded in evidence
        """
        # Build context from evidence
        context_parts = []
        for idx, item in enumerate(evidence, 1):
            payload = item.get("payload", {})
            text = payload.get("text", "")
            source = payload.get("source", "unknown")
            date = payload.get("date", "unknown date")
            patient_id = payload.get("patient_id", "unknown")
            
            context_parts.append(
                f"[Evidence {idx}] (patient_id: {patient_id}, source: {source}, date: {date})\n{text}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Build system prompt with guardrails
        system_prompt = f"""You are a helpful assistant that answers questions about patient health data.

CRITICAL RULES:
1. Answer STRICTLY based on the provided evidence context below
2. If the evidence doesn't contain sufficient information to answer the question, say "I don't have that data for {person_name} in the given time range."
3. ALWAYS include patient_id when present in the evidence (shown as "patient_id:" in each evidence item)
4. ALWAYS include dates and specific values with units when present in the evidence
5. Be concise and precise
6. If evidence shows conflicting data, acknowledge it
7. Never make up information not present in the evidence
8. IMPORTANT: Look for phrases like "No meals logged", "No data", "not recorded" - these indicate absence of data

FORMATTING INSTRUCTIONS:
- When listing patients, ALWAYS include their **patient_id** (the UUID shown in evidence)
- When listing names, extract them from the profile text (e.g., "Profile for John Doe" → name is "John Doe")
- Use **bold** for important items (e.g., **Patient ID**, **Name**, **Item Name**)
- Use numbered lists (1. 2. 3.) for multiple items or patients
- Add a line break between each list item
- Use sub-bullets with "- " for details under each item
- Structure your answer clearly with proper spacing

EVIDENCE CONTEXT:
{context}

Answer the user's question based on this evidence."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content.strip()
            
            logger.info(
                "Generated LLM answer",
                question_length=len(question),
                evidence_count=len(evidence),
                answer_length=len(answer)
            )
            
            return answer
        
        except Exception as e:
            logger.error("LLM answer generation failed", error=str(e))
            return f"Error generating answer: {str(e)}"

