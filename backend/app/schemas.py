from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class SessionCreate(BaseModel):
    session_id: str
    consent_telemetry: bool = True
    consent_webcam: bool = False

class SessionOut(BaseModel):
    session_id: str

class EventIn(BaseModel):
    ts_ms: int
    name: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class EventsBatchIn(BaseModel):
    session_id: str
    events: List[EventIn]

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

class EffortLabelIn(BaseModel):
    session_id: str
    ts_ms: int
    rating_1_7: int

class LoadEstimateOut(BaseModel):
    load_score: float  # 0..1
    label: str         # LOW/MED/HIGH
    confidence: float  # 0..1
    recommended_action: Optional[str] = None
