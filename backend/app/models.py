from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .database import Base

class Repository(Base):
    __tablename__ = "repositories"
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    status = Column(String, default="ready")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CodeChunk(Base):
    __tablename__ = "code_chunks"
    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    path = Column(String, nullable=False)
    language = Column(String, default="text")
    start_line = Column(Integer, default=1)
    end_line = Column(Integer, default=1)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384))
