
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
import os

from aep_example.main import app
from aep_example.db import get_db, Base
from aep_example.models import Shelf, Book

TEST_DB_URL = "sqlite+aiosqlite:///./test_api.db"

engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    try:
        os.remove("./test_api.db")
    except OSError:
        pass

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_models())

    yield

    async def drop_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(drop_models())
    try:
        os.remove("./test_api.db")
    except OSError:
        pass

def test_pagination_flow():
    # Clear tables first? Or just ignore previous data.
    pass

def test_update_shelf():
    # Create shelf
    resp = client.post("/shelves", json={"theme": "Original Theme"})
    assert resp.status_code == 201
    shelf_id = resp.json()["path"].split("/")[-1]

    # Update theme
    resp = client.patch(f"/shelves/{shelf_id}", json={"theme": "Updated Theme"})
    assert resp.status_code == 200
    assert resp.json()["theme"] == "Updated Theme"

    # Verify persistence
    resp = client.get(f"/shelves/{shelf_id}")
    assert resp.status_code == 200
    assert resp.json()["theme"] == "Updated Theme"

def test_update_book():
    # Create shelf
    resp = client.post("/shelves", json={"theme": "Book Shelf"})
    assert resp.status_code == 201
    shelf_id = resp.json()["path"].split("/")[-1]

    # Create book
    resp = client.post(f"/shelves/{shelf_id}/books", json={"title": "Original Title", "author": "Original Author"})
    assert resp.status_code == 201
    book_id = resp.json()["path"].split("/")[-1]

    # Update title only
    resp = client.patch(f"/shelves/{shelf_id}/books/{book_id}", json={"title": "Updated Title"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Original Author" # Should remain unchanged

    # Update author only
    resp = client.patch(f"/shelves/{shelf_id}/books/{book_id}", json={"author": "Updated Author"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title" # Should remain unchanged
    assert data["author"] == "Updated Author"

    # Verify persistence
    resp = client.get(f"/shelves/{shelf_id}/books/{book_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Updated Author"
