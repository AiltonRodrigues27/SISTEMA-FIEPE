from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.infrastructure.database import engine


@pytest.fixture
def session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()
