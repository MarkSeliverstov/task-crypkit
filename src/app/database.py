import contextlib
from typing import Any, AsyncIterator, Tuple

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import joinedload

from .config import Config
from .model import Base, Coin, Dashboard  # type: ignore


class Database:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}) -> None:
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def aclose(self) -> None:
        await self._engine.dispose()

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with database.session() as session:
            await self.ensure_default_dashboard(session)

    async def drop_all(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @staticmethod
    async def ensure_default_dashboard(session: AsyncSession) -> Dashboard:
        dashboard: Dashboard | None = await session.scalar(
            select(Dashboard).where(Dashboard.id == Config.DASHBOARD_ID)
        )
        if dashboard is None:
            dashboard = Dashboard(id=Config.DASHBOARD_ID, coins=[])
            session.add(dashboard)
            await session.commit()
        return dashboard

    @staticmethod
    async def get_default_dashboard(session: AsyncSession) -> Dashboard:
        result: Result[Tuple[Dashboard]] = await session.execute(
            select(Dashboard)
            .options(joinedload(Dashboard.coins).joinedload(Coin.info))
            .filter(Dashboard.id == Config.DASHBOARD_ID)
        )
        dashboard: Dashboard | None = result.scalar()
        assert dashboard, "Should be created before"
        return dashboard

    @staticmethod
    async def get_coin_info(session: AsyncSession, id: str) -> Coin | None:
        result: Result[Tuple[Coin]] = await session.execute(
            select(Coin).options(joinedload(Coin.info)).filter(Coin.id == id)
        )
        return result.scalar()


database: Database = Database(Config.DB_CONNECTION_URL)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with database.session() as session:
        yield session
