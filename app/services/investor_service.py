import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas import InvestorInterestCreate, InvestorInterestResponse
from app.data_access import create_investor_interest, get_investor_interests, get_investor_interest

logger = logging.getLogger(__name__)

def create_investor_interest_service(investor_interest_data: InvestorInterestCreate, user_id: str, db: Session) -> InvestorInterestResponse:
    try:
        new_investor_interest = create_investor_interest(db, investor_interest_data, user_id)
        return InvestorInterestResponse.from_orm(new_investor_interest)
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating investor interest: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_investor_interests_service(skip: int, limit: int, db: Session) -> list[InvestorInterestResponse]:
    try:
        investor_interests = get_investor_interests(db, skip, limit)
        return [InvestorInterestResponse.from_orm(investor_interest) for investor_interest in investor_interests]
    except Exception as e:
        logger.error(f"Error getting investor interests: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_investor_interest_service(investor_interest_id: int, db: Session) -> InvestorInterestResponse:
    try:
        investor_interest = get_investor_interest(db, investor_interest_id)
        if not investor_interest:
            raise HTTPException(status_code=404, detail="Investor interest not found")
        return InvestorInterestResponse.from_orm(investor_interest)
    except Exception as e:
        logger.error(f"Error getting investor interest: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
