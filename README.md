# Adaptive Learning via Cognitive Load Estimation

An AI-driven, web-based Computer Science tutoring system that **estimates learners’ cognitive load in real time** using interaction telemetry and privacy-preserving webcam features, and **adapts instruction dynamically** to optimize learning outcomes.

This project is part of a broader **AI + Education + Systems research portfolio**, focusing on intelligent tutoring systems, human-centered AI, and adaptive learning infrastructure.

---

## 🚀 Motivation

Learners often struggle not because content is too difficult, but because **cognitive load is poorly managed**. Traditional online learning systems are static: they do not respond to frustration, overload, or disengagement in real time.

This project explores:

- How **cognitive load can be inferred** from behavioral and visual signals
- How **adaptive systems** can respond dynamically to learner state
- How to design **privacy-aware, scalable learning infrastructure**

---

## 🧠 Core Research Questions

1. Can cognitive load be reliably estimated using **software-only telemetry** and **on-device webcam features**?
2. Which signals (errors, pauses, gaze stability, head motion) correlate most with mental effort?
3. Does **load-aware adaptation** improve learning efficiency, retention, or user experience?
4. How can personalization be achieved with minimal labeled data?

---

## 🏗️ System Architecture

**Frontend (Next.js / React)**
- Interactive CS tutoring interface
- Code editor with real-time telemetry logging
- Webcam-based feature extraction (on-device, no video storage)
- Live “Cognitive Load Meter”

**Backend (FastAPI / Python)**
- Event-sourced telemetry ingestion
- Webcam feature ingestion
- Time-windowed feature aggregation
- Cognitive load estimation service
- Adaptive decision engine

**Storage**
- SQLite (MVP) / PostgreSQL (production-ready)
- Event, feature, label, and session tables

---

## 📊 Cognitive Load Estimation

### Input Signals

**Interaction Telemetry**
- Compile/runtime errors
- Wrong vs correct attempts
- Hint usage frequency
- Typing pauses and corrections
- Action density and retries

**Webcam-Derived Features (Privacy-Preserving)**
- Face presence ratio
- Head motion variability
- Blink rate (proxy for fatigue/effort)
- Gaze stability (optional extension)

> ⚠️ No raw video or images are stored. All processing happens client-side.

---

## 🔄 Adaptive Learning Loop

1. Learner interacts with CS problem
2. Telemetry + webcam features are collected
3. Cognitive load is estimated in real time
4. System adapts instruction by:
   - Adjusting difficulty
   - Offering hints or worked examples
   - Decomposing tasks
   - Modifying pacing

---

## 🧪 Evaluation Plan

**Model Evaluation**
- Correlation with self-reported effort (1–7 scale)
- Classification accuracy for High / Medium / Low load
- Confidence calibration

**Learning Evaluation**
- A/B testing: adaptive vs static tutor
- Time-to-correct
- Retention performance
- Dropout and frustration rates

---

## 🧰 Tech Stack

**Frontend**
- Next.js (React, TypeScript)
- Monaco / CodeMirror (editor)
- MediaPipe Face Mesh (webcam features)

**Backend**
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

**ML / Data**
- Python (scikit-learn, pandas)
- Windowed feature aggregation
- Rule-based baseline → ML models → contextual bandits (planned)

---

## 📁 Repository Structure

adaptive-load-tutor/
├── backend/
│ ├── app/
│ │ ├── main.py # FastAPI app
│ │ ├── db.py # DB config
│ │ ├── models.py # ORM models
│ │ ├── schemas.py # API schemas
│ │ ├── features.py # Load estimation logic
│ │ └── settings.py
│ └── requirements.txt
│
├── frontend/
│ ├── src/
│ │ ├── app/
│ │ ├── components/
│ │ └── lib/
│ └── package.json
│
└── README.md


---

## ⚙️ Running the Project (MVP)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

Frontend
cd frontend
npm install
npm run dev
Open: http://localhost:3000

🔒 Ethics & Privacy
Explicit consent required for webcam features
No raw video or biometric data stored
Features are numeric, aggregated, and anonymized
Designed for IRB-compatible research deployment

🛣️ Roadmap
 Replace heuristic load model with ML estimator
 Personalized load calibration per learner
 Contextual bandit / RL-based adaptation policy
 Gaze estimation with calibration
 Retention-based learning evaluation
 Research paper / poster submission

🎓 Research Context
This project aligns with work in:
Intelligent Tutoring Systems (ITS)
Human-Computer Interaction (HCI)
Learning Sciences
Adaptive Systems
AI for Education

👤 Author
Alex Chidera Umeasalugo
Undergraduate Computer Science Researcher
Interests: AI for Education, Distributed Systems, Human-Centered AI

This project is still in progress
