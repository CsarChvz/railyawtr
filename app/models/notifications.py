from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, text, JSON
from sqlalchemy.orm import relationship
import sqlalchemy

from ..db.database import Base


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    type_notification = Column(String, nullable=False)  # Tipo de notificación (e.g., "promotion", "new_contact", "billing_info")
    message = Column(String, nullable=False)
    data = Column(JSON, nullable=True)  # Información específica del tipo de notificación
    read = Column(Boolean, default=False)
    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=sqlalchemy.func.now(),
    )

    user = relationship("User", back_populates="notifications")
