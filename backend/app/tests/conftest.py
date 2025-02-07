import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from io import BytesIO

from app.db import Base, get_db
from app.main import app
from app.auth.jwt import AuthHandler

# In-memory database setup for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables in the test database
Base.metadata.create_all(bind=engine)


# Fixture for the database
@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# Fixture for the test client
@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


# Fixture for the AuthHandler
@pytest.fixture(scope="function")
def auth_handler():
    return AuthHandler()


@pytest.fixture
def test_file():
    return ("test_file.txt", BytesIO(b"test content"), "text/plain")
