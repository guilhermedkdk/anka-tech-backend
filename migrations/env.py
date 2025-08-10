from __future__ import annotations

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# garante que "app" seja importável quando rodar de /migrations
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

# Alembic config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# importa metadata e settings do projeto
from app.db.base import Base
from app.core.config import settings

# importa os models para que sejam registrados no Base.metadata
import app.db.models

target_metadata = Base.metadata

# URL síncrona exclusiva para migrações
SQLALCHEMY_URL_SYNC = settings.DATABASE_SYNC_URL or os.getenv("DATABASE_SYNC_URL")
if not SQLALCHEMY_URL_SYNC:
    raise RuntimeError("DATABASE_SYNC_URL não configurada para migrações.")

def run_migrations_offline() -> None:
    """Executa migrações no modo offline (gera SQL sem aplicar)."""
    context.configure(
        url=SQLALCHEMY_URL_SYNC,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Executa migrações conectando ao banco (modo online)."""
    connectable = create_engine(
        SQLALCHEMY_URL_SYNC,
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
