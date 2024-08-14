import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, database_config
from src.model import Base

# Set up an in-memory SQLite database for testing purposes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create a new database session for each test
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[database_config.get_db] = _get_db
    return TestClient(app)


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_create_book(client):
    response = client.post("/books/", json={"title": "1984", "author": "George Orwell", "isbn": "0-8436-1072-7",
                                            "published_year": 1949})
    assert response.status_code == 200
    assert response.json()["title"] == "1984"
    assert response.json()["author"] == "George Orwell"


def test_get_book(client):
    response = client.post("/books/", json={"title": "1984", "author": "George Orwell", "isbn": "0-8436-1072-7",
                                            "published_year": 1949})
    book_id = response.json()["id"]
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "1984"


def test_update_book(client):
    response = client.post("/books/", json={"title": "1984", "author": "George Orwell", "isbn": "0-8436-1072-7",
                                            "published_year": 1949})
    book_id = response.json()["id"]
    response = client.put(f"/books/{book_id}", json={"author": "G. Orwell"})
    assert response.status_code == 200
    assert response.json()["author"] == "G. Orwell"


def test_delete_book(client):
    response = client.post("/books/", json={"title": "1984", "author": "George Orwell", "isbn": "0-8436-1072-7",
                                            "published_year": 1949})
    book_id = response.json()["id"]
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 200
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404


def test_get_non_existent_book(client):
    response = client.get("/books/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_create_patron(client):
    response = client.post("/patrons/",
                           json={"name": "John Doe", "phone_number": "1234567890", "email": "johndoe@gmail.com"})
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"
    assert response.json()["email"] == "johndoe@gmail.com"


def test_update_patron(client):
    response = client.post("/patrons/",
                           json={"name": "John Doe", "phone_number": "1234567890", "email": "johndoe@gmail.com"})
    patron_id = response.json()["id"]
    response = client.put(f"/patrons/{patron_id}", json={"phone_number": "0987654321"})
    assert response.status_code == 200
    assert response.json()["phone_number"] == "0987654321"


def test_delete_patron(client):
    response = client.post("/patrons/",
                           json={"name": "John Doe", "phone_number": "1234567890", "email": "johndoe@gmail.com"})
    patron_id = response.json()["id"]
    response = client.delete(f"/patrons/{patron_id}")
    assert response.status_code == 200
    response = client.get(f"/patrons/{patron_id}")
    assert response.status_code == 404


if __name__ == '__main__':
    import pytest

    exit_code = pytest.main()
    print(f"pytest exit code: {exit_code}")
