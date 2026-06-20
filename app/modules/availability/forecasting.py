"""
Availability & Forecasting Module
----------------------------------
Predicts stockout risk from supply-chain event history.

Current approach: consumption rate from recent dispensing events + stock on hand.
Next iteration: time-series ML (Prophet or LSTM) on facility-level consumption.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.stock_event import StockEvent, EventType
from app.models.schemas import StockoutRisk
from typing import List
from datetime import datetime, timedelta


RISK_THRESHOLDS = {
    "critical": 7,    # days
    "high": 14,
    "medium": 30,
}


def get_stockout_risks(db: Session, facility_id: str = None) -> List[StockoutRisk]:
    """
    For each medicine at each facility, compute days of stock remaining
    based on recent consumption rate and current stock on hand.
    """
    query = db.query(StockEvent)
    if facility_id:
        query = query.filter(StockEvent.facility_id == facility_id)

    # Get latest stock-on-hand per facility+medicine
    latest_subq = (
        db.query(
            StockEvent.facility_id,
            StockEvent.medicine_id,
            func.max(StockEvent.created_at).label("max_ts"),
        )
        .filter(StockEvent.stock_on_hand_after.isnot(None))
        .group_by(StockEvent.facility_id, StockEvent.medicine_id)
        .subquery()
    )

    latest_events = (
        db.query(StockEvent)
        .join(
            latest_subq,
            (StockEvent.facility_id == latest_subq.c.facility_id)
            & (StockEvent.medicine_id == latest_subq.c.medicine_id)
            & (StockEvent.created_at == latest_subq.c.max_ts),
        )
        .all()
    )

    risks = []
    cutoff = datetime.utcnow() - timedelta(days=30)

    for event in latest_events:
        stock = event.stock_on_hand_after or 0
        reorder = event.reorder_level or 0

        # Compute avg daily consumption from last 30 days
        dispensed = (
            db.query(func.sum(StockEvent.quantity))
            .filter(
                StockEvent.facility_id == event.facility_id,
                StockEvent.medicine_id == event.medicine_id,
                StockEvent.event_type == EventType.DISPENSED,
                StockEvent.created_at >= cutoff,
            )
            .scalar()
            or 0
        )
        daily_rate = dispensed / 30 if dispensed > 0 else None
        days_remaining = (stock / daily_rate) if daily_rate else None

        if days_remaining is None:
            risk_level = "unknown"
            recommendation = "No dispensing data in last 30 days. Verify stock manually."
        elif days_remaining <= RISK_THRESHOLDS["critical"]:
            risk_level = "critical"
            recommendation = f"Stock critically low. Emergency reorder needed within {int(days_remaining)} days."
        elif days_remaining <= RISK_THRESHOLDS["high"]:
            risk_level = "high"
            recommendation = f"Reorder immediately. Approx {int(days_remaining)} days remaining."
        elif days_remaining <= RISK_THRESHOLDS["medium"]:
            risk_level = "medium"
            recommendation = f"Plan reorder. Approx {int(days_remaining)} days remaining."
        else:
            risk_level = "low"
            recommendation = f"Stock adequate. Approx {int(days_remaining)} days remaining."

        risks.append(StockoutRisk(
            facility_id=event.facility_id,
            medicine_id=event.medicine_id,
            medicine_name=event.medicine_name,
            stock_on_hand=stock,
            reorder_level=reorder,
            days_of_stock_remaining=days_remaining,
            risk_level=risk_level,
            recommendation=recommendation,
        ))

    return risks