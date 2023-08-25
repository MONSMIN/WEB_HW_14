import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from src.conf import config

Base = declarative_base()


class DatabaseSessionManager:
    """
    The DatabaseSessionManager class is responsible for managing database sessions.

    Parameters:
    - url (str): The URL of the database.

    Attributes:
    - _engine (AsyncEngine | None): The asynchronous database engine.
    - _session_maker (async_sessionmaker | None): The asynchronous session maker.
    """

    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker | None = async_sessionmaker(autocommit=False, autoflush=False,
                                                                            bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        A context manager for obtaining an asynchronous database session.
        Yields:
        - session (AsyncSession): An asynchronous database session.
        """

        if self._session_maker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    The get_db function is a context manager that returns an asynchronous session.

    Yields:
    - session (AsyncSession): An asynchronous database session.
    """
    async with sessionmanager.session() as session:
        yield session
