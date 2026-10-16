from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.infrastructure.database import settings
from app.infrastructure.sqlalchemy_base import Base

# Importar os models registra as tabelas em Base.metadata, que o Alembic usa para gerar migrations.
from app.modules.clubs.adapters.outbound.persistence import models as clubs_models  # noqa: F401
from app.modules.league.adapters.outbound.persistence import models as league_models  # noqa: F401
from app.modules.market.adapters.outbound.persistence import models as market_models  # noqa: F401
from app.modules.players.adapters.outbound.persistence import models as players_models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
