import asyncio
import json
from collections.abc import AsyncIterator

import websockets

from app.core.config import get_settings


def connect_payload(uid: str, actid: str, susertoken: str) -> dict:
    return {"t": "c", "uid": uid, "actid": actid, "source": "TRTP", "susertoken": susertoken}


def heartbeat_payload() -> dict:
    return {"t": "h"}


def touchline_subscribe_payload(*keys: str) -> dict:
    return {"t": "t", "k": "#".join(keys)}


async def live_touchline(uid: str, actid: str, susertoken: str, keys: list[str]) -> AsyncIterator[dict]:
    async with websockets.connect(get_settings().definedge_ws_url) as websocket:
        await websocket.send(json.dumps(connect_payload(uid, actid, susertoken)))
        await websocket.send(json.dumps(touchline_subscribe_payload(*keys)))
        heartbeat = asyncio.create_task(_heartbeat(websocket))
        try:
            async for message in websocket:
                yield json.loads(message)
        finally:
            heartbeat.cancel()


async def _heartbeat(websocket) -> None:
    while True:
        await asyncio.sleep(50)
        await websocket.send(json.dumps(heartbeat_payload()))
