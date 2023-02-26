import pytest
import websockets
import json
from chimera.backend.websocket import WebSocketsChimeraServer
from chimera.common import ErrorCode


@pytest.mark.asyncio
async def test_start_stop_server():
    server = WebSocketsChimeraServer("127.0.0.1", "14200")

    await server.start()

    assert server._server_task is not None
    assert server._stop is not None
    assert not server._stop.done()

    await server.stop()
    assert server._server_task is None
    assert server._stop is None

@pytest.mark.asyncio
async def test_send_recv():
    server = WebSocketsChimeraServer("127.0.0.1", "14200")
    await server.start()

    ws = await websockets.connect("ws://127.0.0.1:14200")

    await ws.send('{"foo": }')
    msg = await ws.recv()

    msg = json.loads(msg)
    assert msg["type"] == "response"
    assert msg["error"]["code"] == ErrorCode.PARSE_ERROR.value
    assert msg["error"]["message"] == str(ErrorCode.PARSE_ERROR)
    assert msg["id"] is None

    await server.stop()
