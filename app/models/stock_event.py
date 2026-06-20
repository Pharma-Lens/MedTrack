"""Shared stock_events model — the single data spine for quality, availability, and diversion modules."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base


class StockEvent(Base):
    __tablename__ = "stock_events"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(String, index=True, nullable=False)
    drug_id = Column(String, index=True, nullable=False)
    batch_id = Column(String, nullable=True)
    event_type = Column(String, nullable=False)  # received, dispensed, expired, flagged, etc.
    quantity = Column(Float, nullable=False)
    country = Column(String, nullable=False, default="UG")  # country-agnostic from day one
    source = Column(String, nullable=True)  # e.g. donor program, procurement channel
    timestamp = Column(DateTime, default=datetime.utcnow)
