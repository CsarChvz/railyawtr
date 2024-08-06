import logging
import os

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.models import Prompt, Question, User
from tests.factories.models_factory import (
    get_random_prompt_dict,
    get_random_question_dict,
    get_random_user_dict,
)

# Configura el logger
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
prefix = '/api/v1'

@pytest.fixture(scope='function')
def db_session_cleanup(db_session: Session):
    yield db_session
    db_session.rollback()


@pytest.fixture(scope='function')
def test_user(db_session_cleanup: Session):
    user_data = get_random_user_dict()
    user = User(**user_data)
    db_session_cleanup.add(user)
    db_session_cleanup.commit()
    db_session_cleanup.refresh(user)
    yield user
    db_session_cleanup.query(Question).filter(Question.user_id == user.id).delete()
    db_session_cleanup.delete(user)
    db_session_cleanup.commit()


@pytest.fixture(scope='function')
def test_prompt(db_session_cleanup: Session, test_user: User):
    prompt_data = get_random_prompt_dict(user_id=test_user.id)
    prompt = Prompt(**prompt_data)
    db_session_cleanup.add(prompt)
    db_session_cleanup.commit()
    db_session_cleanup.refresh(prompt)
    yield prompt
    db_session_cleanup.query(Question).filter(Question.prompt_id == prompt.id).delete()
    db_session_cleanup.delete(prompt)
    db_session_cleanup.commit()


@pytest.fixture(scope='function')
def test_question(db_session_cleanup: Session, test_prompt: Prompt, test_user: User):
    question_data = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )
    question = Question(**question_data)
    db_session_cleanup.add(question)
    db_session_cleanup.commit()
    db_session_cleanup.refresh(question)
    yield question
    db_session_cleanup.delete(question)
    db_session_cleanup.commit()


@pytest.fixture(scope='function', autouse=True)
def set_test_env():
    os.environ['TESTING'] = '1'
    yield
    os.environ.pop('TESTING', None)


def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value

'''
- [ ] Test CREATE question from a prompt successfully
'''


# def test_unit_create_question_from_prompt_successfully(
#     client: TestClient,
#     test_user: User,
#     test_prompt: Prompt,
#     monkeypatch,
# ):
#     question_data = get_random_question_dict(
#         prompt_id=test_prompt.id, user_id=test_user.id
#     )
#     question_instance = Question(**question_data)

#     # Mock SQLAlchemy query and session methods
#     monkeypatch.setattr('sqlalchemy.orm.Session.add', mock_output())
#     monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
#     monkeypatch.setattr(
#         'sqlalchemy.orm.Session.refresh', mock_output(question_instance)
#     )
#     monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(question_instance))

#     body = {
#         'user_id': question_data['user_id'],
#     }

#     response = client.post(f'/api/questions/prompt/{test_prompt.id}', json=body)

#     print(response.json())
#     assert response.status_code == 201

#     response_json = response.json()
#     assert response_json['user_id'] == question_instance.user_id
#     assert response_json['prompt_id'] == question_instance.prompt_id
#     assert response_json['question_text'] == question_instance.question_text


'''
- [X] Test CREATE question internal server error
'''


def test_unit_create_question_internal_server_error(
    client: TestClient, test_user: User, test_prompt: Prompt, monkeypatch
):
    question_data = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )

    def mock_create_question_exception(*args, **kwargs):
        raise Exception('Internal server error')

    for key, value in question_data.items():
        monkeypatch.setattr(Question, key, value)

    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_create_question_exception)
    monkeypatch.setattr('sqlalchemy.orm.Session.refresh', mock_output())
    question_data.pop('id')
    question_data.pop('created_at')

    response = client.post(
        f'{prefix}/questions/prompt/{test_prompt.id}', json=question_data
    )
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [X] Test GET questions from a prompt successfully
'''


def test_unit_get_questions_from_prompt_successfully(
    client: TestClient, monkeypatch, test_prompt: Prompt, test_user: User
):
    questions = [
        get_random_question_dict(prompt_id=test_prompt.id, user_id=test_user.id)
        for _ in range(3)
    ]
    question_objs = [Question(**question) for question in questions]

    monkeypatch.setattr('sqlalchemy.orm.Query.filter_by', mock_output(question_objs))
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_output(question_objs))

    response = client.get(f'{prefix}/questions/prompt/{test_prompt.id}')
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json) == len(question_objs)


'''
- [X] Test GET questions from a prompt internal server error
'''


def test_unit_get_questions_from_prompt_internal_error(
    client: TestClient, monkeypatch, test_prompt: Prompt
):
    def mock_internal_server_error(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.filter_by', mock_internal_server_error)
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_internal_server_error)

    response = client.get(f'{prefix}/questions/prompt/{test_prompt.id}')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [X] Test GET questions from a prompt - no questions available
'''


def test_unit_get_questions_from_prompt_no_questions_available(
    client: TestClient, monkeypatch, test_prompt: Prompt
):
    monkeypatch.setattr('sqlalchemy.orm.Query.filter_by', mock_output([]))
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_output([]))

    response = client.get(f'{prefix}/questions/prompt/{test_prompt.id}')
    assert response.status_code == 200
    assert response.json() == []


'''
- [X-f] Test GET random question successfully
'''
def test_unit_get_random_question_successfully(
    client: TestClient,
    test_question: Question,
    monkeypatch,
):
    monkeypatch.setattr(
        'app.services.get_random_question_service', mock_output(test_question)
    )

    response = client.get(f'{prefix}/questions/random-question')

    assert response.status_code == 201


'''
- [X] Test GET a random question - no questions available
'''


def test_unit_get_random_question_no_questions_available(
    client: TestClient, monkeypatch
):
    # Mockear la consulta para devolver una lista vacía
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(None))
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_output(None))
    # Realizar la solicitud GET para obtener una pregunta aleatoria
    response = client.get(f'{prefix}/questions/random-question')

    # Verificar que el estado de la respuesta sea 404 y el mensaje de error sea correcto
    assert response.status_code == 404
    response_json = response.json()
    assert response_json == {'detail': 'No questions available'}


'''
- [X] Test GET single question 
'''


def test_unit_get_single_question_successfully(
    client: TestClient, monkeypatch, test_prompt, test_user
):
    question_dict = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(question_dict))

    response = client.get(f'{prefix}/questions/{question_dict['id']}')
    assert response.status_code == 201
    assert response.json() == question_dict


'''
- [X] Test GET single question not found
'''


def test_unit_get_single_question_not_found(
    client: TestClient, monkeypatch, test_prompt, test_user
):
    question_dict = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )

    # Mock the SQLAlchemy query to return None
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(None))

    response = client.get(f'{prefix}/questions/{question_dict['id']}')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Question not found'}


'''
- [X] Test GET single question internal server error
'''


def test_unit_get_single_question_internal_server_error(
    client: TestClient, monkeypatch, test_prompt, test_user
):
    question_dict = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )

    def mock_create_question_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_create_question_exception)

    response = client.get(f'{prefix}/questions/{question_dict['id']}')

    assert response.status_code == 500


'''
- [X] Test DELETE question user successfully
'''


def test_unit_delete_prompt_successfully(
    client: TestClient, monkeypatch, test_user, test_prompt
):
    question_dic = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )
    question_instance = Question(**question_dic)

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(question_instance))
    monkeypatch.setattr('sqlalchemy.orm.Session.delete', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())

    response = client.delete(f'{prefix}/questions/{question_instance.id}')
    assert response.status_code == 201


'''
- [X] Test DELETE prompt not found
'''


def test_unit_delete_prompt_not_found(
    client: TestClient, monkeypatch, test_user, test_prompt
):
    question = []
    question_dic = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(question))
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    response = client.delete(f'{prefix}/questions/{question_dic['id']}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Question not found'}


'''
- [X] Test DELETE question internal server error
'''


def test_unit_delete_question_internal_error(
    client: TestClient, monkeypatch, test_user, test_prompt
):
    question_dic = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )

    def mock_delete_question_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_delete_question_exception)
    response = client.delete(f'{prefix}/questions/{question_dic['id']}')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [X] Test UPDATE question successfully
'''


def test_unit_update_question_successfully(
    client: TestClient, monkeypatch, test_user, test_prompt
):
    question_dic = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )
    question_instance = Question(**question_dic)

    # Mock SQLAlchemy methods
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(question_instance))
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.refresh', mock_output())

    response = client.put(
        f'{prefix}/questions/{question_instance.id}',
        json={'question_text': question_instance.question_text},
    )
    assert response.status_code == 201
    assert response.json() == question_dic


'''
- [X] Test UPDATE question not found
'''


def test_unit_update_question_not_found(
    client: TestClient, monkeypatch, test_user, test_prompt
):
    question_dic = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )
    question_instance = Question(**question_dic)
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.refresh', mock_output())
    response = client.put(
        f'{prefix}/questions/{question_instance.id}',
        json={'question_text': question_instance.question_text},
    )
    assert response.status_code == 404
    assert response.json() == {'detail': 'Question not found'}


'''
- [X] Test UPDATE question internal server error
'''


def test_unit_update_question_internal_error(
    client: TestClient, monkeypatch, test_user, test_prompt
):
    question_dic = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )
    question_instance = Question(**question_dic)

    def mock_create_user_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_create_user_exception)

    body = question_dic.copy()
    body.pop('id')
    body.pop('created_at')
    response = client.put(f'{prefix}/prompts/{question_instance.id}', json=body)
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}
