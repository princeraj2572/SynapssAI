from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from db.session import Base


class Alert(Base):
    __tablename__ = "alerts"

    id           = Column(Integer, primary_key=True, index=True)
    type         = Column(String, nullable=False)   # burnout | streak_risk | goal_missed
    message      = Column(Text, nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    dismissed    = Column(Boolean, default=False)
