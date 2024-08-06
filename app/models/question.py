from sqlalchemy import (
    
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
    Column,
    Index
)
from sqlalchemy.orm import relationship
from ..db.database import Base
from pgvector.sqlalchemy import Vector

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    prompt_id = Column(Integer, ForeignKey("prompts.id"), index=True)
    question_text = Column(String)
    difficulty = Column(Integer, default=1)
    #embedding = Column(Vector(1536))
    
    options = relationship("Option", back_populates="question")
    prompt = relationship("Prompt", back_populates="questions")
    user_assignments = relationship('UserAssignment', back_populates='question')

    __table_args__ = (
        Index('idx_question_prompt_id', 'prompt_id'),
    )
