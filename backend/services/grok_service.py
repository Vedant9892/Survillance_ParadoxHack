"""Grok AI service — sends frames to xAI Grok for threat analysis."""

import base64
import httpx

from backend.config.settings import settings


async def analyze_frame_with_grok(image_b64: str, incident_description: str) -> str:
    """
    Send a frame (base64) + incident context to Grok vision model.
    Returns the threat analysis text.
    """
    if not settings.GROK_API_KEY:
        return (
            "[Grok API key not configured] "
            f"Simulated analysis: The frame shows a potential threat — {incident_description}. "
            "Recommend immediate review by security personnel."
        )

    headers = {
        "Authorization": f"Bearer {settings.GROK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.GROK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert security threat analyst AI. "
                    "Analyze the provided surveillance frame and incident context. "
                    "Return a concise threat assessment report covering: "
                    "1) What you observe, 2) Threat level (low/medium/high/critical), "
                    "3) Recommended actions."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}",
                        },
                    },
                    {
                        "type": "text",
                        "text": f"Incident detected: {incident_description}. Analyze this frame for threats.",
                    },
                ],
            },
        ],
        "max_tokens": 512,
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(settings.GROK_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
