from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
    Index
)
import sqlalchemy
from sqlalchemy.orm import relationship
from ..db.database import Base

class Deck(Base):
    __tablename__ = 'decks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    prompt_id = Column(Integer, ForeignKey('prompts.id'), nullable=False)
    name = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=sqlalchemy.func.now())

    user = relationship('User', back_populates='decks')
    prompt = relationship('Prompt', back_populates='decks')
    user_assignments = relationship('UserAssignment', back_populates='deck')

    __table_args__ = (
        Index('idx_deck_user_id', 'user_id'),
        Index('idx_deck_prompt_id', 'prompt_id'),
    )
