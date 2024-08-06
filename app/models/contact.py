from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    text,
    ForeignKey,
    Index,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from ..db.database import Base

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))
    followed_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))
    created_at = Column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP'),
    )

    follower = relationship('User', foreign_keys=[follower_id], back_populates='following')
    followed = relationship('User', foreign_keys=[followed_id], back_populates='followers')

    __table_args__ = (
        UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),
        Index('idx_follower_id', 'follower_id'),
        Index('idx_followed_id', 'followed_id'),
    )
