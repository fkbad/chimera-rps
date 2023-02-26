import pytest

from chimera.common import ErrorCode

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins

from tests.common.fixtures import test_server


@pytest.mark.asyncio
async def test_game_action(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    response = await test_server.game_action(c1, m, "move", {"phrase": "Test"})

    assert response["result"] == {"received": "Test"}


@pytest.mark.asyncio
async def test_game_action_wrong_match(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    response = await test_server.game_action(c1, m+"foobar", "move", {"phrase": "Test"})

    assert response["error"]["code"] == ErrorCode.INCORRECT_MATCH.value
    assert response["error"]["message"] == str(ErrorCode.INCORRECT_MATCH)


@pytest.mark.asyncio
async def test_game_action_player_not_in_match(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    _, _, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    c3 = test_server.create_client()

    response = await test_server.game_action(c3, m, "move", {"phrase": "Test"})

    assert response["error"]["code"] == ErrorCode.INCORRECT_MATCH.value
    assert response["error"]["message"] == str(ErrorCode.INCORRECT_MATCH)


@pytest.mark.asyncio
async def test_game_action_wrong_action(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    response = await test_server.game_action(c1, m, "wrong", {"phrase": "Test"})

    assert response["error"]["code"] == ErrorCode.GAME_NO_SUCH_ACTION.value
    assert response["error"]["message"] == str(ErrorCode.GAME_NO_SUCH_ACTION)


@pytest.mark.asyncio
async def test_game_action_missing_action_data(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    response = await test_server.game_action(c1, m, "move", {})

    assert response["error"]["code"] == ErrorCode.GAME_INCORRECT_ACTION_DATA.value
    assert response["error"]["message"] == str(ErrorCode.GAME_INCORRECT_ACTION_DATA)


@pytest.mark.asyncio
async def test_game_action_unexpected_action_data(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    response = await test_server.game_action(c1, m, "move", {"phrase": "Test", "foo": "bar"})

    assert response["error"]["code"] == ErrorCode.GAME_INCORRECT_ACTION_DATA.value
    assert response["error"]["message"] == str(ErrorCode.GAME_INCORRECT_ACTION_DATA)


@pytest.mark.asyncio
async def test_game_action_not_player_turn(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    response = await test_server.game_action(c2, m, "move", {"phrase": "Test"})

    assert response["error"]["code"] == ErrorCode.GAME_NOT_PLAYER_TURN.value
    assert response["error"]["message"] == str(ErrorCode.GAME_NOT_PLAYER_TURN)