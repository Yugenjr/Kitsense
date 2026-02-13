"""ML-ish personalization layer for stage-aware tutoring.

This module intentionally keeps the model lightweight so the prototype can run
without external dependencies. In production, replace with an embedding-based
retriever + intent classifier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class StagePrediction:
    stage: str
    confidence: float
    reasoning: str


STAGE_KEYWORDS: Dict[str, List[str]] = {
    "Body Making": ["body", "chassis", "frame", "assemble", "parts", "mechanical"],
    "Circuit Building": ["circuit", "wire", "sensor", "board", "battery", "connection"],
    "Frame Assembly": ["frame", "wheel", "mount", "caster", "chassis"],
    "Sensor Logic": ["ultrasonic", "distance", "logic", "code", "detect", "sensor"],
}


def classify_stage(user_message: str, available_stages: List[str]) -> StagePrediction:
    """Map user message to the most likely kit stage.

    This simple keyword model is the placeholder ML layer.
    """
    text = user_message.lower()
    best_stage = available_stages[0] if available_stages else "General Guidance"
    best_score = 0

    for stage in available_stages:
        keywords = STAGE_KEYWORDS.get(stage, [stage.lower()])
        score = sum(1 for token in keywords if token in text)
        if score > best_score:
            best_score = score
            best_stage = stage

    confidence = min(0.95, 0.35 + (best_score * 0.2)) if best_score else 0.3
    reasoning = (
        f"Detected {best_score} stage keywords; routing learner to '{best_stage}'."
        if best_score
        else "No explicit stage keywords detected; using first stage as default learning path."
    )
    return StagePrediction(stage=best_stage, confidence=confidence, reasoning=reasoning)


def age_tuned_tone(age_group: str) -> str:
    if age_group in {"10-14", "8-12"}:
        return "Use short, playful sentences with vivid analogies."
    if age_group in {"12-16", "14-18"}:
        return "Use encouraging maker language with quick technical explanations."
    return "Use clear and supportive educational language."
