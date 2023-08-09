import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from todo_app.database import Base
from todo_app.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    client = TestClient(app)
    yield client


@pytest.fixture
def override_get_db(monkeypatch):
    def mock_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    monkeypatch.setattr(app, "dependency_overrides", {get_db: mock_get_db})


def test_create_todo(client, override_get_db):
    todo_data = {
        "title": "string",
        "description": "string",
        "priority": 3,
        "complete": False,
    }
    response = client.post("/todo", json=todo_data)
    assert response.status_code == 201


def test_read_all(client, override_get_db):
    response = client.get("/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json() == [
        {
            "id": 1,
            "title": "string",
            "description": "string",
            "priority": 3,
            "complete": False,
        }
    ]


def test_get_todo_by_id(client, override_get_db):
    response = client.get("/todo/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "string",
        "description": "string",
        "priority": 3,
        "complete": False,
    }


def test_update_todo(client, override_get_db):
    todo_data = {
        "title": "updated_title",
        "description": "updated_description",
        "priority": 2,
        "complete": True,
    }
    response = client.put("/todo/1", json=todo_data)
    assert response.status_code == 204


def test_delete_todo(client, override_get_db):
    response = client.delete("/todo/1")
    assert response.status_code == 204
