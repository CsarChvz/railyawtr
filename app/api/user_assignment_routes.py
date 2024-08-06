import random
from fastapi import APIRouter, Depends, HTTPException, Query, HTTPException

from sqlalchemy.orm import Session
import datetime

from app.db.database import get_db_session

from app.models.deck import Deck
from app.models.user import User
from app.models.prompt import Prompt
from app.models.question import Question
from app.models.user_assignment import UserAssignment
from app.models.option import Option

from app.schemas import PromptBase
from app.schemas.user_assignment import UserAssignmentResult
from app.services import (
        get_deck_by_prompt_service,
        create_deck_service,
        create_prompt_service,
        questions_assigned_to_deck_service,
        get_questions_from_a_prompt_service,
        set_questions_assigned_to_deck_service,
        generate_and_save_new_questions_services,
        get_first_assigned_question_service,
        find_prompt_by_text,
        get_prompt,
        get_user_question_assignment_service,
        get_correct_option_service,
        get_all_question_assignments_service,
        get_unassigned_questions_for_user_service,
        get_deck_service,
        calculate_user_level,
        schedule_review
    )

user_assignment_router = APIRouter()

@user_assignment_router.get('/start')
def start_assi(user_id: str, prompt_text: str, db: Session = Depends(get_db_session)):

    '''
    Inica la sesión de estudio del usuario o la retoma si es que ya estudio el mismo prompt

    :param user_id: El usuario
    :param prompt_text: El texto del tema que se busca estudiar
    :param db: La sesión de base de datos.
    '''
    # Buscamos si ya existe el prompt
    prompt = find_prompt_by_text(prompt_text, db)
    if not prompt:
        # Creamos el prompt
        prompt_data = PromptBase(text=prompt_text)
        prompt = create_prompt_service(prompt_data=prompt_data, user_id=user_id, db=db)
        # Checamos si el usuario ya tiene un deck con este prompt
    deck = get_deck_by_prompt_service(user_id,prompt.id, db)
    # Si no esta el deck, entonecs:
    if not deck:
        # Se crea el deck
        deck = create_deck_service(user_id, prompt.id, db)

    # Se checa existen preguntas asignadas al deck, o sea que haya registros en la tabla user assignments con relacion al deck
    assigned_questions = questions_assigned_to_deck_service(deck.id,user_id, db)

    if not assigned_questions:
        #Si no existen, entonces buscamos si ya hay preguntas del prompt
        questions = get_questions_from_a_prompt_service(prompt_id=prompt.id, db=db)
        #Si existen preguntas ya, entonces asignamos 10 al usuario
        if not questions:
            # Generamos las preguntas y se las asignamos al usuario
            questions = generate_and_save_new_questions_services(prompt.text, prompt.id, db)

        # Asignamos las preguntas
        assigned_questions = set_questions_assigned_to_deck_service(user_id=user_id,prompt_id=prompt.id, deck_id=deck.id,questions=questions,db=db)

    ## Mandamos la primera pregunta del user_assignement
    return get_first_assigned_question_service(user_id=user_id, deck_id=deck.id,db=db)


@user_assignment_router.post('/answer_question')
def answer_question(question_assigned: int = Query(...), option_selected_id: int = Query(...), db: Session = Depends(get_db_session)):
    assignment_question = get_user_question_assignment_service(question_assigned, db)
    assignment_question.selected_option_id = option_selected_id
    if not assignment_question:
        raise HTTPException(status_code=404, detail='Assignment not found')

    correct_option = get_correct_option_service(assignment_question.question_id, db)
    is_correct = correct_option.id == option_selected_id
    difficulty_question = assignment_question.question.difficulty
    schedule_review(assignment_question, is_correct,difficulty_question)
    db.commit()

    return {'message': 'Answer submitted', 'correct': is_correct, 'selected_option': option_selected_id}

@user_assignment_router.post('/next-question')
def next_question(deck_id: int = Query(...), user_id: str = Query(...), db: Session = Depends(get_db_session)):
    today = datetime.datetime.now().date() - datetime.timedelta(days=1)
    user_level = calculate_user_level(user_id, deck_id, db)
    # Obtener todas las asignaciones de preguntas para el deck
    assignments = get_all_question_assignments_service(deck_id, db)
    # Filtrar las asignaciones que no se han presentado hoy
    available_assignments = [
        assignment for assignment in assignments
    ]
    if not available_assignments:
        # Si todas las preguntas se han presentado hoy, buscar nuevas preguntas o generar nuevas
        unassigned_questions = get_unassigned_questions_for_user_service(deck_id, db)

        if not unassigned_questions:
            deck = get_deck_service(deck_id, db)

            available_assignments = generate_new_questions(user_id=user_id,prompt_id=deck.prompt_id,db=db)
    
    if not available_assignments:
        # A qui lo que se haría sería generar preguntas nuevas o tal vez repetir
        raise HTTPException(status_code=404, detail='No questions available for today's session')

    next_assignment = min(
        available_assignments,
        key=lambda a: (
            abs(a.question.difficulty - user_level), 
            a.interval,  
            random.random() 
        )
    )
    db.commit()

    return UserAssignmentResult.model_validate(next_assignment)


@user_assignment_router.post('/new-questions')
def generate_new_questions_route(
    user_id: str = Query(...),
    prompt_id: int = Query(...),
    db: Session = Depends(get_db_session)
):
    # Verificar si el deck existe
    deck = get_deck_by_prompt_service(user_id, prompt_id, db)
    if not deck:
        raise HTTPException(status_code=404, detail='Deck not found for this user and prompt')

    # Obtener el prompt
    prompt = get_prompt(prompt_id, db)
    if not prompt:
        raise HTTPException(status_code=404, detail='Prompt not found')

    # Generar nuevas preguntas
    questions = generate_and_save_new_questions_services(prompt.text, prompt.id, db)
    print(len(questions))
    if not questions:
        raise HTTPException(status_code=500, detail='Failed to generate new questions')

    # Asignar las nuevas preguntas al usuario
    assigned_questions = set_questions_assigned_to_deck_service(
        user_id=user_id,
        prompt_id=prompt.id,
        deck_id=deck.id,
        questions=questions,
        db=db
    )

    # Preparar la respuesta
    response = {
        'message': 'New questions generated and assigned successfully',
        'num_questions_generated': len(questions),
        'num_questions_assigned': len(assigned_questions) if assigned_questions else 0,
        'deck_id': deck.id,
        'prompt_id': prompt.id
    }

    return response

def generate_new_questions(
    user_id: str ,
    prompt_id: int ,
    db: Session
):
    
    # @TODO: Get the user level and request questions with thad difficult level
    # Verificar si el deck existe
    deck = get_deck_by_prompt_service(user_id, prompt_id, db)
    if not deck:
        raise HTTPException(status_code=404, detail='Deck not found for this user and prompt')

    # Obtener el prompt
    prompt = get_prompt(prompt_id, db)
    if not prompt:
        raise HTTPException(status_code=404, detail='Prompt not found')

    # Generar nuevas preguntas
    questions = generate_and_save_new_questions_services(prompt.text, prompt.id, db)
    print(len(questions))
    if not questions:
        raise HTTPException(status_code=500, detail='Failed to generate new questions')

    # Asignar las nuevas preguntas al usuario
    assigned_questions = set_questions_assigned_to_deck_service(
        user_id=user_id,
        prompt_id=prompt.id,
        deck_id=deck.id,
        questions=questions,
        db=db
    )

    return assigned_questions

