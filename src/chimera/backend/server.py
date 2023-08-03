from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Callable, Dict

from coolname import generate_slug  # type: ignore

from chimera.common import ErrorCode
from chimera.authoring import Game
import chimera.exceptions as exc


class Match:

    STATE_WAITING_FOR_PLAYERS = 0
    STATE_READY = 1
    STATE_INPROGRESS = 2
    STATE_DONE = 3

    STATE_STR = {
        STATE_WAITING_FOR_PLAYERS: "awaiting-players",
        STATE_READY: "ready",
        STATE_INPROGRESS: "in-progress",
        STATE_DONE: "done"
    }

    def __init__(self, match_id, game_id, game):
        self.match_id = match_id
        self.game_id = game_id
        self.game = game
        self.state = Match.STATE_WAITING_FOR_PLAYERS
        self.subscribers = set()

    def add_player(self, player_name):
        player = self.game._create_player(player_name)
        self.game._add_player(player)

        if self.game.num_players >= self.game.min_players:
            self.state = Match.STATE_READY

        return player

    def add_subscriber(self, client):
        self.subscribers.add(client)

    def is_ready(self):
        return self.state == Match.STATE_READY

    @property
    def match_state(self):
        state = {}
        state["match-id"] = self.match_id
        state["match-status"] = Match.STATE_STR[self.state]
        if self.state == Match.STATE_DONE:
            if self.game.winner is not None:
                state["match-winner"] = self.game.winner.name
            else:
                state["match-winner"] = None
        state["game-id"] = self.game_id
        if self.state in (Match.STATE_INPROGRESS, Match.STATE_DONE):
            state["game-state"] = self.game.game_state
        return state

    async def start(self):
        self.state = Match.STATE_INPROGRESS
        self.game.on_start()
        for client in self.subscribers:
            await client.send_notification("match", "start", self.match_state)

    async def notify_update(self):
        for client in self.subscribers:
            await client.send_notification("match", "update", self.match_state)

    async def end(self):
        self.state = Match.STATE_DONE
        self.game.on_end()
        for client in self.subscribers:
            await client.send_notification("match", "end", self.match_state)


class RegisteredGame:

    def __init__(self, game_id, game_cls, description):
        self.game_id = game_id
        self.game_cls = game_cls
        self.description = description

    def __repr__(self):
        return f"RegisteredGame('{self.game_id}', {self.game_cls.__name__}, '{self.description}')"


class BaseConnectedClient(ABC):

    def __init__(self):
        self.current_match = None
        self.current_player = None

    @abstractmethod
    async def _send_msg(self, msg):
        pass

    async def send_error(self, msg_id, error_code, data=None):
        msg = {}
        msg["type"] = "response"
        msg["id"] = msg_id
        msg["error"] = {"code": error_code.value,
                        "message": str(error_code)
                        }
        if data is not None:
            msg["error"]["data"] = data

        await self._send_msg(msg)

    async def send_response(self, msg_id, result):
        msg = {}
        msg["type"] = "response"
        msg["id"] = msg_id
        msg["result"] = result

        await self._send_msg(msg)

    async def send_notification(self, scope, event, data):
        msg = {}
        msg["type"] = "notification"
        msg["scope"] = scope
        msg["event"] = event
        msg["data"] = data

        await self._send_msg(msg)


def register_handler(handler_name):
    def wrapper(func):
        func.handler_name = handler_name
        return func

    return wrapper


MessageHandlerType = Callable[["BaseChimeraServer", BaseConnectedClient, dict], None]


class BaseChimeraServer(ABC):
    MSG_HANDLERS: Dict[str, MessageHandlerType] = {}

    def __init__(self):
        self.clients = {}
        self.games = {}
        self.matches = {}

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    async def _process_message(self, client, raw_message):
        # Check that the JSON is correct
        try:
            msg = json.loads(raw_message)
        except json.JSONDecodeError as json_exc:
            error_details = f"Incorrect JSON (parsing failed at line {json_exc.lineno} column {json_exc.colno})"
            await client.send_error(msg_id=None,
                                    error_code=ErrorCode.PARSE_ERROR,
                                    data={"details": error_details}
                                    )
            return

        # Check that a type member has been included
        message_type = msg.get("type")
        if message_type is None:
            await client.send_error(msg_id=None,
                                    error_code=ErrorCode.INCORRECT_REQUEST,
                                    data={"details": "Message has no 'type' member"}
                                    )
            return

        # Check that we've received a request message
        if message_type != "request":
            await client.send_error(msg_id=None,
                                    error_code=ErrorCode.INCORRECT_REQUEST,
                                    data={"details": f"Incorrect message type: {msg['type']}"}
                                    )
            return

        # Check that the request includes an id
        msg_id = msg.get("id")
        if msg_id is None:
            await client.send_error(msg_id=None,
                                    error_code=ErrorCode.INCORRECT_REQUEST,
                                    data={"details": f"No id specified"}
                                    )
            return

        # Check that the operation is correct (i.e., an operation
        # has been specified, and we have a handler for that operation)
        operation = msg.get("operation")
        if operation is None:
            await client.send_error(msg_id=msg_id,
                                    error_code=ErrorCode.INCORRECT_REQUEST,
                                    data={"details": f"No operation specified"}
                                    )
            return

        handler_func = BaseChimeraServer.MSG_HANDLERS.get(operation)
        if handler_func is None:
            await client.send_error(msg_id=msg_id,
                                    error_code=ErrorCode.NO_SUCH_OPERATION
                                    )
            return

        await handler_func(self, client, msg)

    def register_game(self, game_id, game_cls, description):
        if not issubclass(game_cls, Game):
            raise ValueError(f"game_logic_cls parameter to register_game must be a subclass of GameLogic")

        rg = RegisteredGame(game_id, game_cls, description)
        print(f"registered game! {game_cls}")

        self.games[game_id] = rg

    async def _validate_params(self, client, msg, params):
        for param in params:
            if param not in msg["params"]:
                await client.send_error(msg_id=msg["id"],
                                        error_code=ErrorCode.INCORRECT_PARAMS,
                                        data={"details": f"Missing '{param}' parameter"}
                                        )
                return False

        return True

    @register_handler("list-games")
    async def _handle_list_games(self, client, msg):
        games = []
        for rg in self.games.values():
            game = {"id": rg.game_id, "description": rg.description}
            games.append(game)

        await client.send_response(msg["id"], {"games": games})

    @register_handler("create-match")
    async def _handle_create_match(self, client, msg):
        if client.current_match is not None:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.ALREADY_IN_MATCH,
                                    data={"details": "You are already in a match. You cannot create new matches."}
                                    )
            return

        params = msg["params"]
        if not await self._validate_params(client, msg, ["game", "player-name"]):
            return

        game_id = params["game"]
        rg = self.games.get(game_id)
        if rg is None:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.UNKNOWN_GAME,
                                    data={"details": f"Unknown game: {game_id}"}
                                    )
            return

        match_id = generate_slug(2)
        while match_id in self.matches:
            match_id = generate_slug(2)

        # TODO: Add support for game options
        game_options = {}
        game = rg.game_cls(game_options)

        match = Match(match_id, game_id, game)
        player = match.add_player(params["player-name"])
        client.current_match = match
        client.current_player = player
        match.add_subscriber(client)

        self.matches[match_id] = match

        response_result = {"match-id": match_id}

        await client.send_response(msg["id"], response_result)

    @register_handler("join-match")
    async def _handle_join_match(self, client, msg):
        if client.current_match is not None:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.ALREADY_IN_MATCH,
                                    data={"details": "You are already in a match. You cannot create new matches."}
                                    )
            return

        params = msg["params"]
        if not await self._validate_params(client, msg, ["game", "player-name", "match-id"]):
            return

        match_id = params["match-id"]
        match = self.matches.get(match_id)
        if match is None:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.UNKNOWN_MATCH,
                                    data={"details": f"Unknown match: {match_id}"}
                                    )
            return

        game_id = params["game"]
        if match.game_id != game_id:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.UNKNOWN_MATCH,
                                    data={"details": f"Wrong game for {match_id} (expected {match.game_id})"}
                                    )
            return

        player_name = params["player-name"]
        if any(p.name == player_name for p in match.game._players):
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.DUPLICATE_PLAYER,
                                    data={"details": f"Player '{player_name}' already exists in match '{match_id}'"}
                                    )
            return

        player = match.add_player(player_name)
        client.current_match = match
        client.current_player = player
        match.add_subscriber(client)

        response_result = {}

        await client.send_response(msg["id"], response_result)

        # If the match is ready (i.e., has enough players)
        # we automatically start it
        if match.is_ready():
            await match.start()


    @register_handler("game-action")
    async def _handle_game_action(self, client, msg):
        params = msg["params"]
        if not await self._validate_params(client, msg, ["match-id", "action", "data"]):
            return

        match_id = params["match-id"]

        if client.current_match is None:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.INCORRECT_MATCH,
                                    data={"details":  f"You are not in {match_id} (or that match does not exist)"}
                                    )
            return

        match = self.matches.get(match_id)
        if match is not client.current_match:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.INCORRECT_MATCH,
                                    data={"details": f"You are not in {match_id} (or that match does not exist)"}
                                    )
            return

        action_name = params["action"]
        game_data = params["data"]

        action_method = getattr(match.game, f"action_{action_name}", None)
        if action_method is None or not callable(action_method):
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.GAME_NO_SUCH_ACTION,
                                    data={"details": f"No such action: {action_name}"}
                                    )
            return

        try:
            result = action_method(client.current_player, game_data)

            await client.send_response(msg["id"], result)
        except exc.NotPlayerTurn as npte:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.GAME_NOT_PLAYER_TURN,
                                    data={"details": npte.details}
                                    )
        except exc.IncorrectActionData as iade:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.GAME_INCORRECT_ACTION_DATA,
                                    data={"details": iade.details}
                                    )
        except exc.IncorrectMove as im:
            await client.send_error(msg_id=msg["id"],
                                    error_code=ErrorCode.GAME_INCORRECT_MOVE,
                                    data={"details": im.details}
                                    )

        if match.game.done:
            await match.end()
            del self.matches[match_id]
        elif match.game._state_updated:
            await match.notify_update()
            match.game._reset_state_updated()


# Build handlers dictionary
for v in BaseChimeraServer.__dict__.values():
    if callable(v) and hasattr(v, "handler_name"):
        BaseChimeraServer.MSG_HANDLERS[v.handler_name] = v
