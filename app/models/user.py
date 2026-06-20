"""
app/models/user.py
MedTrack user accounts — facility staff, administrators, auditors.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    FACILITY_STAFF = "facility_staff"
    AUDITOR = "auditor"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    full_name = Column(String(256), nullable=False)
    hashed_password = Column(String(512), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FACILITY_STAFF)
    facility_id = Column(String(64), nullable=True)   # None = access to all facilities
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"