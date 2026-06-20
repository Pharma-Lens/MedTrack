"""
app/modules/quality/anomaly_model.py
Isolation Forest anomaly detector for quality event patterns.

Current state: scaffold with feature extraction and model interface.
Training requires labelled historical data (connect NDA Uganda or WHO GTIN feed).

Next steps:
  1. Collect labelled events (pass/fail/suspect) from pilot facilities
  2. Run train() to fit and persist the model
  3. Swap heuristic checks in verification.py for model predictions
"""
from __future__ import annotations
import os
import pickle
import numpy as np
from typing import Optional
from app.core.logging import logger

MODEL_PATH = os.getenv("QUALITY_MODEL_PATH", "models/quality_isolation_forest.pkl")


def extract_features(event_dict: dict) -> np.ndarray:
    """
    Convert a stock event dict into a feature vector for the anomaly model.

    Features (expand as labelled data grows):
      0 - has_batch_number: 1 if batch_number present, else 0
      1 - quantity: raw quantity value
      2 - event_type_encoded: received=0, dispensed=1, other=2
      3 - has_quality_notes: 1 if quality_notes present, else 0
      4 - note_length: character length of quality_notes (0 if absent)
    """
    type_map = {"received": 0, "dispensed": 1}
    return np.array([[
        1 if event_dict.get("batch_number") else 0,
        float(event_dict.get("quantity", 0)),
        type_map.get(event_dict.get("event_type", ""), 2),
        1 if event_dict.get("quality_notes") else 0,
        len(event_dict.get("quality_notes") or ""),
    ]])


def load_model():
    """Load a persisted Isolation Forest model if one exists."""
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        logger.warning(f"Could not load quality model: {e}")
        return None


def train(events: list[dict], contamination: float = 0.05) -> None:
    """
    Fit Isolation Forest on historical event dicts and persist.
    contamination = expected fraction of anomalous events (tune per facility).
    """
    try:
        from sklearn.ensemble import IsolationForest
    except ImportError:
        logger.error("scikit-learn not installed. Run: pip install scikit-learn")
        return

    X = np.vstack([extract_features(e) for e in events])
    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    model.fit(X)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"Quality model trained on {len(events)} events, saved to {MODEL_PATH}")


def predict_anomaly(event_dict: dict) -> Optional[float]:
    """
    Returns anomaly score in [0, 1] where higher = more suspicious.
    Returns None if no model is loaded yet.
    """
    model = load_model()
    if model is None:
        return None
    X = extract_features(event_dict)
    # Isolation Forest scores: negative = anomaly, positive = normal
    raw_score = model.decision_function(X)[0]
    # Normalise to [0, 1] where 1 = most anomalous
    normalised = float(1 - (raw_score + 0.5))
    return max(0.0, min(1.0, normalised))
