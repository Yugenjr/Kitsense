from __future__ import annotations

from typing import Any, Dict, Set

import re

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from kit_repository import KitNotFoundError, get_kit_by_id, get_kit_by_identifier
from ml_layer import age_tuned_tone, classify_stage


class SessionStartRequest(BaseModel):
    identifier: str = Field(..., description="Order ID or kit ID")


class ChatRequest(BaseModel):
    identifier: str
    message: str


app = FastAPI(title="Brand X Unified Chatbot API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _extract_stage_names(kit: Dict[str, Any]) -> list[str]:
    return [stage["stage_name"] for stage in kit["stages"]]


def _normalize_tokens(text: str) -> Set[str]:
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def _kit_context_keywords(kit: Dict[str, Any]) -> Set[str]:
    tokens: Set[str] = set()
    tokens |= _normalize_tokens(kit["kit_name"])
    for stage in kit["stages"]:
        tokens |= _normalize_tokens(stage["stage_name"])
        tokens |= _normalize_tokens(stage["technical_content"])
        tokens |= _normalize_tokens(stage["story_explanation"])
    return {token for token in tokens if len(token) > 2}


def _is_kit_context_message(message: str, kit: Dict[str, Any]) -> bool:
    msg_tokens = _normalize_tokens(message)
    if not msg_tokens:
        return False
    return bool(msg_tokens & _kit_context_keywords(kit))


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
            "get_kit_by_id": "backend.kit_repository.get_kit_by_id(kit_id)",
        },
        "policy": "Responses are restricted to the learner's identified robotics kit context.",
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/kits/{kit_id}")
def read_kit(kit_id: str) -> Dict[str, Any]:
    try:
        return get_kit_by_id(kit_id)
    except KitNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/session/start")
def start_session(req: SessionStartRequest) -> Dict[str, Any]:
    kit = get_kit_by_identifier(req.identifier)
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found for provided order/kit ID")

    return {
        "kit_id": kit["kit_id"],
        "kit_name": kit["kit_name"],
        "age_group": kit["age_group"],
        "difficulty": kit["difficulty"],
        "next_questions": [
            "Do you need help with mechanical assembly?",
            "Are you working on wiring or calibration?",
            "Would you like a story-based explanation first?",
        ],
    }


@app.post("/api/chat")
def chat(req: ChatRequest) -> Dict[str, Any]:
    kit = get_kit_by_identifier(req.identifier)
    if not kit:
        raise HTTPException(status_code=404, detail="Unknown identifier")

    if not _is_kit_context_message(req.message, kit):
        return {
            "kit": {"id": kit["kit_id"], "name": kit["kit_name"]},
            "out_of_scope": True,
            "response": (
                f"I can only help with the '{kit['kit_name']}' kit. "
                "Please ask about assembly, wiring, testing, or troubleshooting for this kit."
            ),
            "suggested_questions": [
                "How do I complete the mechanical assembly stage?",
                "How should I wire sensors and motor drivers safely?",
                "Can you explain this step with a simple story?",
            ],
        }

    available_stages = _extract_stage_names(kit)
    prediction = classify_stage(req.message, available_stages)
    matched_stage = next((s for s in kit["stages"] if s["stage_name"] == prediction.stage), kit["stages"][0])

    guidance = (
        f"For {matched_stage['stage_name']}: {matched_stage['technical_content']} "
        f"Story: {matched_stage['story_explanation']}"
    )

    return {
        "kit": {"id": kit["kit_id"], "name": kit["kit_name"]},
        "out_of_scope": False,
        "predicted_stage": prediction.stage,
        "confidence": prediction.confidence,
        "reasoning": prediction.reasoning,
        "tone_policy": age_tuned_tone(kit["age_group"]),
        "response": guidance,
    }
