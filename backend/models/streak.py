from sqlalchemy import Column, Integer, Date, ForeignKey
from db.session import Base


class Streak(Base):
    __tablename__ = "streaks"

    id             = Column(Integer, primary_key=True)
    activity_id    = Column(Integer, ForeignKey("activities.id"), unique=True, index=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_date      = Column(Date, nullable=True)
