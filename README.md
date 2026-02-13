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
  - “Coding” aesthetic via `Fira Code` + `Space Grotesk`
  - Can be embedded across web dashboards / portals

- **Backend (`backend/app.py`)**
  - FastAPI REST endpoints
  - `/api/session/start` for identity and kit resolution
  - `/api/chat` for stage-aware responses

- **Data Layer (`backend/kits_data.json`)**
  - Maps order IDs and kit IDs to kit content
  - Stores stages, explanations, and story cards

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
- Predicted stage
- Confidence + reasoning
- Age-tuned tone policy
- Story-card-based guidance

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

## 6) Why this is platform-agnostic

- Backend is exposed as clean REST APIs.
- Frontend is isolated and can be wrapped as a widget/SDK snippet.
- Kit context is externalized in data + ML routing logic, not hardcoded per platform.

