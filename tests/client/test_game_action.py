import pytest

from chimera.common import ErrorCode
from chimera.exceptions import GameNoSuchAction, GameIncorrectActionData, GameNotPlayerTurn
from tests.common.utils import validate_exc_info
from tests.common.fixtures import test_client_p1wins


def test_game_action(test_client_p1wins):
    c1, c2, m1, m2 = test_client_p1wins

    result = m1.game_action("move", {"phrase": "Test"})

    assert result == {"received": "Test"}


def test_game_action_wrong_action(test_client_p1wins):
    c1, c2, m1, m2 = test_client_p1wins

    with pytest.raises(GameNoSuchAction) as exc_info:
        m1.game_action("wrong", {"phrase": "Test"})

    validate_exc_info(exc_info, ErrorCode.GAME_NO_SUCH_ACTION)


def test_game_action_missing_action_data(test_client_p1wins):
    c1, c2, m1, m2 = test_client_p1wins

    with pytest.raises(GameIncorrectActionData) as exc_info:
        m1.game_action("move", {})

    validate_exc_info(exc_info, ErrorCode.GAME_INCORRECT_ACTION_DATA)


def test_game_action_unexpected_action_data(test_client_p1wins):
    c1, c2, m1, m2 = test_client_p1wins

    with pytest.raises(GameIncorrectActionData) as exc_info:
        m1.game_action("move", {"phrase": "Test", "foo": "bar"})

    validate_exc_info(exc_info, ErrorCode.GAME_INCORRECT_ACTION_DATA)


def test_game_action_not_player_turn(test_client_p1wins):
    c1, c2, m1, m2 = test_client_p1wins

    with pytest.raises(GameNotPlayerTurn) as exc_info:
        m2.game_action("move", {"phrase": "Test"})

    validate_exc_info(exc_info, ErrorCode.GAME_NOT_PLAYER_TURN)
