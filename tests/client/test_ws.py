import asyncio
import threading
import pytest

from chimera.backend.websocket import WebSocketsChimeraServer
from chimera.client import Chimera


async def server(stop_sig, server_ready, loop):
    asyncio.set_event_loop(loop)
    server = WebSocketsChimeraServer("127.0.0.1", "14200")
    await server.start()
    server_ready.set()
    await stop_sig
    await server.stop()

@pytest.fixture
def threaded_server():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    sig = asyncio.Future(loop=loop)
    def run_loop(loop, coro):
        loop.run_until_complete(coro)
        loop.close()
    server_ready = threading.Event()
    thread = threading.Thread(target=run_loop, args=(loop, server(sig, server_ready, loop)))
    thread.start()
    server_ready.wait()
    yield
    loop.call_soon_threadsafe(sig.set_result, None)
    thread.join()

def test_list_games(threaded_server):
    chimera = Chimera("127.0.0.1", "14200")
    games = chimera.get_games()
