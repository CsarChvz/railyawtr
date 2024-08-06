from sqlalchemy.orm import Session
from app.models import InvestorInterest
from app.schemas import InvestorInterestCreate

def create_investor_interest(db: Session, investor_interest: InvestorInterestCreate, user_id: str):
    db_investor_interest = InvestorInterest(
        user_id=user_id,
        amount=investor_interest.amount,
        reason=investor_interest.reason
    )
    db.add(db_investor_interest)
    db.commit()
    db.refresh(db_investor_interest)
    return db_investor_interest

def get_investor_interests(db: Session, skip: int = 0, limit: int = 10):
    return db.query(InvestorInterest).offset(skip).limit(limit).all()

def get_investor_interest(db: Session, investor_interest_id: int):
    return db.query(InvestorInterest).filter(InvestorInterest.id == investor_interest_id).first()

def get_investor_interests(db: Session, skip: int = 0, limit: int = 10):
    return db.query(InvestorInterest).offset(skip).limit(limit).all()

def get_investor_interest(db: Session, investor_interest_id: int):
    return db.query(InvestorInterest).filter(InvestorInterest.id == investor_interest_id).first()
