from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
    Index
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from ..db.database import Base


class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    text = Column(String)
    user_id = Column(String, ForeignKey('users.id'), index=True)
    #embedding = Column(Vector(1536))
    
    user = relationship('User', back_populates='prompts')
    questions = relationship('Question', back_populates='prompt')
    user_assignments = relationship('UserAssignment', back_populates='prompt')
    decks = relationship('Deck', back_populates='prompt')  # Add this line if 'decks' should exist

    __table_args__ = (
        Index('idx_prompt_user_id', 'user_id'),
    )
