import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.is_selected_updated import UpdateIsSelectedSchema
from app.utils.auth import AuthenticationChecker
from app.db.database import get_db_session
from app.schemas import OptionBase, OptionResult
from app.services import (
    create_option_for_question_service,
    delete_option_service,
    get_options_for_question_service,
    update_option_service,
    update_is_selected_service,
    create_option_typed_for_question_service
)


options_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@options_router.get(
    "/question/{question_id}/options",
    response_model=List[OptionResult],
)
def get_options_for_question(question_id: int, db: Session = Depends(get_db_session)):
    try:
        return get_options_for_question_service(question_id, db)
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@options_router.post(
    "/question/{question_id}/options",
    response_model=List[OptionResult],
    status_code=201,
)
def create_option_for_question(
    question_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return create_option_for_question_service(question_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating option: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@options_router.post(
    "/question/{question_id}/option-typed",
    response_model=OptionResult,
    status_code=201,
)
def create_option_typed_for_question(
    question_id: int,
    option_data: OptionBase,
    lang: str = Query(...),
    db: Session = Depends(get_db_session),
):
    try:
        return create_option_typed_for_question_service(question_id=question_id,option_text=option_data.option_text,lang=lang,db=db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating option: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


@options_router.put(
    "/option/{option_id}",
    response_model=OptionResult,
    status_code=201,
)
def update_option(
    option_id: int,
    option_data: OptionBase,
    db: Session = Depends(get_db_session),
):
    try:
        return update_option_service(option_id, option_data, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while updating option: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@options_router.delete(
    "/option/{option_id}",
    response_model=OptionResult,
    status_code=201,
)
def delete_option(
    option_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return delete_option_service(option_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while deleting option: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@options_router.put(
    "/option/{option_id}/is-selected",
    response_model=OptionResult,
    status_code=200,
)
def update_is_selected(
    option_id: int,
    update_data: UpdateIsSelectedSchema,
    db: Session = Depends(get_db_session),
):
    try:
        return update_is_selected_service(option_id, update_data, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while updating is_selected: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")