import asyncio
import signal

import websockets
import logging
import json

from chimera.backend.server import BaseConnectedClient, BaseChimeraServer

LOGGER = logging.getLogger("chimera.server")

class WebSocketsConnectedClient(BaseConnectedClient):

    def __init__(self, websocket):
        super().__init__()
        self.websocket = websocket
        host, port = websocket.remote_address
        self.client_str = f"{host}:{port}"

    async def _send_msg(self, msg):
        raw_message = json.dumps(msg)
        LOGGER.debug(f"{self.client_str} SEND: {raw_message}")
        await self.websocket.send(raw_message)


class WebSocketsChimeraServer(BaseChimeraServer):

    def __init__(self, address, port):
        super().__init__()
        self.address = address
        self.port = port
        self._server_task = None
        self._ready = None
        self._stop = None

    async def _serve(self):
        async with websockets.serve(self._handler, self.address, self.port):
            self._ready.set_result(True)
            LOGGER.info(f"Server listening on {self.address}:{self.port}")
            await self._stop

    async def start(self):
        self._stop = asyncio.Future()
        self._ready = asyncio.Future()
        self._server_task = asyncio.create_task(self._serve())

        await self._ready

    async def stop(self):
        self._stop.set_result(True)
        await self._server_task
        self._server_task = None
        self._stop = None
        LOGGER.info(f"Server closed")

    async def wait_stopped(self):
        await self._server_task

    async def _handler(self, websocket):
        client = WebSocketsConnectedClient(websocket)
        self.clients[websocket] = client
        host, port = websocket.remote_address
        client_str = f"{host}:{port}"
        LOGGER.info(f"{client_str} Connected")
        try:
            async for raw_message in websocket:
                LOGGER.debug(f"{client_str} RCVD: {raw_message}")
                await self._process_message(client, raw_message)
        except websockets.exceptions.ConnectionClosed:
            pass
        LOGGER.info(f"{client_str} Disconnected")

        del self.clients[websocket]
