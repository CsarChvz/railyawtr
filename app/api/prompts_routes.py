import logging
import os
from typing import Counter, List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query
from openai import BaseModel
from sqlalchemy.orm import Session

from app.schemas.prompt_individual import PromptIndividual
from app.utils.auth import AuthenticationChecker, get_current_user
from app.db.database import get_db_session
from app.data_access import (create_prompt_emb, find_similar_prompts)
from app.schemas import PromptBase, PromptResult, PromptUpdate
from app.services import (
    create_prompt_service,
    delete_prompt_service,
    get_user_prompts_service,
    update_prompt_service,
    get_prompt,
    get_all_prompts_service,
    generate_embeddings,
    generate_questions
)

load_dotenv()

prompts_router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



class TrendingPromptSchema(BaseModel):
    text: str
    frequency: int


@prompts_router.get("/embed")
def get_simiar( 
    text: str = Query(...),
    db: Session = Depends(get_db_session)
):
    result = generate_embeddings(text)
    prompts = find_similar_prompts(result, db)

    # questions = generate_questions(text)
    # print(questions)
    for prompt, score in prompts:
        print(score)
    return  [PromptResult.model_validate(prompt) for prompt, score in prompts]

@prompts_router.get("/trending", response_model=List[TrendingPromptSchema])
def get_trending_prompts(db: Session = Depends(get_db_session)):
    try:
        prompts = get_all_prompts_service(db)
        
        if not prompts:
            raise HTTPException(status_code=404, detail="No prompts found")
        
        prompt_texts = [prompt.text for prompt in prompts]

        prompt_counter = Counter(prompt_texts)

        most_common_prompts = prompt_counter.most_common(10)

        response = [
            {"text": prompt, "frequency": frequency}
            for prompt, frequency in most_common_prompts
        ]

        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while retrieving trending prompts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@prompts_router.post(
    "", response_model=PromptResult
)
def create_prompt(
    prompt_data: PromptBase,
    user_id: str = Query(...),
    db: Session = Depends(get_db_session),
):
    try:
        if not prompt_data.text:
            raise HTTPException(
                status_code=506, detail="Missing required fields: text"
            )

        # Verificar si estamos en un entorno de pruebas
        if os.getenv("TESTING") == "1":
            current_user_id = prompt_data.user_id
        else:
            current_user_id = user_id

        prompt = create_prompt_service(prompt_data, current_user_id, db)
        return PromptResult.model_validate(prompt)
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error while creating prompt: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@prompts_router.get(
    "/user/{user_id}",
    response_model=list[PromptResult],
)
def get_user_prompts(user_id: str, db: Session = Depends(get_db_session)):
    try:
        return get_user_prompts_service(user_id, db)
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while retrieving prompts for user {user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")

@prompts_router.get(
    "/history",
    response_model=list[PromptResult],
)
def get_user_prompts(user_id: str = Query(...), db: Session = Depends(get_db_session)):
    try:
        return get_user_prompts_service(user_id, db)
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while retrieving prompts for user {user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@prompts_router.get(
    "/{prompt_id}",
    response_model=PromptIndividual,
)
def get_user_prompts(prompt_id: int, db: Session = Depends(get_db_session)):
    try:
        return get_prompt(prompt_id=prompt_id, db=db)
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error while retrieving prompt {prompt_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")

@prompts_router.put(
    "/{prompt_id}",
    response_model=PromptResult,
    status_code=201,
)
def update_prompt(
    prompt_id: int,
    prompt_data: PromptUpdate,
    db: Session = Depends(get_db_session),
):
    try:
        return update_prompt_service(prompt_id, prompt_data, db)
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@prompts_router.delete(
    "/{prompt_id}",
    response_model=PromptResult,
    status_code=201,
)
def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db_session),
):
    try:
        return delete_prompt_service(prompt_id, db)
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        logger.error(f"Unexpected error while updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@prompts_router.post("/embed")
def post_emmbede( 
    prompt_data: PromptBase,
    db: Session = Depends(get_db_session)
):
    result = generate_embeddings(prompt_data.text)
    prompt = create_prompt_emb(text=prompt_data.text, user_id="google-oauth2|116218682452035897380", embedding=result, db=db)
    return PromptResult.model_validate(prompt) 

