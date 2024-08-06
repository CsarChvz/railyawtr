import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.utils.auth import AuthenticationChecker, get_current_user
from app.db.database import get_db_session
from app.schemas import NotificationCreateSchema, NotificationResponseSchema, NotificationBaseSchema
from app.services import (
    create_notification_service,
    get_notifications_service,
    get_notification_by_id_service,
    update_notification_service,
    delete_notification_service,
)

notification_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@notification_router.post(
    "/",
    response_model=NotificationResponseSchema,
    status_code=201,
)
def create_notification(
    notification_data: NotificationBaseSchema,
    user_id: str = Query(...),
    db: Session = Depends(get_db_session),
):
    try:
        return create_notification_service(notification_data, user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating notification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@notification_router.get(
    "/",
    response_model=List[NotificationResponseSchema],
)
def get_notifications(
    user_id: str = Query(...),
    db: Session = Depends(get_db_session),
):
    try:
        return get_notifications_service(user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while retrieving notifications: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@notification_router.get(
    "/{notification_id}",
    response_model=NotificationResponseSchema,
)
def get_notification_by_id(
    notification_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return get_notification_by_id_service(notification_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while retrieving notification {notification_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@notification_router.put(
    "/{notification_id}",
    response_model=NotificationResponseSchema,
)
def update_notification(
    notification_id: int,
    notification_data: NotificationCreateSchema,
    db: Session = Depends(get_db_session),
):
    try:
        return update_notification_service(notification_id, notification_data, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while updating notification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@notification_router.delete(
    "/{notification_id}",
    response_model=NotificationResponseSchema,
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return delete_notification_service(notification_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while deleting notification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
