from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, text, Index
from sqlalchemy.orm import relationship
import sqlalchemy

from ..db.database import Base

class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), index=True)
    option_text = Column(String, nullable=False)
    is_correct_answer = Column(Boolean, default=False)
    is_selected = Column(Boolean, default=False)
    is_typed = Column(Boolean, default=False)
    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=sqlalchemy.func.now(),
    )

    question = relationship("Question", back_populates="options")
    user_responses = relationship('UserResponse', back_populates='selected_option')

    __table_args__ = (
        Index('idx_option_question_id', 'question_id'),
    )
