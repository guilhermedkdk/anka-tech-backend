from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Usa o engine assíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Cria um Session factory
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Classe base para os modelos
class Base(DeclarativeBase):
    pass

# Dependência para injeção no FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
