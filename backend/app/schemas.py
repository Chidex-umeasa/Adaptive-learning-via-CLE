from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

# --- Auth ---

class UserRegister(BaseModel):
    email: str
    password: str
    display_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    display_name: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- Sessions ---

class SessionCreate(BaseModel):
    session_id: str
    consent_telemetry: bool = True
    consent_webcam: bool = False

class SessionOut(BaseModel):
    session_id: str

# --- Events ---

class EventIn(BaseModel):
    ts_ms: int
    name: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class EventsBatchIn(BaseModel):
    session_id: str
    events: List[EventIn]

# --- Webcam ---

class WebcamFeatureIn(BaseModel):
    ts_ms: int
    face_present: float = 0.0
    gaze_on_screen: float = 0.0
    gaze_dispersion: float = 0.0
    blink_rate: float = 0.0
    head_motion: float = 0.0
    away_events: int = 0

class WebcamBatchIn(BaseModel):
    session_id: str
    features: List[WebcamFeatureIn]

# --- Labels ---

class EffortLabelIn(BaseModel):
    session_id: str
    ts_ms: int
    rating_1_7: int

# --- Load ---

class LoadEstimateOut(BaseModel):
    load_score: float
    label: str
    confidence: float
    recommended_action: Optional[str] = None

# --- Problems ---

class HintOut(BaseModel):
    id: str
    text: str
    level: int

class TestCaseOut(BaseModel):
    input: List[Any]
    expected: Any

class ProblemOut(BaseModel):
    id: str
    title: str
    description: str
    difficulty: int
    category: str
    starter_code: str
    hints: List[HintOut] = []
    test_cases: List[TestCaseOut] = []
    concepts: List[str] = []

class ProblemListItem(BaseModel):
    id: str
    title: str
    difficulty: int
    category: str

class SubmissionIn(BaseModel):
    session_id: str
    problem_id: str
    code: str

class SubmissionOut(BaseModel):
    correct: bool
    tests_passed: int
    tests_total: int
    errors: List[str] = []
    next_problem_id: Optional[str] = None

# --- Experiments ---

class ExperimentCreate(BaseModel):
    name: str
    config: Dict[str, Any]

class ExperimentOut(BaseModel):
    id: str
    name: str
    config: Dict[str, Any]
    active: bool

class ExperimentResultsOut(BaseModel):
    experiment_id: str
    variants: Dict[str, Any]

# --- Analytics ---

class SessionSummary(BaseModel):
    session_id: str
    user_email: Optional[str] = None
    created_at: str
    event_count: int
    mean_load: Optional[float] = None
    problems_attempted: int
    problems_solved: int

class AggregateStats(BaseModel):
    total_sessions: int
    total_events: int
    total_users: int
    mean_load_score: Optional[float] = None
