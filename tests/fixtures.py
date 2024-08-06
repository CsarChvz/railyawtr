import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.main import app
from tests.utils.database_utils import migrate_to_db
from tests.utils.docker_utils import start_database_container


@pytest.fixture(scope="session", autouse=True)
def db_engine():
    container = start_database_container()

    engine = create_engine(os.getenv("TEST_DATABASE_URL"))

    with engine.begin() as connection:
        migrate_to_db("migrations", "alembic.ini", connection)

    yield engine

    container.stop()
    container.remove()
    engine.dispose()


@pytest.fixture(scope="session")
def db_session_factory(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=db_engine)
    return SessionLocal


@pytest.fixture(scope="function")
def db_session(db_session_factory):
    db = db_session_factory()
    yield db
    # db.close()


@pytest.fixture(scope="function")
def client_test():
    with TestClient(app) as _client_test:
        yield _client_test


@pytest.fixture(scope="function")
def client(client_test):
    client_test.cookies.set(
        "session",
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNUWnNHTjhWUkRkaElaMkllN0w0aCJ9.eyJpc3MiOiJodHRwczovL2Zhc3QtYXBpLWV4LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2NjQwMDIyNTAzOTk2YzQyNzE0YTJkOTAiLCJhdWQiOlsiaHR0cHM6Ly9mYXN0YXBpLmV4YW1wbGUuY29tIiwiaHR0cHM6Ly9mYXN0LWFwaS1leC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzE3MDA0MzMyLCJleHAiOjE3MTcwOTA3MzIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgYWRkcmVzcyBwaG9uZSIsImd0eSI6InBhc3N3b3JkIiwiYXpwIjoieWJXS1NIcmxaUkpieEtqbVJWMjI3MzRmOEViQmgxV3IiLCJwZXJtaXNzaW9ucyI6WyJjcnVkOmFkbWluLWNyZWF0ZS11c2VyIiwiY3J1ZDphZG1pbi1kZWxldGUtdXNlciIsImNydWQ6YWRtaW4tZ2V0LXVzZXIiLCJjcnVkOmFkbWluLXF1ZXN0aW9ucyIsImNydWQ6YWRtaW4tdXBkYXRlLXVzZXIiLCJyZWFkLWRlbGV0ZTphZG1pbi1yZXNwb25zZXMiXX0.tnkWQPHhH26-aZQ0IrBPW8lHL6CEyvUn9suLxR6uRpF_MsW1pN5QEcU70aTPL4PKzk39jzYDo3GkUYM0Bzr1SP-mgEbtGUSBtnIHJThUztzXmz62nGTM-Lu9BD8z29XaYHXMtwwYJgpxgYrXUIj2ap_bk_vqmbUh41IBy21xJTgg_8xG3WcjcfNPrFvIX_CZiL8tl9sXDa0EYHFwDXd2Qe0kqtWVFdJ7yb64l6UI4nmEI9CJ9ezZfoKr968ppFVj_n-lfrsRcPJntDNp-mtEne_pRHq_K0VS7UECHPAD0FNDZvorL1RlyfmBGBVXLN9_VPk--v83MzlFvCoPjT4x3g"
    )
    return client_test
