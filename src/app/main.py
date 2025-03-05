import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from uvicorn.server import Server

from app.config import Config
from app.updating_dashboard_data import update_dashboard_data

from .api import endpoints, root, ws_dashboard
from .database import database


async def cron_update_data() -> None:
    while True:
        await update_dashboard_data()
        await asyncio.sleep(Config.UPDATING_INTERVAL_SEC)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await database.create_tables()
    task: asyncio.Task[None] = asyncio.create_task(cron_update_data())
    yield
    task.cancel()
    await database.aclose()


API_V1_PREFIX: str = "/api/v1"
app: FastAPI = FastAPI(lifespan=lifespan, docs_url=f"{API_V1_PREFIX}/docs")
app.include_router(ws_dashboard.router, prefix=API_V1_PREFIX)
app.include_router(endpoints.router, prefix=API_V1_PREFIX)
app.include_router(root.router)


async def run_backend() -> None:
    server: Server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=8000))
    await server.serve()


def main() -> None:
    try:
        asyncio.run(run_backend())
    except KeyboardInterrupt:
        pass
