import logging
import os

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.models import Prompt, User
from tests.factories.models_factory import get_random_prompt_dict, get_random_user_dict

# Configura el logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

prefix = "/api/v1"
@pytest.fixture(scope="function")
def test_user(db_session: Session):
    user_data = get_random_user_dict()
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.delete(user)
    db_session.commit()


@pytest.fixture(scope="function", autouse=True)
def set_test_env():
    os.environ["TESTING"] = "1"
    yield
    os.environ.pop("TESTING", None)


def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value


"""
- [X] Test CREATE prompt successfully
"""


def test_unit_create_prompt_successfully(
    client: TestClient, test_user: User, monkeypatch
):
    logger.info("Starting test for creating prompt successfully")
    prompt_data = get_random_prompt_dict(user_id=test_user.id)

    for key, value in prompt_data.items():
        monkeypatch.setattr(Prompt, key, value)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())
    prompt_data.pop("id")
    prompt_data.pop("created_at")
    logger.info(f"Prompt data: {prompt_data}")

    response = client.post(f"{prefix}/prompts/", json=prompt_data)
    assert response.status_code == 200

    response_json = response.json()
    logger.info(f"Response JSON: {response_json}")

    assert response_json["id"] is not None
    assert response_json["created_at"] is not None
    assert response_json["text"] == prompt_data["text"]
    assert response_json["user_id"] == test_user.id


"""
- [X] Test CREATE prompt internal server error
"""


def test_unit_create_prompt_internal_error(
    client: TestClient, monkeypatch, test_user: User
):
    prompt_data = get_random_prompt_dict(user_id=test_user.id)

    def mock_create_prompt_exception(*args, **kwargs):
        raise Exception("Internal server error")

    for key, value in prompt_data.items():
        monkeypatch.setattr(Prompt, key, value)

    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_create_prompt_exception)
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    prompt_data.pop("id")
    prompt_data.pop("created_at")

    response = client.post(f"{prefix}/prompts/", json=prompt_data)

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}

    monkeypatch.undo()


"""
- [X] Test DELETE prompt user successfully
"""


def test_unit_delete_prompt_successfully(client: TestClient, monkeypatch, test_user):
    prompt_dic = get_random_prompt_dict(user_id=test_user.id)
    prompt_instance = Prompt(**prompt_dic)

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(prompt_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.delete", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())

    response = client.delete(f"{prefix}/prompts/{prompt_instance.id}")
    assert response.status_code == 201


"""
- [X] Test DELETE prompt not found
"""


def test_unit_delete_prompt_not_found(client: TestClient, monkeypatch):
    prompt = []
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(prompt))
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    response = client.delete(f"{prefix}/prompts/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Prompt not found"}


"""
- [X] Test DELETE prompt internal server error
"""


def test_unit_delete_prompt_internal_error(client: TestClient, monkeypatch):
    def mock_delete_prompt_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_delete_prompt_exception)
    response = client.delete(f"{prefix}/prompts/1")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


"""
- [X] Test UPDATE prompt user successfully
"""


def test_unit_update_prompt_successfully(
    client: TestClient, monkeypatch, test_user: User
):
    # Create a prompt instance
    prompt_dict = get_random_prompt_dict(user_id=test_user.id)
    prompt_instance = Prompt(**prompt_dict)

    # Mock SQLAlchemy methods
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(prompt_instance))
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    body = {"text": "Updated prompt text"}

    response = client.put(f"{prefix}/prompts/{prompt_instance.id}", json=body)

    assert response.status_code == 201

    expected_response = {
        "id": prompt_instance.id,
        "created_at": prompt_instance.created_at.format(),
        "text": body["text"],
        "user_id": prompt_instance.user_id,
    }

    assert response.json() == expected_response


"""
- [X] Test UPDATE prompt not found
"""


def test_unit_update_prompt_not_found(
    client: TestClient, monkeypatch, test_user
):  # Create a prompt instance
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    body = {"text": "Updated prompt text"}
    response = client.put(f"{prefix}/prompts/1", json=body)
    assert response.status_code == 404
    assert response.json() == {"detail": "Prompt not found"}


"""
- [X] Test UPDATE prompt internal server error
"""


def test_unit_update_prompt_internal_error(client: TestClient, monkeypatch, test_user):
    prompt_dict = get_random_prompt_dict(user_id=test_user.id)

    def mock_create_user_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_create_user_exception)

    body = prompt_dict.copy()
    body.pop("id")
    body.pop("created_at")
    response = client.put(f"{prefix}/prompts/1", json=body)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


"""
- [X] Test GET prompts by user id successfully
"""


def test_unit_get_prompts_by_user_id_successfully(
    client: TestClient, monkeypatch, test_user: User, db_session: Session
):
    # Crear múltiples prompts para el usuario
    prompts = [get_random_prompt_dict(user_id=test_user.id) for _ in range(3)]
    prompt_objs = [Prompt(**prompt) for prompt in prompts]
    db_session.bulk_save_objects(prompt_objs)
    db_session.commit()

    # Mock SQLAlchemy methods
    monkeypatch.setattr("sqlalchemy.orm.Query.filter_by", mock_output(prompt_objs))
    monkeypatch.setattr("sqlalchemy.orm.Query.all", mock_output(prompt_objs))
    monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

    response = client.get(f"{prefix}/prompts/user/{test_user.id}")
    assert response.status_code == 200

    response_json = response.json()

    assert len(response_json) == len(prompt_objs)
    for prompt in response_json:
        assert prompt["user_id"] == test_user.id



"""
- [X] Test GET user prompts user not found
"""
def test_unit_get_user_prompts_user_not_found(client: TestClient, monkeypatch):
    user_id = "non_existent_user_id"
    prompts = []

    # Mock the database query to simulate that the user does not exist
    monkeypatch.setattr(
        "sqlalchemy.orm.Query.filter_by", lambda *args, **kwargs: mock_output(prompts)
    )
    monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output(None))

    response = client.get(f"{prefix}/prompts/user/{user_id}")
    assert response.json() == []


"""
- [X-f] Test GET prompts by user id internal server error
"""


def test_unit_get_prompts_by_user_id_internal_error(
    client: TestClient, monkeypatch, test_user: User
):
    def mock_create_prompt_exception(*args, **kwargs):
        raise Exception("Internal server error")

    monkeypatch.setattr("sqlalchemy.orm.Query.filter_by", mock_create_prompt_exception)
    monkeypatch.setattr("sqlalchemy.orm.Query.all", mock_create_prompt_exception)

    response = client.get(f"{prefix}/prompts/user/{test_user.id}")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
