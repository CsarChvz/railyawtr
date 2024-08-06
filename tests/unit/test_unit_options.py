import logging
import os

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.models import Option, Prompt, Question, User
from tests.factories.models_factory import (
    get_random_option_dict,
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


@pytest.fixture(scope='function', autouse=True)
def set_test_env():
    os.environ['TESTING'] = '1'
    yield
    os.environ.pop('TESTING', None)


def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value


'''
- [X] Test GET options for question successfully
'''


def test_unit_get_options_for_question_successfully(
    client: TestClient, test_question: Question, monkeypatch
):
    option_data = get_random_option_dict(question_id=test_question.id)
    option_instance = Option(**option_data)

    monkeypatch.setattr(
        'sqlalchemy.orm.Query.filter_by', mock_output([option_instance])
    )
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_output([option_instance]))

    response = client.get(f'{prefix}/options/question/{test_question.id}/options')
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]['id'] == option_instance.id
    assert response_json[0]['question_id'] == option_instance.question_id
    assert response_json[0]['option_text'] == option_instance.option_text


'''
- [X] Test GET options for question not found
'''


def test_unit_get_options_for_question_not_found(client: TestClient, monkeypatch):
    monkeypatch.setattr('sqlalchemy.orm.Query.filter_by', mock_output([]))
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_output([]))

    response = client.get(f'{prefix}/options/question/1/options')
    assert response.status_code == 200
    assert response.json() == []


'''
- [X] Test GET options for question internal server error
'''


def test_unit_get_options_for_question_internal_error(client: TestClient, monkeypatch):
    def mock_get_options_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.filter_by', mock_get_options_exception)
    monkeypatch.setattr('sqlalchemy.orm.Query.all', mock_get_options_exception)

    response = client.get(f'{prefix}/options/question/1/options')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [ ] Test CREATE option for question successfully
'''


# def test_unit_create_prompt_successfully(
#     client: TestClient, test_question: User, monkeypatch
# ):
#     option_dict = get_random_option_dict(question_id=test_question.id)

#     option_instance = Option(**option_dict)
#     for key, value in option_dict.items():
#         monkeypatch.setattr(Option, key, value)

#     monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(option_instance))
#     monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
#     monkeypatch.setattr('sqlalchemy.orm.Session.refresh', mock_output())

#     response = client.post(f'api/options/question/{test_question.id}/options')
#     print(response.json())
#     assert response.status_code == 201


'''
- [X] Test CREATE option for question internal server error
'''


def test_unit_create_option_for_question_internal_error(
    client: TestClient, test_question: Question, monkeypatch
):
    def mock_create_option_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr(
        'app.services.create_option_for_question_service', mock_create_option_exception
    )

    response = client.post(f'{prefix}/options/question/{test_question.id}/options')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [X] Test UPDATE option successfully
'''


def test_unit_update_option_successfully(
    client: TestClient, test_question: Question, monkeypatch
):
    option_dict = get_random_option_dict(question_id=test_question.id)
    option_instance = Option(**option_dict)

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(option_instance))
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.refresh', mock_output())

    body = {'option_text': 'Updated prompt text'}

    response = client.put(f'{prefix}/options/option/{option_instance.id}', json=body)

    assert response.status_code == 201

    expected_response = {
        'id': option_instance.id,
        'option_text': body['option_text'],
        'question_id': option_instance.question_id,
    }

    assert response.json() == expected_response


'''
- [X] Test UPDATE option not found
'''


def test_unit_update_option_not_found(client: TestClient, monkeypatch, test_question):
    option_dict = get_random_option_dict(question_id=test_question.id)
    option_instance = Option(**option_dict)
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.refresh', mock_output())

    body = {'option_text': 'Updated prompt text'}
    response = client.put(f'{prefix}/options/option/{option_instance.id}', json=body)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Option not found'}


'''
- [X] Test UPDATE option internal server error
'''


def test_unit_update_option_internal_error(
    client: TestClient, monkeypatch, test_question
):
    option_dict = get_random_option_dict(question_id=test_question.id)
    option_instance = Option(**option_dict)

    def mock_create_option_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_create_option_exception)

    body = {'option_text': 'Updated prompt text'}
    response = client.put(f'{prefix}/options/option/{option_instance.id}', json=body)
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [X] Test DELETE option successfully
'''


def test_unit_delete_option_successfully(
    client: TestClient, monkeypatch, test_question
):
    option_dict = get_random_option_dict(question_id=test_question.id)
    option_instance = Option(**option_dict)
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(option_instance))
    monkeypatch.setattr('sqlalchemy.orm.Session.delete', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())

    response = client.delete(f'{prefix}/options/option/{option_instance.id}')
    assert response.status_code == 201


'''
- [X] Test DELETE option not found
'''


def test_unit_delete_option_not_found(
    client: TestClient, monkeypatch, test_question: Question
):
    option = []
    option_dict = get_random_option_dict(question_id=test_question.id)
    option_instance = Option(**option_dict)
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(option))
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    response = client.delete(f'{prefix}/options/option/{option_instance.id}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Option not found'}


'''
- [X] Test DELETE option internal server error
'''


def test_unit_delete_option_internal_error(
    client: TestClient, monkeypatch, test_question: Question
):
    def mock_delete_option_exception(*args, **kwargs):
        raise Exception('Internal server error')

    option_dict = get_random_option_dict(question_id=test_question.id)
    option_instance = Option(**option_dict)
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_delete_option_exception)
    response = client.delete(f'{prefix}/options/option/{option_instance.id}')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}
