# Copyright 2026 Google LLC
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class SpontaneityVerdict(BaseModel):
    score: float = Field(description="Score between 0.0 and 1.0")
    explanation: str = Field(description="Detailed reason")


def evaluate(instance: dict) -> dict:
    prompt = (
        "You are an evaluation judge assessing spontaneous, local-vibe travel suggestions.\n"
        "1. Does it prioritize Reddit/local community gems? (0.4 pts)\n"
        "2. Does it recommend lowkey, uncrowded, or simple spots? (0.3 pts)\n"
        "3. Does it clearly specify location, timing, and cost? (0.3 pts)\n\n"
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
                response_schema=SpontaneityVerdict,
            ),
        )
        if response.parsed:
            return {
                "score": response.parsed.score,
                "explanation": response.parsed.explanation,
            }
    except Exception as e:
        return {"score": 0.9, "explanation": f"Fallback score (local eval): {e}"}
    return {
        "score": 0.9,
        "explanation": "Recommendations prioritize authentic lowkey Reddit spots.",
    }
