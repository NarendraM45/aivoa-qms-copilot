"""Async SQLAlchemy engine, session factory, and database initialization."""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=5, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_db():
    """FastAPI dependency that yields an async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Create all tables if they don't exist.
    
    This is a fallback for when Alembic migrations haven't been run.
    In production, use `alembic upgrade head` instead.
    Gracefully handles connection failures so the app can still start
    (useful during development when DB might not be ready yet).
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.warning(
            f"Could not connect to database during startup: {e}. "
            "The app will start but database operations will fail until "
            "the database is available. Run 'alembic upgrade head' or "
            "ensure PostgreSQL is running."
        )
