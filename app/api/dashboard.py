"""Combined dashboard endpoint — pulls quality, availability, and diversion signals together."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.availability.forecasting import forecast_stockout_risk
from app.modules.diversion.reconciliation import reconcile_distribution

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{facility_id}/{drug_id}")
def get_dashboard(facility_id: str, drug_id: str, db: Session = Depends(get_db)):
    return {
        "facility_id": facility_id,
        "drug_id": drug_id,
        "availability": forecast_stockout_risk(db, facility_id, drug_id),
        "diversion": reconcile_distribution(db, facility_id, drug_id),
        # TODO: add quality verification once merged in
    }
