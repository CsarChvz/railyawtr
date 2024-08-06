import pytest
from sqlalchemy import inspect


@pytest.fixture(scope="function")
def db_inspector(db_session_factory):
    return inspect(db_session_factory().bind)