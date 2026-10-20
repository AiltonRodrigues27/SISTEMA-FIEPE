from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.main import app


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()
