from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe-mãe dos modelos SQLAlchemy.

    Cada módulo declara os seus em adapters/outbound/persistence/models.py.
    """
