import pytest
from starlette.testclient import TestClient

from app.models import User
from tests.factories.models_factory import get_random_user_dict


def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value
prefix = '/api/v1'

'''
- [X] Test DELETE user successfully
'''


def test_unit_delete_user_successfully(client: TestClient, monkeypatch):
    user_dict = get_random_user_dict()
    user_instance = User(**user_dict)

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(user_instance))
    monkeypatch.setattr('sqlalchemy.orm.Session.delete', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())

    response = client.delete(f'{prefix}/user/{user_instance.id}')
    assert response.status_code == 200


'''
- [X] Test DELETE user not found
'''


def test_unit_delete_user_not_found(client: TestClient, monkeypatch):
    user = []
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(user))
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    response = client.delete(f'{prefix}/user/1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


'''
- [X] Test DELETE user internal server error
'''


def test_unit_delete_user_internal_error(client: TestClient, monkeypatch):
    def mock_create_user_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_create_user_exception)
    response = client.delete(f'{prefix}/user/1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [X] Test UPDATE user not found
'''


def test_unit_update_user_not_found(client: TestClient, monkeypatch):
    user_dict = get_random_user_dict()
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.refresh', mock_output())

    body = user_dict.copy()
    body.pop('id')

    response = client.put(f'{prefix}/user/1', json=body)
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


'''
- [X] Test UPDATE user internal server error
'''


def test_unit_update_user_internal_error(client: TestClient, monkeypatch):
    user_dict = get_random_user_dict()

    def mock_create_user_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_create_user_exception)

    body = user_dict.copy()
    body.pop('id')
    response = client.put(f'{prefix}/user/1', json=body)
    assert response.status_code == 500
    assert response.json() == {'detail': 'Internal server error'}


'''
- [X] Test GET single user by id successfully
'''


@pytest.mark.parametrize('user', [get_random_user_dict() for _ in range(3)])
def test_unit_get_single_user_successfully(client: TestClient, monkeypatch, user):
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(user))
    response = client.get(f'{prefix}/user/{user['id']}')
    assert response.status_code == 200
    assert response.json() == user


'''
- [X] Test GET single user id not found
'''


@pytest.mark.parametrize('user', [get_random_user_dict() for _ in range(3)])
def test_unit_get_single_user_not_found(client: TestClient, monkeypatch, user):
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output())
    response = client.get(f'{prefix}/user/{user['id']}')
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


'''
- [X] Test GET single user by slug internal server error
'''


@pytest.mark.parametrize('user', [get_random_user_dict() for _ in range(3)])
def test_unit_get_single_user_with_internal_server_error(client, monkeypatch, user):
    def mock_create_user_exception(*args, **kwargs):
        raise Exception('Internal server error')

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_create_user_exception)
    response = client.get(f'{prefix}/user/{user['id']}')
    assert response.status_code == 500


'''
- [X] Test POST new user successfully
'''


def test_unit_create_new_user_successfully(client: TestClient, monkeypatch):
    user = get_random_user_dict()

    for key, value   in user.items():
        monkeypatch.setattr(User, key, value)

    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.refresh', mock_output())

    body = user.copy()
    response = client.post(f'{prefix}/user/', json=body)
    assert response.status_code == 201
    assert response.json() == user


'''
- [X] Test POST user exists
'''



def test_unit_post_user_exists(client: TestClient, monkeypatch):
    user_data = get_random_user_dict()
    existing_user = User(**user_data)

    # Mock the database query to return an existing user, simulating a user that already exists
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output(existing_user))

    body = user_data.copy()
    response = client.post(f'{prefix}/user/', json=body)

    assert response.status_code == 400
    assert response.json() == {'detail': 'User already exists with this id'}


'''
- [X] Test POST user db server issue
'''


def test_unit_create_new_user_with_internal_server_error(
    client: TestClient, monkeypatch
):
    category = get_random_user_dict()

    # Mock an exception to simulate an internal server error
    def mock_create_user_exception(*args, **kwargs):
        raise Exception('Internal server error')

    for key, value in category.items():
        monkeypatch.setattr(User, key, value)
    monkeypatch.setattr('sqlalchemy.orm.Query.first', mock_output())
    monkeypatch.setattr('sqlalchemy.orm.Session.commit', mock_create_user_exception)

    body = category.copy()
    response = client.post(f'{prefix}/user/', json=body)
    assert response.status_code == 500

