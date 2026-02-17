# System Architecture

## Overview

The Adaptive Load Tutor is a web-based CS tutoring system that estimates learner cognitive load in real-time and adapts instruction accordingly. The system follows a three-tier architecture: browser client, API server, and data storage.

## Components

### Frontend (Next.js 14 + TypeScript)

| Component | Purpose |
|-----------|---------|
| `Tutor.tsx` | Main orchestrator — two-column layout, session management, telemetry lifecycle |
| `CodeEditor.tsx` | Code editing with real keystroke metrics (chars, deletes, pause timing) |
| `LoadGauge.tsx` | SVG semi-circular gauge with animated load visualization |
| `ProblemDescription.tsx` | Renders problem title, description, difficulty, test cases, concepts |
| `ProblemSidebar.tsx` | Problem list with solved/unsolved indicators |
| `HintPanel.tsx` | Progressive hint reveal with telemetry logging |
| `WebcamFeatures.tsx` | Camera permission, FaceMeshProcessor lifecycle, privacy indicator |
| `AuthModal.tsx` | Login/register with JWT token management |
| `Navbar.tsx` | Navigation with user info and dashboard link |
| `Telemetry.ts` | Event buffer with configurable flush interval and retry logic |
| `FaceMeshProcessor.ts` | Webcam processing: EAR blink detection, gaze tracking, head motion |

### Backend (FastAPI + SQLAlchemy)

| Module | Purpose |
|--------|---------|
| `main.py` | FastAPI app, CORS, router registration, core endpoints |
| `auth.py` | JWT creation/verification, bcrypt password hashing, auth dependencies |
| `features.py` | 10-second window aggregation, heuristic load scoring |
| `ml_inference.py` | joblib model loading, ML prediction with heuristic fallback |
| `problems.py` | Problem bank (17 problems, 5 difficulty tiers, 5 categories) |
| `sequencer.py` | Adaptive problem selection based on load + history, JS code evaluation |
| `ab_testing.py` | Hash-based A/B variant assignment for research experiments |
| `models.py` | SQLAlchemy ORM: User, Session, Event, WebcamFeature, EffortLabel, Submission, Experiment |
| `routers/` | auth, problems, experiments, analytics endpoints |

### ML Pipeline (Offline)

| Script | Purpose |
|--------|---------|
| `generate_synthetic_data.py` | Bootstrap training data with correlated feature distributions |
| `export_training_data.py` | Extract aligned features from database for training |
| `train.py` | 5-fold CV with GBR/RF/Ridge, model selection, artifact export |

## API Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/health` | No | Health check |
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Get JWT token |
| GET | `/auth/me` | Yes | Get current user |
| POST | `/sessions` | Optional | Create/update session |
| POST | `/events/batch` | No | Ingest telemetry events |
| POST | `/webcam/batch` | No | Ingest webcam features |
| POST | `/labels/effort` | No | Record effort rating |
| GET | `/load/{session_id}` | No | Get load estimate |
| GET | `/problems` | No | List all problems |
| GET | `/problems/{id}` | No | Get problem detail |
| GET | `/problems/next/{session_id}` | No | Get adaptive next problem |
| POST | `/problems/submit` | No | Submit solution |
| POST | `/experiments` | No | Create experiment |
| GET | `/experiments/{id}/results` | No | Get experiment results |
| GET | `/analytics/sessions` | No | List session summaries |
| GET | `/analytics/aggregate` | No | Global statistics |
| GET | `/analytics/export/csv` | No | Export data as CSV |

## Privacy Architecture

1. **No raw video storage**: The `<video>` element is hidden. FaceMeshProcessor runs entirely in-browser.
2. **Feature-only transmission**: Only 6 numeric values per 2-second window cross the network.
3. **Explicit consent**: Webcam features require opt-in. Telemetry consent defaults to true but is surfaced.
4. **Session isolation**: UUIDs prevent session correlation without authentication.
5. **Data export**: CSV export for research use includes only aggregated features and labels.

## Deployment

```
docker compose up    # Starts PostgreSQL + FastAPI + Next.js
```

Development:
```
cd backend && uvicorn app.main:app --reload    # Port 8000
cd frontend && npm run dev                      # Port 3000
```
