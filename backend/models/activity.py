from sqlalchemy import Column, Integer, String, Float, Boolean
from db.session import Base


class Activity(Base):
    __tablename__ = "activities"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False, unique=True)
    category     = Column(String, default="general")
    unit         = Column(String, default="count")
    target_value = Column(Float, nullable=True)
    is_auto      = Column(Boolean, default=False)
    description  = Column(String, nullable=True)
