import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..database import database
from ..model import Dashboard  # type: ignore
from .ws_connection_manager import manager

router: APIRouter = APIRouter(prefix="/ws")


@router.websocket("/dashboard")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            async with database.session() as session:
                dashboard: Dashboard = await database.get_default_dashboard(session)
                await manager.send_personal_message(
                    f"{json.dumps(dashboard.to_dict())}", websocket
                )
                await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Client left the chat")
