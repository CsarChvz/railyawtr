import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.utils.auth import AuthenticationChecker, get_current_user
from app.db.database import get_db_session
from app.schemas import InvestorInterestCreate, InvestorInterestResponse, InvestorInterestBase
from app.services import (
    create_investor_interest_service,
    get_investor_interests_service,
    get_investor_interest_service,
)

investor_interest_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@investor_interest_router.post(
    "/",
    response_model=InvestorInterestResponse,
    status_code=201,
)
def create_investor_interest(
    investor_interest_data: InvestorInterestCreate,
    user_id: str= Query(...),
    db: Session = Depends(get_db_session),
):
    try:
        return create_investor_interest_service(investor_interest_data, user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating investor interest: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@investor_interest_router.get(
    "/",
    response_model=List[InvestorInterestResponse],
)
def get_investor_interests(
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db_session),
):
    try:
        return get_investor_interests_service(skip, limit, db)
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@investor_interest_router.get(
    "/{investor_interest_id}",
    response_model=InvestorInterestResponse,
)
def get_investor_interest_by_id(
    investor_interest_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return get_investor_interest_service(investor_interest_id, db)
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
