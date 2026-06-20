from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.stock_event import EventType, QualityFlag


class StockEventCreate(BaseModel):
    facility_id: str
    medicine_id: str
    medicine_name: str
    batch_number: Optional[str] = None
    event_type: EventType
    quantity: float = Field(gt=0)
    unit: str = "units"
    quality_flag: Optional[QualityFlag] = QualityFlag.UNVERIFIED
    quality_notes: Optional[str] = None
    stock_on_hand_after: Optional[float] = None
    reorder_level: Optional[float] = None
    expected_quantity: Optional[float] = None
    recorded_by: Optional[str] = None
    source_system: Optional[str] = None


class StockEventOut(StockEventCreate):
    id: int
    variance: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QualityVerificationResult(BaseModel):
    event_id: int
    medicine_name: str
    batch_number: Optional[str]
    quality_flag: QualityFlag
    confidence: float
    notes: str


class StockoutRisk(BaseModel):
    facility_id: str
    medicine_id: str
    medicine_name: str
    stock_on_hand: float
    reorder_level: float
    days_of_stock_remaining: Optional[float]
    risk_level: str   # "low" | "medium" | "high" | "critical"
    recommendation: str


class DiversionAlert(BaseModel):
    facility_id: str
    medicine_id: str
    medicine_name: str
    expected_quantity: float
    actual_quantity: float
    variance: float
    variance_pct: float
    alert_level: str   # "normal" | "watch" | "alert" | "critical"
    flagged_at: datetime


class DashboardSummary(BaseModel):
    total_events: int
    quality_failures: int
    stockout_risks: int
    diversion_alerts: int
    facilities_monitored: int
    medicines_tracked: int
