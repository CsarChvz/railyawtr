from sqlalchemy import Column, DateTime, Integer, String, Numeric, text, ForeignKey
from sqlalchemy.orm import relationship
import sqlalchemy
from ..db.database import Base

class InvestorInterest(Base):
    __tablename__ = 'investor_interest'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP'),
    )
    
    user = relationship('User', back_populates='investor_interests')
