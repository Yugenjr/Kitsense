from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml_layer import age_tuned_tone, classify_stage

DATA_PATH = Path(__file__).with_name("kits_data.json")


class SessionStartRequest(BaseModel):
    identifier: str = Field(..., description="Order ID or kit ID")


class ChatRequest(BaseModel):
    identifier: str
    message: str


app = FastAPI(title="Brand X Unified Chatbot API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_data() -> Dict[str, Any]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_kit(identifier: str) -> Optional[Dict[str, Any]]:
    payload = _load_data()
    token = identifier.strip().upper()
    for kit in payload.get("kits", []):
        if token == kit["kit_id"] or token in {oid.upper() for oid in kit.get("order_ids", [])}:
            return kit
    return None


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "name": "Brand X Unified Chatbot API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "start_session": "/api/session/start",
            "chat": "/api/chat",
        },
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/session/start")
def start_session(req: SessionStartRequest) -> Dict[str, Any]:
    kit = find_kit(req.identifier)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found for provided order/kit ID")

    return {
        "kit_id": kit["kit_id"],
        "kit_name": kit["kit_name"],
        "age_group": kit["age_group"],
        "difficulty": kit["difficulty"],
        "next_questions": [
            "Do you need help with body making?",
            "Are you assembling parts or building the circuit?",
            "Would you like a story-based explanation first?",
        ],
    }


@app.post("/api/chat")
def chat(req: ChatRequest) -> Dict[str, Any]:
    kit = find_kit(req.identifier)
    if not kit:
        raise HTTPException(status_code=404, detail="Unknown identifier")

    available_stages = [stage["name"] for stage in kit["stages"]]
    prediction = classify_stage(req.message, available_stages)
    matched_stage = next((s for s in kit["stages"] if s["name"] == prediction.stage), kit["stages"][0])

    guidance = (
        f"For {matched_stage['name']}: {matched_stage['content']} "
        f"Story card: {matched_stage['story_card']}"
    )

    return {
        "kit": {"id": kit["kit_id"], "name": kit["kit_name"]},
        "predicted_stage": prediction.stage,
        "confidence": prediction.confidence,
        "reasoning": prediction.reasoning,
        "tone_policy": age_tuned_tone(kit["age_group"]),
        "response": guidance,
    }
