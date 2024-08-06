from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Float,
    Index
)
from sqlalchemy.orm import relationship
from ..db.database import Base

class UserResponse(Base):
    __tablename__ = 'user_responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_assignment_id = Column(Integer, ForeignKey('user_assignments.id'), nullable=False)
    session_timestamp = Column(DateTime, nullable=False)
    response = Column(String, nullable=False)
    correct = Column(Integer, nullable=False)  # 1 for correct, 0 for incorrect
    selected_option_id = Column(Integer, ForeignKey('options.id'), nullable=True)
    difficulty = Column(Integer, nullable=False)
    last_grade = Column(Float, nullable=False)

    user_assignment = relationship("UserAssignment", back_populates="responses")
    selected_option = relationship("Option")

    __table_args__ = (
        Index('idx_user_response_user_assignment_id', "user_assignment_id"),
        Index('idx_user_response_session_timestamp', "session_timestamp"),
    )
