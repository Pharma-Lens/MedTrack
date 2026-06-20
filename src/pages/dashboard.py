from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.schemas import DashboardSummary
from app.models.stock_event import StockEvent, QualityFlag
from app.modules.availability.forecasting import get_stockout_risks
from app.modules.diversion.reconciliation import compute_reconciliation

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    """Single endpoint powering the MedTrack overview dashboard."""
    total_events = db.query(func.count(StockEvent.id)).scalar() or 0

    quality_failures = (
        db.query(func.count(StockEvent.id))
        .filter(StockEvent.quality_flag.in_([QualityFlag.FAIL, QualityFlag.SUSPECT]))
        .scalar()
        or 0
    )

    risks = get_stockout_risks(db)
    stockout_risks = sum(1 for r in risks if r.risk_level in ("critical", "high"))

    alerts = compute_reconciliation(db)
    diversion_alerts = sum(1 for a in alerts if a.alert_level in ("critical", "alert"))

    facilities = (
        db.query(func.count(func.distinct(StockEvent.facility_id))).scalar() or 0
    )
    medicines = (
        db.query(func.count(func.distinct(StockEvent.medicine_id))).scalar() or 0
    )

    return DashboardSummary(
        total_events=total_events,
        quality_failures=quality_failures,
        stockout_risks=stockout_risks,
        diversion_alerts=diversion_alerts,
        facilities_monitored=facilities,
        medicines_tracked=medicines,
    )
