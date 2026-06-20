from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.schemas import DiversionAlert
from app.modules.diversion.reconciliation import compute_reconciliation

router = APIRouter()


@router.get("/alerts", response_model=List[DiversionAlert])
def diversion_alerts(
    facility_id: Optional[str] = Query(None, description="Filter by facility"),
    window_days: int = Query(30, ge=1, le=365, description="Reconciliation window in days"),
    db: Session = Depends(get_db),
):
    """Return diversion alerts from supply reconciliation."""
    return compute_reconciliation(db, facility_id=facility_id, window_days=window_days)


@router.get("/alerts/critical", response_model=List[DiversionAlert])
def critical_diversion_alerts(db: Session = Depends(get_db)):
    """Return only critical and alert-level diversion flags."""
    all_alerts = compute_reconciliation(db)
    return [a for a in all_alerts if a.alert_level in ("critical", "alert")]
