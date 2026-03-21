from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from db.session import Base


class Memory(Base):
    __tablename__ = "memories"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    type       = Column(String, default="daily_summary")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    # embedding stored as text (JSON array) — pgvector column added via migration
