"""
app/modules/availability/forecast_model.py
Time-series stockout forecasting model interface.

Current state: consumption-rate heuristic in forecasting.py works for pilot.
This module defines the interface for the next-iteration ML model.

Upgrade path:
  1. Accumulate 90+ days of dispensing data per facility+medicine
  2. Fit Prophet (or lightweight LSTM) per medicine track
  3. Replace days_remaining estimate in forecasting.py with model output
"""
from __future__ import annotations
import os
import pickle
from typing import Optional, List
from app.core.logging import logger

MODEL_DIR = os.getenv("FORECAST_MODEL_DIR", "models/forecasts/")


def _model_path(facility_id: str, medicine_id: str) -> str:
    safe = lambda s: s.replace("/", "_").replace(" ", "_")
    return os.path.join(MODEL_DIR, f"{safe(facility_id)}__{safe(medicine_id)}.pkl")


def train_prophet(
    facility_id: str,
    medicine_id: str,
    dates: List[str],          # ISO date strings
    quantities: List[float],   # daily dispensed quantities
) -> None:
    """
    Fit a Prophet model on daily consumption data and persist per facility+medicine.
    Requires: pip install prophet
    """
    try:
        from prophet import Prophet
        import pandas as pd
    except ImportError:
        logger.error("Prophet not installed. Run: pip install prophet")
        return

    df = pd.DataFrame({"ds": pd.to_datetime(dates), "y": quantities})
    model = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
    model.fit(df)

    os.makedirs(MODEL_DIR, exist_ok=True)
    path = _model_path(facility_id, medicine_id)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"Forecast model trained: {facility_id}/{medicine_id} → {path}")


def predict_days_remaining(
    facility_id: str,
    medicine_id: str,
    stock_on_hand: float,
    horizon_days: int = 60,
) -> Optional[float]:
    """
    Use a trained Prophet model to estimate days until stockout.
    Falls back to None if no model exists (caller uses heuristic).
    """
    path = _model_path(facility_id, medicine_id)
    if not os.path.exists(path):
        return None

    try:
        from prophet import Prophet
        import pandas as pd
        from datetime import date, timedelta
    except ImportError:
        return None

    with open(path, "rb") as f:
        model = pickle.load(f)

    future = model.make_future_dataframe(periods=horizon_days)
    forecast = model.predict(future)
    tail = forecast.tail(horizon_days)[["ds", "yhat"]].copy()
    tail["yhat"] = tail["yhat"].clip(lower=0)

    cumulative = 0.0
    for _, row in tail.iterrows():
        cumulative += row["yhat"]
        if cumulative >= stock_on_hand:
            days_out = (row["ds"].date() - date.today()).days
            return max(0, days_out)

    return float(horizon_days)  # stock lasts beyond forecast horizon
