from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    text,
    ForeignKey,
    Index
)
from sqlalchemy.orm import relationship
import sqlalchemy

from ..db.database import Base


class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    message = Column(String, nullable=False)
    
    user = relationship('User', back_populates='feedbacks')