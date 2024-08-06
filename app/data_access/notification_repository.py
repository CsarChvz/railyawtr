from sqlalchemy.orm import Session
from app.models import Notification
from app.schemas import NotificationBaseSchema, NotificationCreateSchema

def create_notification(notification_data: NotificationCreateSchema, user_id:str, db: Session) -> Notification:
    new_notification = Notification(**notification_data.dict(), user_id=user_id)
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

def get_notifications(user_id: str, db: Session) -> list[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).all()

def get_notification_by_id(notification_id: int, db: Session) -> Notification:
    return db.query(Notification).filter(Notification.id == notification_id).first()

def update_notification(notification_id: int, notification_data: NotificationBaseSchema, db: Session) -> Notification:
    notification = get_notification_by_id(notification_id, db)
    if notification is None:
        return None
    for key, value in notification_data.dict(exclude_unset=True).items():
        setattr(notification, key, value)
    db.commit()
    db.refresh(notification)
    return notification

def delete_notification(notification_id: int, db: Session) -> Notification:
    notification = get_notification_by_id(notification_id, db)
    if notification is None:
        return None
    db.delete(notification)
    db.commit()
    return notification
