from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import StockEventCreate, StockEventOut, QualityVerificationResult
from app.models.stock_event import StockEvent
from app.modules.quality.verification import verify_and_save

router = APIRouter()


@router.post("/events", response_model=StockEventOut, status_code=201)
def log_event(event: StockEventCreate, db: Session = Depends(get_db)):
    """Log a new stock event and auto-run quality verification."""
    db_event = StockEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    # Auto-verify on ingest
    verify_and_save(db, db_event.id)
    db.refresh(db_event)
    return db_event


@router.get("/verify/{event_id}", response_model=QualityVerificationResult)
def verify_event(event_id: int, db: Session = Depends(get_db)):
    """Run quality verification on an existing event."""
    result = verify_and_save(db, event_id)
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return result


@router.get("/failures")
def list_quality_failures(db: Session = Depends(get_db)):
    """Return all events flagged as FAIL or SUSPECT."""
    from app.models.stock_event import QualityFlag
    events = (
        db.query(StockEvent)
        .filter(StockEvent.quality_flag.in_([QualityFlag.FAIL, QualityFlag.SUSPECT]))
        .order_by(StockEvent.created_at.desc())
        .limit(100)
        .all()
    )
    return events
