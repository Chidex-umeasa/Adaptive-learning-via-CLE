from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .db import Base

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # consent flags
    consent_telemetry: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    consent_webcam: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    events = relationship("Event", back_populates="session", cascade="all, delete-orphan")
    webcam = relationship("WebcamFeature", back_populates="session", cascade="all, delete-orphan")
    labels = relationship("EffortLabel", back_populates="session", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    ts_ms: Mapped[int] = mapped_column(Integer, nullable=False)  # client timestamp ms
    name: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    session = relationship("Session", back_populates="events")

Index("ix_events_session_ts", Event.session_id, Event.ts_ms)

class WebcamFeature(Base):
    __tablename__ = "webcam_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    ts_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    # aggregated features per small interval/window
    face_present: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)   # 0..1
    gaze_on_screen: Mapped[float] = mapped_column(Float, nullable=False, default=0.0) # 0..1 (optional)
    gaze_dispersion: Mapped[float] = mapped_column(Float, nullable=False, default=0.0) # >=0 (optional)
    blink_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)     # blinks/min (noisy)
    head_motion: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)    # variability proxy
    away_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    session = relationship("Session", back_populates="webcam")

Index("ix_webcam_session_ts", WebcamFeature.session_id, WebcamFeature.ts_ms)

class EffortLabel(Base):
    __tablename__ = "effort_labels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    ts_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    rating_1_7: Mapped[int] = mapped_column(Integer, nullable=False)

    session = relationship("Session", back_populates="labels")

Index("ix_labels_session_ts", EffortLabel.session_id, EffortLabel.ts_ms)
