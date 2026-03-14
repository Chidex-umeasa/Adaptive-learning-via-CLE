from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc)
from uuid import uuid4
from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String, ForeignKey("users.id"), nullable=True)

    consent_telemetry: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    consent_webcam: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="sessions")
    events = relationship("Event", back_populates="session", cascade="all, delete-orphan")
    webcam = relationship("WebcamFeature", back_populates="session", cascade="all, delete-orphan")
    labels = relationship("EffortLabel", back_populates="session", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="session", cascade="all, delete-orphan")
    experiment_assignment = relationship("ExperimentAssignment", back_populates="session", uselist=False)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    ts_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    session = relationship("Session", back_populates="events")

Index("ix_events_session_ts", Event.session_id, Event.ts_ms)


class WebcamFeature(Base):
    __tablename__ = "webcam_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    ts_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    face_present: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gaze_on_screen: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gaze_dispersion: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    blink_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    head_motion: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
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


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    problem_id: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tests_passed: Mapped[int] = mapped_column(Integer, default=0)
    tests_total: Mapped[int] = mapped_column(Integer, default=0)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    session = relationship("Session", back_populates="submissions")

Index("ix_submissions_session", Submission.session_id)


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    assignments = relationship("ExperimentAssignment", back_populates="experiment")


class ExperimentAssignment(Base):
    __tablename__ = "experiment_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)
    experiment_id: Mapped[str] = mapped_column(String, ForeignKey("experiments.id"), nullable=False)
    variant: Mapped[str] = mapped_column(String, nullable=False)

    session = relationship("Session", back_populates="experiment_assignment")
    experiment = relationship("Experiment", back_populates="assignments")

Index("ix_assignment_session", ExperimentAssignment.session_id)
