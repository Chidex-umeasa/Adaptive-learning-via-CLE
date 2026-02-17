import hashlib
from enum import Enum


class ExperimentVariant(str, Enum):
    CONTROL = "control"
    HEURISTIC = "heuristic"
    ML_MODEL = "ml_model"
    FULL_ADAPTIVE = "full_adaptive"


class ABEngine:
    def __init__(self, config: dict):
        self.weights = config.get("weights", {
            "control": 25,
            "heuristic": 25,
            "ml_model": 25,
            "full_adaptive": 25,
        })

    def assign_variant(self, session_id: str) -> str:
        h = int(hashlib.sha256(session_id.encode()).hexdigest(), 16)
        bucket = h % 100
        cumulative = 0
        for variant, weight in self.weights.items():
            cumulative += weight
            if bucket < cumulative:
                return variant
        return "control"

    @staticmethod
    def should_adapt(variant: str) -> bool:
        return variant in ("heuristic", "ml_model", "full_adaptive")

    @staticmethod
    def should_use_ml(variant: str) -> bool:
        return variant in ("ml_model", "full_adaptive")

    @staticmethod
    def should_sequence(variant: str) -> bool:
        return variant == "full_adaptive"
