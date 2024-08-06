# En app/models/user_assignment.py

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    String,
    func,
    text,
    Index,
    Date
)
from sqlalchemy.orm import relationship
from ..db.database import Base

class UserAssignment(Base):
    __tablename__ = 'user_assignments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    deck_id = Column(Integer, ForeignKey('decks.id'), nullable=False)
    prompt_id = Column(Integer, ForeignKey('prompts.id'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    selected_option_id = Column(Integer, ForeignKey('options.id'), nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    last_reviewed_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    next_review_date = Column(Date, server_default=func.current_date())
    interval = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)
    review_count = Column(Integer, default=0)

    user = relationship("User", back_populates="user_assignments")
    deck = relationship("Deck", back_populates="user_assignments")
    prompt = relationship("Prompt", back_populates="user_assignments")
    question = relationship("Question", back_populates="user_assignments")
    selected_option = relationship("Option", back_populates="user_assignments")

    __table_args__ = (
        Index('idx_user_assignment_user_id', "user_id"),
        Index('idx_user_assignment_deck_id', "deck_id"),
        Index('idx_user_assignment_prompt_id', "prompt_id"),
        Index('idx_user_assignment_question_id', "question_id"),
        Index('idx_user_assignment_selected_option_id', "selected_option_id"),
        Index('idx_user_assignment_next_review_date', "next_review_date"),
    )