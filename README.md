# Platform-Agnostic AI Chatbot for Personalized Robotics Learning (Brand X)

This prototype delivers a **single unified chatbot platform** that personalizes support based on a learner's **order ID or kit ID** and dynamically injects kit-specific context.

## 1) Product Idea

### One Brain, Dynamic Context Injection
Instead of building one bot per kit, this architecture uses:

- **Single chatbot backend API**
- **Kit knowledge database**
- **ML stage-classification layer**
- **Embeddable professional frontend widget**

Flow:

1. Learner enters Order ID or Kit ID.
2. Backend resolves learner's kit.
3. Kit metadata + stage content + story cards are loaded.
4. Chat message is routed through the ML layer for stage prediction.
5. Response is generated with age-tuned guidance and concept storytelling.

## 2) System Architecture

- **Frontend (`frontend/`)**
  - Professional clean UI suitable for web portals and dashboards
  - “Coding” aesthetic via modern developer-friendly typography
  - Can be embedded across web dashboards / portals

- **Backend (`backend/app.py`)**
  - FastAPI REST endpoints
  - `/api/session/start` for identity and kit resolution
  - `/api/chat` for stage-aware responses
  - `/api/kits/{kit_id}` for exact case-insensitive kit retrieval
  - Strict out-of-scope protection so chatbot answers only in selected kit context

- **Data Layer (`backend/kits_data.json`)**
  - Stores 20 realistic mock kits in a `kits_by_id` dictionary for O(1)-style key lookup
  - Maps order IDs and kit IDs to stage content, technical explanations, and story narratives

- **ML Layer (`backend/ml_layer.py`)**
  - Lightweight stage classifier (keyword/intention-based baseline)
  - Confidence estimation + reasoning trace
  - Age-group tone policy
  - Designed for easy replacement with embeddings + vector retrieval

## 3) API Endpoints

### `POST /api/session/start`
Input:
```json
{ "identifier": "RX-101" }
```
Returns kit metadata + proactive questions:
- “Do you need help with body making?”
- “Are you assembling parts or building the circuit?”

### `POST /api/chat`
Input:
```json
{ "identifier": "RX-101", "message": "I need help wiring sensors" }
```
Returns:
- In-scope replies for kit stages (with story card and tone policy)
- Out-of-scope refusal when question is unrelated to robotics kit learning


### Repository function
`backend/kit_repository.py` includes:
- `get_kit_by_id(kit_id: str)`
  - exact match only (no partial matching)
  - case-insensitive
  - raises clear `"Kit not found"` error when missing

## 4) ML Layer Evolution Path (Production)

This prototype uses a deterministic baseline so it's easy to validate. To productionize:

1. Replace keyword classifier with a **small intent model** (e.g., MiniLM or DistilBERT fine-tune).
2. Add **vector store retrieval** (FAISS/Pinecone/pgvector) for kit manuals.
3. Add **response orchestrator**:
   - Stage predictor
   - Retrieval step
   - Guardrails + age adaptation
4. Add telemetry for:
   - stage prediction accuracy
   - learner completion rates
   - confusion hotspots

## 5) Run Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend
```bash
cd frontend
python -m http.server 4173
```
Then open `http://127.0.0.1:4173`.

Backend sanity URLs:
- `http://127.0.0.1:8000/` (API info)
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## 6) How to build this backend as a real chatbot

1. **Keep identity first**
   - Always require order ID/kit ID before chat.
   - Store `session_id -> kit_id` so each user is pinned to one kit context.
2. **Inject only kit context into prompts**
   - Build context from selected kit stages, story cards, and troubleshooting docs.
   - Never send unrelated knowledge chunks to the model.
3. **Add a strict relevance gate**
   - If query has no overlap with kit context or robotics intent, refuse and redirect.
   - Return suggested in-scope questions.
4. **Use a constrained system prompt with your LLM provider**
   - Example policy:
     - "Answer only from provided kit context."
     - "If context is missing, say you don't know and ask a kit-specific follow-up question."
     - "Do not answer general world-knowledge questions unrelated to the identified kit."
5. **Persist conversation state**
   - Save recent turns and current stage to improve guidance continuity.
6. **Production essentials**
   - API auth, rate limits, logging, moderation, and eval dashboards.

## 7) Why this is platform-agnostic

- Backend is exposed as clean REST APIs.
- Frontend is isolated and can be wrapped as a widget/SDK snippet.
- Kit context is externalized in data + ML routing logic, not hardcoded per platform.
