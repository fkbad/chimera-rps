from __future__ import annotations

from queue import Queue, Empty
from typing import Callable, Dict, Optional

from chimera.exceptions import MalformedResponse, ErrorResponse, ERROR_EXCEPTIONS


class Game:
    """
    Class representing a game on the Chimera server.

    Should not be instantiated directly.
    """

    _api: ClientAPI
    _id: str
    _description: str
    _matches: Dict[str, Match]

    def __init__(self, api: ClientAPI, game_id: str, description: str):
        """ Constructor

        Args:
            api: API object
            game_id: Game identifier
            description: Game description
        """
        self._api = api
        self._id = game_id
        self._description = description
        self._matches = {}

    def __repr__(self) -> str:
        return f"Game('{self._id}', '{self._description}')"

    @property
    def id(self) -> str:
        """Get game identifier"""
        return self._id

    @property
    def description(self):
        """Get game description"""
        return self._description

    def create_match(self, player_name: str) -> Match:
        """ Creates a new match

        Args:
            player_name: Player name to use in the match

        Raises:
            AlreadyInAMatch: If player is already in another match

        Returns: Match object

        """
        params = {"game": self.id, "player-name": player_name}
        response = self._api.send_request("create-match", params)

        if "match-id" not in response["result"]:
            raise MalformedResponse("Missing 'match-id' field", response)

        match_id = response["result"]["match-id"]
        match = Match(self._api, self, match_id, player_name)

        self._api._matches[(self.id, match_id)] = match

        return match

    def join_match(self, match_id: str, player_name: str) -> Match:
        """ Joins an existing match

        Args:
            match_id:
            player_name:

        Raises:
            AlreadyInAMatch: If the player is already in a match
            UnknownMatch: If there is no match for the provided match identifier
            DuplicatePlayer: If there is already a player with the same name
                in the match

        Returns: Match object

        """
        params = {"game": self.id, "match-id": match_id, "player-name": player_name}
        response = self._api.send_request("join-match", params)

        if len(response["result"]) != 0:
            raise MalformedResponse("Unexpected results in 'join-match'", response)

        match = Match(self._api, self, match_id, player_name)
        self._api._matches[(self.id, match_id)] = match

        return match


class Match:
    """
    Class representing a match in the server.

    Should never be instantiated directly.
    """

    STATUS_AWAITING_PLAYERS = "awaiting-players"
    STATUS_READY = "ready"
    STATUS_IN_PROGRESS = "in-progress"
    STATUS_DONE = "done"
    STATUS_UNKNOWN = None

    _api: ClientAPI
    _game: Game
    _match_id: str
    _status: Optional[str]
    _player_name: str
    _winner: Optional[str]
    _game_state: Optional[dict]
    _notifications: Queue

    def __init__(self, api: ClientAPI, game: Game, match_id: str, player_name: str):
        """ Constructor

        Args:
            api: API object
            game: Game object
            match_id: Match identifier
            player_name: Player name
        """
        self._api = api
        self._game = game
        self._match_id = match_id
        self._status = Match.STATUS_UNKNOWN
        self._player_name = player_name
        self._winner = None
        self._game_state = None
        self._notifications = Queue()

    def __repr__(self) -> str:
        """Returns string representation of object"""
        return f"Match(<Game '{self._game.id}'>, '{self._match_id}')"

    def _process_notification(self, match_notification: MatchNotification) -> None:
        """ Process a notification and update game state

        Args:
            match_notification: Match notification

        Returns: None

        """
        self._status = match_notification.match_status
        self._game_state = match_notification.game_state
        self._winner = match_notification.winner

    def wait_for_update(self):
        notification = self._notifications.get()
        notification.process()
        try:
            while True:
                notification = self._notifications.get_nowait()
                notification.process()
        except Empty:
            pass

    def next_notification(self) -> Optional[MatchNotification]:
        """ If there are any unprocessed notifications, returns the next notification

        Returns: A MatchNotification object if there are any unprocessed
            notifications. Otherwise, returns None.

        """
        if not self._notifications.empty():
            return self._notifications.get_nowait()
        else:
            return None

    @property
    def id(self):
        """Gets the match identifier"""
        return self._match_id

    @property
    def status(self) -> Optional[str]:
        """Gets the match status"""
        return self._status

    @property
    def player_name(self) -> str:
        """Gets the player's name in the match"""
        return self._player_name

    @property
    def winner(self) -> Optional[str]:
        """Get's the winner's name (if any)"""
        return self._winner

    @property
    def game_state(self) -> Optional[dict]:
        """Get's the gane's state"""
        return self._game_state

    def game_action(self, action: str, data: Optional[dict] = None) -> None:
        """ Requests a game action

        Args:
            action: Name of the action to be performed
            data: Action-specific data

        Raises:
            GameNoSuchAction: If there is no such action in this game
            GameIncorrectActionData: If the provided data is incorrect
            GameNotPlayerTurn: If the requested action cannot be performed
                until it is the player's turn

        Returns: None

        """
        if data is None:
            data = {}

        params = {"match-id": self.id, "action": action, "data": data}
        response = self._api.send_request("game-action", params)

        return response["result"]


class MatchNotification:
    """
    Class for storing information about a match notification received by the server.

    Should never be instantiated directly.
    """

    EVENT_START = "start"
    EVENT_UPDATE = "update"
    EVENT_END = "end"

    _match: Match
    _event: str
    _data: dict

    def __init__(self, match: Match, event: str, data: dict):
        """ Constructor

        Args:
            match: Match this notification pertains to
            event: Event being notified
            data: Notification data
        """
        self._match = match
        self._event = event
        self._data = data

    @property
    def event(self) -> str:
        """Gets the notification event"""
        return self._event

    @property
    def match_status(self) -> Optional[str]:
        """Gets the match status included in the notification"""
        return self._data.get("match-status")

    @property
    def game_state(self) -> Optional[dict]:
        """Gets the game state included in the notification"""
        return self._data.get("game-state")

    @property
    def winner(self) -> Optional[str]:
        """Gets the winner included in the notification"""
        return self._data.get("match-winner")

    def process(self) -> None:
        """ Processes the notification, and updates tha state
        of the match with the information included in the
        notification.

        Returns: None

        """
        self._match._process_notification(self)


MatchNotificationCallback = Callable[[MatchNotification], None]


class ClientAPI:
    def __init__(self, connector, notification_callback):
        self._connector = connector
        self._notification_callback = notification_callback
        self._matches = {}

    @staticmethod
    def _validate_response_fields(response, obj, fields, where):
        for field in fields:
            if field not in obj:
                raise MalformedResponse(f"Missing '{field}' field in {where}", response)

    def _process_notification(self, notification):
        # Only match notifications are supported at the moment
        assert notification["scope"] == "match"

        game_id = notification["data"]["game-id"]
        match_id = notification["data"]["match-id"]

        match = self._matches.get((game_id, match_id))

        if match is None:
            # Silently drop notification
            # TODO: Raise or log this somehow
            return

        event = notification["event"]
        data = notification["data"]
        notification = MatchNotification(match, event, data)

        if self._notification_callback is not None:
            self._notification_callback(notification)
        else:
            match._notifications.put(notification)


    def _raise_error_exception(self, response):
        assert "error" in response

        self._validate_response_fields(response, response["error"],
                              ["code", "message", "data"], "error")

        error_code = response["error"]["code"]

        error_exception = ERROR_EXCEPTIONS.get(error_code, ErrorResponse)

        raise error_exception(response["error"]["code"],
                              response["error"]["message"],
                              response["error"]["data"])

    def get_games(self) -> Dict[str, Game]:
        response = self.send_request("list-games")

        if "games" not in response["result"]:
            raise MalformedResponse("Missing 'games' field", response)

        games = {}
        for g in response["result"]["games"]:
            self._validate_response_fields(response, g, ["id", "description"], "game")
            game = Game(self, g["id"], g["description"])
            games[game.id] = game

        return games

    def set_notification_callback(self, notification_callback):
        self._notification_callback = notification_callback

    def send_request(self, operation, params=None):
        response = self._connector.send_request(operation, params)

        self._validate_response_fields(response, response,
                              ["type", "id"], "response")

        if response["type"] != "response":
            raise MalformedResponse(f"Unexpected message type '{response['type']}", response)

        if "error" in response:
            raise self._raise_error_exception(response)

        self._validate_response_fields(response, response,
                                       ["result"], "response")

        return response
