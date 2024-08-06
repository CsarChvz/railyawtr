import logging
import os

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.models import Option, Prompt, Question, User, UserResponse
from tests.factories.models_factory import (
    get_random_option_dict,
    get_random_prompt_dict,
    get_random_question_dict,
    get_random_user_dict,
    get_random_user_response_dict,
)

# Configura el logger
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
prefix = '/api/v1'

@pytest.fixture(scope='function')
def test_user(db_session: Session):
    user_data = get_random_user_dict()
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.query(Question).filter(Question.user_id == user.id).delete()
    db_session.delete(user)
    db_session.commit()


@pytest.fixture(scope='function')
def test_prompt(db_session: Session, test_user: User):
    prompt_data = get_random_prompt_dict(user_id=test_user.id)
    prompt = Prompt(**prompt_data)
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)
    yield prompt
    db_session.query(Question).filter(Question.prompt_id == prompt.id).delete()
    db_session.delete(prompt)
    db_session.commit()


@pytest.fixture(scope='function')
def test_question(db_session: Session, test_prompt: Prompt, test_user: User):
    question_data = get_random_question_dict(
        prompt_id=test_prompt.id, user_id=test_user.id
    )
    question = Question(**question_data)
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    yield question
    db_session.delete(question)
    db_session.commit()


@pytest.fixture(scope='function')
def test_option(db_session: Session, test_question: Question):
    option_data = get_random_option_dict(question_id=test_question.id)
    option = Option(**option_data)
    db_session.add(option)
    db_session.commit()
    db_session.refresh(option)
    yield option
    db_session.delete(option)
    db_session.commit()


@pytest.fixture(scope='function')
def test_user_response(
    db_session: Session, test_question: Question, test_user: User, test_option: Option
):
    user_response_data = get_random_user_response_dict(
        question_id=test_question.id,
        user_id=test_user.id,
        selected_option_id=test_option.id,
    )
    user_response = UserResponse(**user_response_data)
    db_session.add(user_response)
    db_session.commit()
    db_session.refresh(user_response)
    yield user_response
    db_session.delete(user_response)
    db_session.commit()


@pytest.fixture(scope='function', autouse=True)
def set_test_env():
    os.environ['TESTING'] = '1'
    yield
    os.environ.pop('TESTING', None)


def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value


'''
- [X] Test CREATE user response successfully
'''

def test_unit_create_user_response_successfully(
    client: TestClient,
    test_question: Question,
    test_user: User,
    test_option: Option,
    monkeypatch,
):
    user_response_data = get_random_user_response_dict(
        question_id=test_question.id,
        user_id=test_user.id,
        selected_option_id=test_option.id,
    )
    user_response_instance = UserResponse(**user_response_data)

    for key, value in user_response_data.items():
        monkeypatch.setattr(UserResponse, key, value)

    monkeypatch.setattr(
        'sqlalchemy.orm.Query.first', mock_output(user_response_instance)
    )
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.refresh', mock_output())
    body = user_response_data.copy()

    body.pop('id')
    body.pop('created_at')
    response = client.post(
        f'{prefix}/responses/question/{test_question.id}/response', json=body
    )
    assert response.status_code == 201

    response_json = response.json()
    assert response_json['id'] is not None
    assert response_json['question_id'] == user_response_instance.question_id
    assert response_json['user_id'] == user_response_instance.user_id
    assert (
        response_json['selected_option_id'] == user_response_instance.selected_option_id
    )


'''
- [X] Test CREATE user response internal server error
'''
def test_unit_delete_category_internal_error(
    client: TestClient,
    test_question: Question,
    test_user: User,
    test_option: Option,
    monkeypatch,
):
    user_response_data = get_random_user_response_dict(
        question_id=test_question.id,
        user_id=test_user.id,
        selected_option_id=test_option.id,
    )

    def mock_create_category_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_create_category_exception)
    body = user_response_data.copy()

    body.pop('id')
    body.pop('created_at')
    response = client.post(
        f'{prefix}/responses/question/{test_question.id}/response', json=body
    )
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [X] Test GET responses for question successfully
'''


def test_unit_get_responses_for_question_successfully(
    client: TestClient,
    test_question: Question,
    test_user_response: UserResponse,
    monkeypatch,
):
    monkeypatch.setattr(
        'sqlalchemy.orm.Query.filter_by', mock_output([test_user_response])
    )
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_output([test_user_response]))

    response = client.get(f'{prefix}/responses/question/{test_question.id}/responses')
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]['id'] == test_user_response.id
    assert response_json[0]['question_id'] == test_user_response.question_id
    assert response_json[0]['user_id'] == test_user_response.user_id
    assert (
        response_json[0]['selected_option_id'] == test_user_response.selected_option_id
    )


'''
- [X] Test GET responses for question not found
'''


def test_unit_get_responses_for_question_not_found(client: TestClient, monkeypatch):
    monkeypatch.setattr('sqlalchemy.orm.Query.filter_by', mock_output([]))
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_output([]))

    response = client.get(f'{prefix}/responses/question/1/responses')
    assert response.status_code == 200
    assert response.json() == []


'''
- [X] Test GET responses for question internal server error
'''


def test_unit_get_responses_for_question_internal_error(
    client: TestClient, monkeypatch
):
    def mock_get_responses_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.filter_by', mock_get_responses_exception)
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_get_responses_exception)

    response = client.get(f'{prefix}/responses/question/1/responses')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [X] Test DELETE user response successfully
'''


def test_unit_delete_user_response_successfully(
    client: TestClient, test_user_response: UserResponse, monkeypatch
):
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(test_user_response))
    monkeypatch.setattr('sqlalchemy.orm.Session.delete', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())

    response = client.delete(f'{prefix}/responses/response/{test_user_response.id}')
    assert response.status_code == 200


'''
- [X] Test DELETE user response not found
'''


def test_unit_delete_user_response_not_found(
    client: TestClient, monkeypatch, test_question: Question
):
    user_response = []
    user_response_data = get_random_user_response_dict(
        question_id=test_question.id, user_id='USR1', selected_option_id=1
    )
    user_response_instance = UserResponse(**user_response_data)
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(user_response))
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    response = client.delete(f'{prefix}/responses/response/{user_response_instance.id}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'User response not found'}


'''
- [X] Test DELETE user response internal server error
'''


def test_unit_delete_user_response_internal_error(
    client: TestClient, test_user_response: UserResponse, monkeypatch
):
    def mock_delete_user_response_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr(
        'sqlalchemy.orm.Query.first', mock_delete_user_response_exception
    )
    response = client.delete(f'{prefix}/responses/response/{test_user_response.id}')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}
