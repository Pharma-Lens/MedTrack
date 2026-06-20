from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.schemas import StockoutRisk
from app.modules.availability.forecasting import get_stockout_risks

router = APIRouter()


@router.get("/risks", response_model=List[StockoutRisk])
def stockout_risks(
    facility_id: Optional[str] = Query(None, description="Filter by facility"),
    db: Session = Depends(get_db),
):
    """Return stockout risk assessments for all monitored medicines."""
    return get_stockout_risks(db, facility_id=facility_id)


@router.get("/risks/critical", response_model=List[StockoutRisk])
def critical_risks(db: Session = Depends(get_db)):
    """Return only critical and high stockout risks."""
    all_risks = get_stockout_risks(db)
    return [r for r in all_risks if r.risk_level in ("critical", "high")]
