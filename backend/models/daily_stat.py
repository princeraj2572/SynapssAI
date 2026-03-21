from sqlalchemy import Column, Integer, Float, Date, ForeignKey, UniqueConstraint
from db.session import Base


class DailyStat(Base):
    __tablename__ = "daily_stats"

    id          = Column(Integer, primary_key=True, index=True)
    date        = Column(Date, nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False, index=True)
    total_value = Column(Float, default=0.0)
    event_count = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("date", "activity_id", name="uq_daily_stat"),)
