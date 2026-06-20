"""Supply availability / stockout forecasting module."""
from sqlalchemy.orm import Session
from app.models.stock_event import StockEvent


def forecast_stockout_risk(db: Session, facility_id: str, drug_id: str) -> dict:
    """Estimate stockout risk for a facility/drug pair from stock_events history.

    TODO: replace placeholder logic with a real forecasting model
    (e.g. consumption rate vs. on-hand stock, seasonality).
    """
    events = (
        db.query(StockEvent)
        .filter(StockEvent.facility_id == facility_id, StockEvent.drug_id == drug_id)
        .all()
    )
    return {
        "facility_id": facility_id,
        "drug_id": drug_id,
        "event_count": len(events),
        "risk": "unknown",
    }
