import json
import weakref
from abc import ABC, abstractmethod
from asyncio import Future
from typing import Union, Dict

import websockets
import asyncio
import threading

from chimera.backend.fake import FakeChimeraServer
from chimera.client import ClientAPI


class BaseConnector(ABC):

    def __init__(self, api: ClientAPI):
        # We need to create this as a weak reference; otherwise,
        # Chimera.__del__ will fail to fully disconnect because
        # this reference will hold up the garbage collector
        self._api = weakref.ref(api)

    @abstractmethod
    def _generate_id(self):
        pass

    @abstractmethod
    def _send_msg(self, msg):
        pass

    def send_request(self, operation, params=None):
        msg = {}
        msg["type"] = "request"
        msg["id"] = self._generate_id()
        msg["operation"] = operation
        if params is not None:
            msg["params"] = params

        response = self._send_msg(msg)

        return response


class WebSocketsConnector(BaseConnector):

    _requests: Dict[str, Future]

    def __init__(self, api: ClientAPI, host: str, port: str):
        super().__init__(api)
        self._uri = f"ws://{host}:{port}"
        self._conn = None
        self._loop = None
        self._running = False
        self._requests = {}
        self._recv = None
        self._msg_id = 1
        self._thread_exc = None

    def _thread(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._rcv_loop())

    async def _rcv_loop(self):
        try:
            self._conn = await websockets.connect(self._uri)
            self._thread_ready.set()
        except ConnectionRefusedError as cre:
            self._thread_exc = cre
            self._thread_ready.set()
            return

        while self._running:
            try:
                self._recv = self._loop.create_task(self._conn.recv())
                msg = await self._recv

                # TODO: Validate JSON and ID
                msg = json.loads(msg)
                msg_id = msg.get("id")
                if msg_id is not None:
                    response_future = self._requests.get(msg_id)
                    if response_future is not None:
                        response_future.set_result(msg)
                        del self._requests[msg_id]
                else:
                    self._api()._process_notification(msg)

                # TODO: Some messages seem to not be delivered unless
                #       we allow for a short delay here. In theory, it should
                #       be enough to call asyncuo.sleep(0) to yield to the
                #       scheduler, but that doesn't seem to work.
                await asyncio.sleep(0.01)
            except websockets.exceptions.ConnectionClosedOK:
                # TODO
                break
            except websockets.exceptions.ConnectionClosedError:
                # TODO
                break
            except asyncio.CancelledError:
                # TODO
                break

        await self._conn.close()

    async def _send(self, msg):
        msg_id = msg["id"]
        response_future = self._loop.create_future()
        self._requests[msg_id] = response_future
        msg_txt = json.dumps(msg)
        await self._conn.send(msg_txt)
        response = await response_future

        return response

    def _generate_id(self):
        host, port = self._conn.local_address
        msg_id = f"{host}:{port}-{self._msg_id:08}"
        self._msg_id += 1

        return msg_id

    def connect(self):
        self._running = True
        self._thread = threading.Thread(target=self._thread)
        self._thread_ready = threading.Event()
        self._thread.daemon = True
        self._thread.start()
        self._thread_ready.wait()

        if self._thread_exc is not None:
            self._running = False
            self._thread.join()
            raise self._thread_exc

    def disconnect(self):
        if self._running:
            self._api = None
            self._running = False
            self._loop.call_soon_threadsafe(self._recv.cancel)
            self._thread.join()

    def _send_msg(self, msg):
        # TODO: Add support for sending messages from inside callback functions
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop == self._loop:
            raise RuntimeError("Sending messages from a callback function is not currently supported")
        task = asyncio.run_coroutine_threadsafe(self._send(msg), self._loop)
        return task.result()


class FakeConnector(BaseConnector):

    def __init__(self, api, fake_server=None):
        super().__init__(api)
        if fake_server is None:
            self.server = FakeChimeraServer()
        else:
            self.server = fake_server
        self.client = self.server.create_client()
        self.msg_id = 1

    def _generate_id(self):
        msg_id = self.msg_id
        self.msg_id += 1

        return msg_id

    def _send_msg(self, msg):
        msg = json.dumps(msg)
        asyncio.run(self.server.fake_send_message(self.client, msg))
        response = next(self.client.responses)

        return response

    def add_game(self, game_id, game_cls, description):
        self.server.register_game(game_id, game_cls, description)

    def process_notifications(self):
        for notification in self.client.notifications:
            self._api()._process_notification(notification)
