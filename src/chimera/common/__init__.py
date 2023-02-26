from enum import Enum


class ErrorCode(Enum):
    # General error codes
    PARSE_ERROR = -32700
    INCORRECT_REQUEST = -32600
    NO_SUCH_OPERATION = -32601
    INCORRECT_PARAMS = -32602

    # Operation-specific codes
    UNKNOWN_GAME = -40100
    ALREADY_IN_MATCH = -40101
    UNKNOWN_MATCH = -40102
    DUPLICATE_PLAYER = -40103
    INCORRECT_MATCH = -40104

    # game-action codes
    GAME_NOT_PLAYER_TURN = -50100
    GAME_NO_SUCH_ACTION = -50101
    GAME_INCORRECT_ACTION_DATA = -50102
    GAME_INCORRECT_MOVE = -50103

    def __str__(self):
        return ERROR_MESSAGES[self.value]


ERROR_MESSAGES = {
    # General error codes
    ErrorCode.PARSE_ERROR.value: "Parse error",
    ErrorCode.INCORRECT_REQUEST.value: "Incorrect request",
    ErrorCode.NO_SUCH_OPERATION.value: "No such operation",
    ErrorCode.INCORRECT_PARAMS.value: "Incorrect parameters",

    # Operation-specific codes
    ErrorCode.UNKNOWN_GAME.value: "Unknown game",
    ErrorCode.ALREADY_IN_MATCH.value: "Already in a match",
    ErrorCode.UNKNOWN_MATCH.value: "Unknown match",
    ErrorCode.DUPLICATE_PLAYER.value: "Duplicate player name",
    ErrorCode.INCORRECT_MATCH.value: "Incorrect match",

    # game-action codes
    ErrorCode.GAME_NOT_PLAYER_TURN.value: "Action not allowed outside player's turn",
    ErrorCode.GAME_NO_SUCH_ACTION.value: "Unsupported action in game",
    ErrorCode.GAME_INCORRECT_ACTION_DATA.value: "Incorrect data in game action",
    ErrorCode.GAME_INCORRECT_MOVE.value: "Incorrect move"
}

