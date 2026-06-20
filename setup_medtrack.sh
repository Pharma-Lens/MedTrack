#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "== MedTrack skeleton setup =="

# 1. Termux packages
pkg update -y && pkg upgrade -y
pkg install -y python git

# 2. Project root
mkdir -p ~/medtrack && cd ~/medtrack

# 3. Virtual environment
python -m venv venv
source venv/bin/activate

# 4. Python deps (kept minimal on purpose -- no pandas/numpy, avoids Termux compile pain)
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy pydantic python-multipart pytest
pip freeze > requirements.txt

# 5. Folder skeleton
mkdir -p app/core app/modules/quality app/modules/supply app/modules/diversion app/api tests data docs
touch app/__init__.py app/core/__init__.py app/modules/__init__.py \
      app/modules/quality/__init__.py app/modules/supply/__init__.py \
      app/modules/diversion/__init__.py app/api/__init__.py tests/__init__.py

# 6. .gitignore
cat > .gitignore << 'EOF'
venv/
__pycache__/
*.pyc
*.db
.env
EOF

# 7. README
cat > README.md << 'EOF'
# MedTrack

One platform, three modules, one dashboard:
- Quality Triage (existing verification logic -- merge into app/modules/quality/engine.py)
- Supply Visibility & Forecasting (app/modules/supply/forecasting.py)
- Diversion & Leakage Detection (app/modules/diversion/reconciliation.py)

Backed by a shared `stock_events` data model (app/core/models.py).

## Run locally
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Then visit http://127.0.0.1:8000/docs for interactive API docs.

## Test
pytest

Drop the PRD / Architecture / Business Case markdown files into docs/ for reference.
EOF

# 8. Database setup
cat > app/core/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./medtrack.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

# 9. Core models -- shared backbone for all three modules
cat > app/core/models.py << 'EOF'
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class EventType(str, enum.Enum):
    receipt = "receipt"
    dispense = "dispense"
    adjustment = "adjustment"
    stockout_reported = "stockout_reported"
    reported_usage = "reported_usage"  # feeds Module 3 reconciliation


class Facility(Base):
    __tablename__ = "facilities"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False, default="UG")  # country-agnostic from day one
    district = Column(String)
    level_of_care = Column(String)

    stock_events = relationship("StockEvent", back_populates="facility")


class Commodity(Base):
    __tablename__ = "commodities"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    program = Column(String)  # HIV / TB / malaria / other

    stock_events = relationship("StockEvent", back_populates="commodity")


class StockEvent(Base):
    __tablename__ = "stock_events"
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    quantity = Column(Float, nullable=False)
    event_time = Column(DateTime, default=datetime.utcnow)
    source = Column(String, default="manual")  # manual, csv, api, lmis

    facility = relationship("Facility", back_populates="stock_events")
    commodity = relationship("Commodity", back_populates="stock_events")
EOF

# 10. Pydantic schemas
cat > app/core/schemas.py << 'EOF'
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.core.models import EventType


class StockEventCreate(BaseModel):
    facility_id: int
    commodity_id: int
    event_type: EventType
    quantity: float
    event_time: Optional[datetime] = None
    source: str = "manual"


class StockEventOut(StockEventCreate):
    id: int

    class Config:
        from_attributes = True
EOF

# 11. Module 2 -- Supply Visibility & Forecasting (pure python, no pandas)
cat > app/modules/supply/forecasting.py << 'EOF'
"""
Module 2: Supply Visibility & Forecasting
Rolling consumption rate vs. on-hand quantity -> days-of-stock-remaining.
No seasonality or lead-time modeling at MVP -- see architecture doc.
"""
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.models import StockEvent, EventType


def _current_on_hand(db: Session, facility_id: int, commodity_id: int) -> float:
    events = db.query(StockEvent).filter(
        StockEvent.facility_id == facility_id,
        StockEvent.commodity_id == commodity_id,
    ).all()

    total = 0.0
    for e in events:
        if e.event_type == EventType.receipt:
            total += e.quantity
        elif e.event_type == EventType.dispense:
            total -= e.quantity
        elif e.event_type == EventType.adjustment:
            total += e.quantity  # signed
    return total


def days_of_stock_remaining(
    db: Session, facility_id: int, commodity_id: int, window_days: int = 30
) -> Optional[float]:
    cutoff = datetime.utcnow() - timedelta(days=window_days)

    dispense_rows = db.query(StockEvent).filter(
        StockEvent.facility_id == facility_id,
        StockEvent.commodity_id == commodity_id,
        StockEvent.event_type == EventType.dispense,
        StockEvent.event_time >= cutoff,
    ).all()

    total_dispensed = sum(e.quantity for e in dispense_rows)
    if total_dispensed <= 0:
        return None  # not enough data yet

    daily_rate = total_dispensed / window_days
    on_hand = _current_on_hand(db, facility_id, commodity_id)

    return round(on_hand / daily_rate, 1)


def stockout_risk_flag(days_remaining: Optional[float], threshold_days: int = 14) -> bool:
    if days_remaining is None:
        return False
    return days_remaining <= threshold_days
EOF

# 12. Module 3 -- Diversion & Leakage Detection
cat > app/modules/diversion/reconciliation.py << 'EOF'
"""
Module 3: Diversion & Leakage Detection
Compares dispensed quantity against reported_usage for the same
facility/commodity/window. Conservative by design -- a false positive
implicates real staff. See architecture doc on audit trail requirements.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.models import StockEvent, EventType


def reconciliation_discrepancy(
    db: Session,
    facility_id: int,
    commodity_id: int,
    window_days: int = 30,
    threshold_pct: float = 0.20,
) -> dict:
    cutoff = datetime.utcnow() - timedelta(days=window_days)

    events = db.query(StockEvent).filter(
        StockEvent.facility_id == facility_id,
        StockEvent.commodity_id == commodity_id,
        StockEvent.event_time >= cutoff,
    ).all()

    dispensed = sum(e.quantity for e in events if e.event_type == EventType.dispense)
    reported = sum(e.quantity for e in events if e.event_type == EventType.reported_usage)

    if dispensed == 0:
        return {"flag": False, "reason": "insufficient_data"}

    discrepancy_pct = abs(dispensed - reported) / dispensed

    return {
        "flag": discrepancy_pct >= threshold_pct,
        "dispensed": dispensed,
        "reported_usage": reported,
        "discrepancy_pct": round(discrepancy_pct, 3),
    }
EOF

# 13. Module 1 placeholder -- merge existing verification logic here
cat > app/modules/quality/engine.py << 'EOF'
"""
Module 1: Quality Triage (placeholder)
This is where the already-built verification logic gets merged in.
Wire it to read/write against the same facility_id / commodity_id keys
used by Modules 2 and 3 so the dashboard can combine all three flags.
"""

def flag_quality_risk(commodity_id: int, facility_id: int) -> dict:
    # TODO: replace with existing verification logic
    return {"flag": False, "reason": "not_yet_implemented"}
EOF

# 14. API routes
cat > app/api/routes_stock_events.py << 'EOF'
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.models import StockEvent
from app.core.schemas import StockEventCreate, StockEventOut

router = APIRouter(prefix="/stock-events", tags=["stock_events"])


@router.post("/", response_model=StockEventOut)
def create_stock_event(event: StockEventCreate, db: Session = Depends(get_db)):
    db_event = StockEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.get("/", response_model=List[StockEventOut])
def list_stock_events(db: Session = Depends(get_db)):
    return db.query(StockEvent).all()
EOF

cat > app/api/routes_dashboard.py << 'EOF'
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.supply.forecasting import days_of_stock_remaining, stockout_risk_flag
from app.modules.diversion.reconciliation import reconciliation_discrepancy
from app.modules.quality.engine import flag_quality_risk

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{facility_id}/{commodity_id}")
def facility_commodity_snapshot(facility_id: int, commodity_id: int, db: Session = Depends(get_db)):
    days_remaining = days_of_stock_remaining(db, facility_id, commodity_id)
    return {
        "facility_id": facility_id,
        "commodity_id": commodity_id,
        "days_of_stock_remaining": days_remaining,
        "stockout_risk": stockout_risk_flag(days_remaining),
        "diversion_check": reconciliation_discrepancy(db, facility_id, commodity_id),
        "quality_flag": flag_quality_risk(commodity_id, facility_id),
    }
EOF

# 15. App entrypoint
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from app.core.database import Base, engine
from app.api import routes_stock_events, routes_dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MedTrack",
    description="Supply visibility, quality triage, and diversion detection for African essential-medicine supply chains.",
)

app.include_router(routes_stock_events.router)
app.include_router(routes_dashboard.router)


@app.get("/")
def root():
    return {
        "status": "MedTrack API running",
        "modules": ["quality_triage", "supply_visibility", "diversion_detection"],
    }
EOF

# 16. Sample data for testing ingestion
cat > data/sample_stock_events.csv << 'EOF'
facility_id,commodity_id,event_type,quantity,event_time,source
1,1,receipt,500,2026-05-01T00:00:00,manual
1,1,dispense,20,2026-05-05T00:00:00,manual
1,1,dispense,18,2026-05-12T00:00:00,manual
1,1,reported_usage,38,2026-05-12T00:00:00,manual
EOF

# 17. Smoke test
cat > tests/test_forecasting.py << 'EOF'
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.core.models import Facility, Commodity, StockEvent, EventType
from app.modules.supply.forecasting import days_of_stock_remaining


def test_days_of_stock_remaining():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    facility = Facility(name="Test Facility", country="UG")
    commodity = Commodity(name="Test Commodity", program="malaria")
    db.add_all([facility, commodity])
    db.commit()

    db.add(StockEvent(facility_id=facility.id, commodity_id=commodity.id,
                       event_type=EventType.receipt, quantity=300, event_time=datetime.utcnow()))
    db.add(StockEvent(facility_id=facility.id, commodity_id=commodity.id,
                       event_type=EventType.dispense, quantity=30, event_time=datetime.utcnow()))
    db.commit()

    result = days_of_stock_remaining(db, facility.id, commodity.id)
    assert result is not None
    assert result > 0
EOF

# 18. Git init
git init -q
git add .
git commit -q -m "MedTrack skeleton: shared stock_events model, supply forecasting stub, diversion reconciliation stub, quality module placeholder"

echo ""
echo "== Done =="
echo "cd ~/medtrack && source venv/bin/activate"
echo "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "pytest"
