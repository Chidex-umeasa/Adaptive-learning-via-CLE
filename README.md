# Adaptive Learning via Cognitive Load Estimation

[![CI](https://github.com/yourusername/adaptive-load-tutor/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/adaptive-load-tutor/actions)

An AI-driven, web-based CS tutoring system that **estimates learners' cognitive load in real time** using interaction telemetry and privacy-preserving webcam features, then **adapts instruction dynamically** to optimize learning outcomes.

## Architecture

```mermaid
graph LR
    A[Browser] -->|Telemetry + Webcam| B[FastAPI]
    B -->|Store| C[(PostgreSQL)]
    B -->|Features| D[ML Model]
    D -->|Load Score| B
    B -->|Adaptive Response| A
    E[ML Pipeline] -->|Train| D
```

> See [docs/architecture.md](docs/architecture.md) for full system documentation and [docs/diagrams/](docs/diagrams/) for Mermaid source files.

## Features

- **Real-time cognitive load estimation** from 14 behavioral + visual signals
- **Adaptive problem sequencing** — difficulty adjusts based on estimated load
- **Privacy-first webcam processing** — Face Mesh runs in-browser, only 6 numeric features transmitted
- **17 CS problems** across 5 categories (basics, strings, arrays, recursion, data structures)
- **ML training pipeline** — GradientBoosting/RandomForest/Ridge with 5-fold CV
- **A/B testing framework** — deterministic hash-based variant assignment for research
- **Research dashboard** — load timelines, feature correlations, experiment comparisons
- **JWT authentication** with multi-user session tracking
- **Docker deployment** — one command startup with PostgreSQL

## Quick Start

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/yourusername/adaptive-load-tutor.git
cd adaptive-load-tutor
docker compose up
# Open http://localhost:3000
```

### Option 2: Local Development
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### ML Pipeline
```bash
cd ml
pip install -r requirements.txt
python generate_synthetic_data.py   # Generate training data
python train.py                      # Train + evaluate models
# Model saved to ml/artifacts/load_model.joblib
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic 2.x |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Database | SQLite (dev) / PostgreSQL 16 (prod) |
| ML | scikit-learn, pandas, numpy, joblib |
| Webcam | FaceMesh (in-browser), EAR blink detection |
| CI/CD | GitHub Actions, Docker Compose, pytest |
| Migrations | Alembic |

## Cognitive Load Signals

| Signal | Source | What It Measures |
|--------|--------|-----------------|
| Compile errors | Code evaluation | Syntax understanding |
| Wrong answers | Test runner | Conceptual gaps |
| Typing pauses | Keystroke timing | Hesitation / thinking |
| Delete ratio | Keystroke metrics | Uncertainty / backtracking |
| Hint requests | UI interaction | Help-seeking behavior |
| Face presence | Webcam | Attention / engagement |
| Gaze dispersion | Webcam | Visual search / confusion |
| Blink rate | Webcam (EAR) | Fatigue / cognitive effort |
| Head motion | Webcam | Restlessness / frustration |

## Project Structure

```
adaptive-load-tutor/
├── .github/workflows/ci.yml          # CI pipeline
├── docker-compose.yml                 # One-command deployment
├── backend/
│   ├── Dockerfile
│   ├── alembic/                       # Database migrations
│   ├── app/
│   │   ├── main.py                    # FastAPI app + routes
│   │   ├── auth.py                    # JWT authentication
│   │   ├── models.py                  # 8 ORM models
│   │   ├── features.py                # Load aggregation + heuristic
│   │   ├── ml_inference.py            # ML model loading + prediction
│   │   ├── problems.py                # 17-problem bank
│   │   ├── sequencer.py               # Adaptive problem selection
│   │   ├── ab_testing.py              # A/B experiment engine
│   │   └── routers/                   # auth, problems, analytics, experiments
│   └── tests/                         # pytest suite (10 test files)
├── frontend/
│   ├── Dockerfile
│   ├── src/
│   │   ├── components/
│   │   │   ├── Tutor.tsx              # Main two-column tutor UI
│   │   │   ├── CodeEditor.tsx         # Editor with keystroke metrics
│   │   │   ├── LoadGauge.tsx          # SVG cognitive load gauge
│   │   │   ├── WebcamFeatures.tsx     # Real webcam integration
│   │   │   ├── ProblemDescription.tsx # Problem display
│   │   │   ├── HintPanel.tsx          # Progressive hints
│   │   │   └── dashboard/            # Analytics components
│   │   ├── context/AuthContext.tsx     # Auth state management
│   │   └── lib/
│   │       ├── faceMeshProcessor.ts   # Webcam feature extraction
│   │       └── types.ts              # Shared TypeScript types
│   └── __tests__/                     # Jest test suite
├── ml/
│   ├── generate_synthetic_data.py     # Bootstrap training data
│   ├── export_training_data.py        # Extract from database
│   ├── train.py                       # Model training + evaluation
│   └── artifacts/                     # Saved models + reports
└── docs/
    ├── architecture.md                # System documentation
    ├── RESEARCH_PROTOCOL.md           # Study design + IRB considerations
    └── diagrams/                      # Mermaid architecture diagrams
```

## Research Design

This system supports formal A/B studies comparing adaptive vs. static tutoring. See [docs/RESEARCH_PROTOCOL.md](docs/RESEARCH_PROTOCOL.md) for:
- Between-subjects study design (Control / Heuristic / ML Model)
- Participant criteria and recruitment protocol
- Measures: learning gain, time-to-correct, completion rate, hint usage
- Statistical analysis plan (ANOVA, effect sizes, feature correlations)
- IRB considerations and privacy safeguards

## API Documentation

The API is fully documented via FastAPI's auto-generated OpenAPI docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See [docs/architecture.md](docs/architecture.md) for the complete endpoint reference.

## Ethics & Privacy

- **No raw video stored** — all webcam processing happens in-browser
- **Explicit consent** required for webcam features (opt-in toggle)
- **Feature-only transmission** — only 6 numeric values per 2-second window
- **Anonymized sessions** — random UUIDs, no PII in telemetry
- **Data minimization** — designed for IRB-compatible research deployment

## Running Tests

```bash
# Backend
cd backend
pip install -r requirements-dev.txt
pytest --cov=app -v

# Frontend
cd frontend
npm test
```

## Author

**Alex Chidera Umeasalugo**
Undergraduate Computer Science Researcher
Interests: AI for Education, Intelligent Tutoring Systems, Human-Centered AI, Distributed Systems

## License

This project is for academic and research purposes.
