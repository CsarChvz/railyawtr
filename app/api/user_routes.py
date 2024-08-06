import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.user_auth_base import UserAuth0Base
from app.utils.auth import AuthenticationChecker, PermissionsValidator, get_current_user
from app.db.database import get_db_session
from app.schemas import UserReturn, UserUpdate, UserUpdateAdmin
from app.services import (
    delete_user_service,
    get_user_service,
    update_user_service,
    create_user_auth0
)
import os
from dotenv import load_dotenv
user_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
# @user_router.post(
#     "/",
#     response_model=UserReturn,
#     status_code=201,
#     dependencies=[Depends(PermissionsValidator(["crud:admin-create-user"]))],
# )
# async def create_user(user: UserCreate, db: Session = Depends(get_db_session)):
#     try:
#         return await create_user_service(user, db)
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         logger.error(f"Unexpected error while creating user: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

@user_router.post(
    "/",
    status_code=201,
    response_model=UserAuth0Base
)
async def create_user(user: UserAuth0Base,  secret_key: str = Query(...), db: Session = Depends(get_db_session)):
    if(secret_key == SECRET_KEY):
        try:
            return await create_user_auth0(user, db)
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Unexpected error while creating user: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    else:
        raise HTTPException(status_code=400, detail="Unaturoized")



@user_router.get(
    "/{user_id}",
    response_model=UserReturn,
    status_code=200,
)
def get_user(user_id: str, db: Session = Depends(get_db_session)):
    try:
        return get_user_service(user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@user_router.put(
    "/{user_id}/admin",
    response_model=UserReturn,
    status_code=200,
)
def update_user_admin(
    user_id: str, user_data: UserUpdateAdmin, db: Session = Depends(get_db_session)
):
    try:
        return update_user_service(user_id, user_data, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@user_router.put(
    "/me",
    response_model=UserReturn,
    status_code=200,
)
def update_user_me(
   user_data: UserUpdate, user_id: str = Query(...), db: Session = Depends(get_db_session),
):
    try:
        
        return update_user_service(user_id=user_id,user_data=user_data, db=db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")




@user_router.put(
    "/{user_id}",
    response_model=UserReturn,
    status_code=200,
)
def update_user(
    user_id: str, user_data: UserUpdate, db: Session = Depends(get_db_session)
):
    try:
        return update_user_service(user_id, user_data, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@user_router.delete(
    "/{user_id}",
    response_model=str,
    status_code=200,
)
def delete_user(user_id: str, token: str = Query(...), db: Session = Depends(get_db_session)):
    try:
        return delete_user_service(user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while deleting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@user_router.get(
    "/profile-user/me",
    response_model=UserReturn,
    status_code=200,
)
def get_user_me(
    user_id: str = Query(...),
    db: Session = Depends(get_db_session),
):
    try:
        return get_user_service(user_id, db)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while retrieving user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
