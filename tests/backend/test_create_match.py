import pytest

from chimera.common import ErrorCode

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins

from tests.common.fixtures import test_server

@pytest.mark.asyncio
async def test_create_match(test_server):
    client = test_server.create_client("Alex")

    test_server.register_game("p1-wins", PlayerOneWins, "Player One Wins")
    test_server.register_game("chicken", Chicken, "Chicken")

    await test_server.create_match(client, "p1-wins", "Alex")


@pytest.mark.asyncio
async def test_create_match_unknown_game(test_server):
    client = test_server.create_client("Alex")

    test_server.register_game("p1-wins", PlayerOneWins, "Player One Wins")
    test_server.register_game("chicken", Chicken, "Chicken")

    response = await test_server.create_match(client, "foobar", "Alex", validate_success=False)

    assert response["error"]["code"] == ErrorCode.UNKNOWN_GAME.value
    assert response["error"]["message"] == str(ErrorCode.UNKNOWN_GAME)

    assert len(test_server.matches) == 0


@pytest.mark.asyncio
async def test_create_match_already_in_match(test_server):
    client = test_server.create_client("Alex")

    test_server.register_game("p1-wins", PlayerOneWins, "Player One Wins")
    test_server.register_game("chicken", Chicken, "Chicken")

    await test_server.create_match(client, "p1-wins", "Alex", validate_success=True)

    response = await test_server.create_match(client, "chicken", "Alex", validate_success=False)

    assert response["error"]["code"] == ErrorCode.ALREADY_IN_MATCH.value
    assert response["error"]["message"] == str(ErrorCode.ALREADY_IN_MATCH)

    assert len(test_server.matches) == 1
