from sqlalchemy import Column, Integer, Text, Date, Float
from sqlalchemy.sql import func
from db.session import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id         = Column(Integer, primary_key=True, index=True)
    date       = Column(Date, nullable=False, unique=True, index=True)
    content    = Column(Text, nullable=False)
    mood_score = Column(Float, nullable=True)
