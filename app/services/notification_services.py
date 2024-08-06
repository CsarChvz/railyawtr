import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.data_access import (
    create_notification,
    get_notifications,
    get_notification_by_id,
    update_notification,
    delete_notification,
)
from app.schemas import  NotificationCreateSchema, NotificationResponseSchema

logger = logging.getLogger(__name__)

def create_notification_service(notification_data: NotificationCreateSchema,user_id:str, db: Session) -> NotificationResponseSchema:
    try:
        new_notification = create_notification(notification_data, user_id, db)
        return NotificationResponseSchema.from_orm(new_notification)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while creating notification: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

def get_notifications_service(user_id: str, db: Session) -> list[NotificationResponseSchema]:
    try:
        notifications = get_notifications(user_id, db)
        return [NotificationResponseSchema.from_orm(notification) for notification in notifications]
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while retrieving notifications: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

def get_notification_by_id_service(notification_id: int, db: Session) -> NotificationResponseSchema:
    try:
        notification = get_notification_by_id(notification_id, db)
        if notification is None:
            raise HTTPException(status_code=404, detail='Notification not found')
        return NotificationResponseSchema.from_orm(notification)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while retrieving notification {notification_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

def update_notification_service(notification_id: int, notification_data: NotificationCreateSchema, db: Session) -> NotificationResponseSchema:
    try:
        notification = update_notification(notification_id, notification_data, db)
        if notification is None:
            raise HTTPException(status_code=404, detail='Notification not found')
        return NotificationResponseSchema.from_orm(notification)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while updating notification {notification_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')

def delete_notification_service(notification_id: int, db: Session) -> NotificationResponseSchema:
    try:
        notification = delete_notification(notification_id, db)
        if notification is None:
            raise HTTPException(status_code=404, detail='Notification not found')
        return NotificationResponseSchema.from_orm(notification)
    except Exception as e:
        db.rollback()
        logger.error(f'Unexpected error while deleting notification {notification_id}: {e}')
        raise HTTPException(status_code=500, detail='Internal server error')
