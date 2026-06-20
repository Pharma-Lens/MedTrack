from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text
from sqlalchemy.sql import func
import enum
from app.database import Base


class EventType(str, enum.Enum):
    RECEIVED = "received"
    DISPENSED = "dispensed"
    EXPIRED = "expired"
    RETURNED = "returned"
    TRANSFERRED = "transferred"
    LOSS_REPORTED = "loss_reported"


class QualityFlag(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    SUSPECT = "suspect"
    UNVERIFIED = "unverified"


class StockEvent(Base):
    """
    The unified data spine for MedTrack.
    One record per medicine movement event — received, dispensed, lost, etc.
    All three modules (quality, availability, diversion) read and write this table.
    """
    __tablename__ = "stock_events"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(String(64), nullable=False, index=True)
    medicine_id = Column(String(64), nullable=False, index=True)
    medicine_name = Column(String(256), nullable=False)
    batch_number = Column(String(128), nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(32), default="units")

    # Quality module fields
    quality_flag = Column(Enum(QualityFlag), default=QualityFlag.UNVERIFIED)
    quality_notes = Column(Text, nullable=True)

    # Supply / availability fields
    stock_on_hand_after = Column(Float, nullable=True)
    reorder_level = Column(Float, nullable=True)

    # Diversion / reconciliation fields
    expected_quantity = Column(Float, nullable=True)   # what the system expected
    variance = Column(Float, nullable=True)            # quantity - expected_quantity

    # Metadata
    recorded_by = Column(String(128), nullable=True)
    source_system = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<StockEvent {self.event_type} {self.medicine_name} x{self.quantity} @ {self.facility_id}>"
