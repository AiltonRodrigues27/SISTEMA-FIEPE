from collections.abc import Generator

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.database import engine
from app.infrastructure.sqlalchemy_base import Base


@pytest.fixture
def session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    table_names = ", ".join(table.name for table in Base.metadata.sorted_tables)
    connection.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()
