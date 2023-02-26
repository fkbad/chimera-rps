import json
import logging

from chimera.backend.server import BaseChimeraServer, BaseConnectedClient

LOGGER = logging.getLogger("chimera.messaging")


class FakeConnectedClient(BaseConnectedClient):

    def __init__(self, name, notification_callback=None):
        super().__init__()
        self.name = name
        self._responses = []
        self._notifications = []

    async def _send_msg(self, msg):
        msg_str = json.dumps(msg)
        LOGGER.debug(f"Server -> {self.name} | {msg_str}")
        if msg["type"] == "response":
            self._responses.append(msg)
        elif msg["type"] == "notification":
            self._notifications.append(msg)

    @property
    def responses(self):
        while len(self._responses) > 0:
            m = self._responses.pop(0)
            yield m

    @property
    def num_responses(self):
        return len(self._responses)

    @property
    def notifications(self):
        while len(self._notifications) > 0:
            m = self._notifications.pop(0)
            yield m

    @property
    def num_notifications(self):
        return len(self._notifications)


class FakeChimeraServer(BaseChimeraServer):

    def __init__(self):
        super().__init__()
        self.clients = []

    async def start(self):
        pass

    async def stop(self):
        pass

    def create_client(self, name="Client"):
        client = FakeConnectedClient(name)
        self.clients.append(client)
        return client

    async def fake_send_message(self, client, message):
        LOGGER.debug(f"{client.name} -> Server | {message}")
        await self._process_message(client, message)
