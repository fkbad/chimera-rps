from typing import Callable, Optional

from chimera.backend.fake import FakeChimeraServer
from chimera.client.api import ClientAPI, MatchNotification, MatchNotificationCallback
from chimera.client.connectors import WebSocketsConnector, FakeConnector
from chimera.exceptions import ChimeraConnectionRefusedException
import chimera.authoring


class Chimera(ClientAPI):
    """
    The main Chimera class. Use this class to connect to a Chimera
    server and access the games on that server.

    Examples:

        >>> chimera = Chimera("chimera.example.org")
        >>> games = chimera.get_games()
        >>> connectm = games["connectm"]
        >>> match = connectm.create_match("Alex")

    """

    def __init__(self, host: str, port: str = "14200",
                 notification_callback: Optional[MatchNotificationCallback] = None):
        """ Constructor

        Raises:
            ChimeraConnectionRefusedException: if unable to connect to the server

        Args:
            host: Hostname of Chimera server
            port: Port to connect to (default: "14200")
            notification_callback: Optional callback function to call
                any time a match notification is received
        """
        connector = WebSocketsConnector(self, host, port)
        super().__init__(connector, notification_callback)
        try:
            self._connector.connect()
        except ConnectionRefusedError as cre:
            raise ChimeraConnectionRefusedException(cre) from cre

    def __del__(self) -> None:
        """ Destructor

        Disconnects from server when object is deleted.

        Returns: None
        """
        self._connector.disconnect()


class FakeChimera(ClientAPI):
    """
    A 'fake' implementation of the client API, used for testing
    purposes. Behaves exactly like the real client API but,
    instead of connecting to a server, it creates a FakeChimeraServer
    instance (which provides access to the message processing layer
    of the server directly, bypassing the network layer)
    """

    def __init__(self, fake_server: Optional[FakeChimeraServer] = None,
                 notification_callback: Optional[MatchNotificationCallback] = None):
        connector = FakeConnector(self, fake_server)
        super().__init__(connector, notification_callback)

    def add_game(self, game_id: str, game_cls: chimera.authoring.Game, description: str) -> None:
        """ Registers a Game class in the fake server

        Args:
            game_id: Game identifier
            game_cls: Game class
            description: Game description

        Returns: None

        """
        self._connector.add_game(game_id, game_cls, description)

    def process_notifications(self) -> None:
        """ Processes all pending notifications

        Since we are not using an actual server, any notifications
        are just deposited in a list, and have to be explicitly processed.

        Returns: None

        """
        self._connector.process_notifications()
