"""Diversion / leakage detection module."""
from sqlalchemy.orm import Session
from app.models.stock_event import StockEvent


def reconcile_distribution(db: Session, facility_id: str, drug_id: str) -> dict:
    """Compare expected vs. recorded distribution volumes to flag diversion risk.

    TODO: replace placeholder logic with real reconciliation against
    expected delivery volumes (e.g. donor shipment manifests).
    """
    events = (
        db.query(StockEvent)
        .filter(StockEvent.facility_id == facility_id, StockEvent.drug_id == drug_id)
        .all()
    )
    received = sum(e.quantity for e in events if e.event_type == "received")
    dispensed = sum(e.quantity for e in events if e.event_type == "dispensed")
    unaccounted = received - dispensed
    return {
        "facility_id": facility_id,
        "drug_id": drug_id,
        "received": received,
        "dispensed": dispensed,
        "unaccounted": unaccounted,
        "flag": unaccounted > 0,
    }
