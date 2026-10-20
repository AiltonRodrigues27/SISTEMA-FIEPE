from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Só o efeito do import importa: registra todas as tabelas no Base.metadata, e as chaves estrangeiras precisam disso.
from app.infrastructure import model_registry  # noqa: F401
from app.infrastructure.settings import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
