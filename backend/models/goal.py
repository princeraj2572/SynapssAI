from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from db.session import Base


class Goal(Base):
    __tablename__ = "goals"

    id          = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), index=True)
    description = Column(String, nullable=False)
    target      = Column(Float, nullable=False)
    period      = Column(String, default="daily")   # daily | weekly | monthly
    start_date  = Column(Date, nullable=True)
    end_date    = Column(Date, nullable=True)
    completed   = Column(Boolean, default=False)
