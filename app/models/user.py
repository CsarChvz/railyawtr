from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    String,
    text,
    Index,
    ForeignKey,
)
import sqlalchemy
from sqlalchemy.orm import relationship
from ..db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String)
    username = Column(String, unique=True)
    birthday = Column(Date)
    gender = Column(String)
    bio = Column(String)
    profile_picture = Column(String)
    location = Column(String)
    email = Column(String, unique=True)
    verified = Column(Boolean, default=False)
    school_num_handles = Column(String)
    phone_number = Column(String, default="5555555555")
    password_hashed = Column(String)
    providers = Column(String)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=sqlalchemy.func.now())

    user_assignments = relationship('UserAssignment', back_populates='user')
    decks = relationship('Deck', back_populates='user')
    prompts = relationship("Prompt", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    following = relationship("Contact", foreign_keys="[Contact.follower_id]", back_populates="follower")
    followers = relationship("Contact", foreign_keys="[Contact.followed_id]", back_populates="followed")
    investor_interests = relationship("InvestorInterest", back_populates="user")

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
    )
