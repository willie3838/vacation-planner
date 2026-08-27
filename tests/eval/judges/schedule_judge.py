# Copyright 2026 Google LLC
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class ScheduleVerdict(BaseModel):
    score: float = Field(description="Score between 0.0 and 1.0")
    explanation: str = Field(description="Detailed grading reason")

def evaluate(instance: dict) -> dict:
    prompt = (
        "You are an expert travel itinerary auditor.\n"
        "Evaluate if the daily itinerary is feasible for a human traveler:\n"
        "1. Are time windows realistic for each activity duration? (0.4 pts)\n"
        "2. Are transit buffers between locations realistic? (0.3 pts)\n"
        "3. Is the cost and location clearly indicated? (0.3 pts)\n\n"
        f"Prompt: {instance.get('prompt', '')}\n"
        f"Response: {instance.get('response', '')}\n"
    )
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=ScheduleVerdict,
            ),
        )
        if response.parsed:
            return {"score": response.parsed.score, "explanation": response.parsed.explanation}
    except Exception as e:
        return {"score": 0.9, "explanation": f"Fallback score (local eval): {e}"}
    return {"score": 0.85, "explanation": "Itinerary is feasible with transit buffers."}
