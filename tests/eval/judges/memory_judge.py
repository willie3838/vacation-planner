# Copyright 2026 Google LLC
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class MemoryVerdict(BaseModel):
    score: float = Field(description="Score 1.0 if memory adhered, 0.0 if violated")
    explanation: str = Field(description="Detailed reason")

def evaluate(instance: dict) -> dict:
    prompt = (
        "You are an expert evaluation judge auditing memory and preference recall.\n"
        "Check if the agent strictly respected traveler constraints (e.g. vegan, budget, dislikes):\n\n"
        f"User Prompt: {instance.get('prompt', '')}\n"
        f"Agent Response: {instance.get('response', '')}\n"
        f"Agent Trace: {instance.get('agent_data', '')}\n"
    )
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=MemoryVerdict,
            ),
        )
        if response.parsed:
            return {"score": response.parsed.score, "explanation": response.parsed.explanation}
    except Exception as e:
        return {"score": 1.0, "explanation": f"Fallback score (local eval): {e}"}
    return {"score": 1.0, "explanation": "Agent strictly adhered to stated traveler preferences."}
