from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from db.session import Base


class Event(Base):
    __tablename__ = "events"

    id          = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False, index=True)
    start_time  = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time    = Column(DateTime(timezone=True), nullable=True)
    value       = Column(Float, default=1.0)
    source      = Column(String, default="manual")
    notes       = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
