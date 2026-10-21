from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies import get_clock
from app.infrastructure.database import get_db
from app.main import app
from app.shared.domain.brasilia_time import BRASILIA


class MutableClock:
    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    def now(self) -> datetime:
        return self.moment


@pytest.fixture
def clock() -> MutableClock:
    return MutableClock(datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA))


@pytest.fixture
def client(session: Session, clock: MutableClock) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_clock] = lambda: clock
    yield TestClient(app)
    app.dependency_overrides.clear()
