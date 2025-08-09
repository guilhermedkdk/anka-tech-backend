from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os

# Lê a variável de ambiente DATABASE_URL (se não existir, usa um default local)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://invest:investpw@localhost:5432/investdb")

# Cria o engine assíncrono
engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

# Cria um Session factory
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Classe base para os modelos
class Base(DeclarativeBase):
    pass

# Dependência para injeção no FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
