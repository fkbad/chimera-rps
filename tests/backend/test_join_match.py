import pytest

from chimera.common import ErrorCode

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins

from tests.common.fixtures import test_server


@pytest.mark.asyncio
async def test_join_match(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

@pytest.mark.asyncio
async def test_join_match_already_playing(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m1 = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")
    c3, c4, m2 = await test_server.setup_match(games, "chicken", "Jamie", "Jessie")

    response = await test_server.join_match(c3, "p1-wins", m1, "Jamie", validate_success=False)

    assert response["error"]["code"] == ErrorCode.ALREADY_IN_MATCH.value
    assert response["error"]["message"] == str(ErrorCode.ALREADY_IN_MATCH)

    assert test_server.matches[m1].game.num_players == 2
    assert test_server.matches[m2].game.num_players == 2


@pytest.mark.asyncio
async def test_join_match_twice(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m1 = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    response = await test_server.join_match(c2, "p1-wins", m1, "Sam", validate_success=False)

    assert response["error"]["code"] == ErrorCode.ALREADY_IN_MATCH.value
    assert response["error"]["message"] == str(ErrorCode.ALREADY_IN_MATCH)

    assert test_server.matches[m1].game.num_players == 2


@pytest.mark.asyncio
async def test_join_match_no_matches(test_server):
    client = test_server.create_client()

    response = await test_server.join_match(client, "p1-wins", "foobar", "Sam", validate_success=False)

    assert response["error"]["code"] == ErrorCode.UNKNOWN_MATCH.value
    assert response["error"]["message"] == str(ErrorCode.UNKNOWN_MATCH)

    assert len(test_server.matches) == 0


@pytest.mark.asyncio
async def test_join_match_wrong_match(test_server):
    player1 = test_server.create_client("Alex")
    player2 = test_server.create_client("Sam")

    test_server.register_game("p1-wins", PlayerOneWins, "Player One Wins")
    test_server.register_game("chicken", Chicken, "Chicken")

    response = await test_server.create_match(player1, "p1-wins", "Alex")
    match_id = response["result"]["match-id"]
    response = await test_server.join_match(player2, "p1-wins", match_id+"foobar", "Sam", validate_success=False)

    assert response["error"]["code"] == ErrorCode.UNKNOWN_MATCH.value
    assert response["error"]["message"] == str(ErrorCode.UNKNOWN_MATCH)

    assert len(test_server.matches) == 1
    assert test_server.matches[match_id].game.num_players == 1


@pytest.mark.asyncio
async def test_join_match_wrong_game(test_server):
    player1 = test_server.create_client("Alex")
    player2 = test_server.create_client("Sam")

    test_server.register_game("p1-wins", PlayerOneWins, "Player One Wins")
    test_server.register_game("chicken", Chicken, "Chicken")

    response = await test_server.create_match(player1, "p1-wins", "Alex")
    match_id = response["result"]["match-id"]
    response = await test_server.join_match(player2, "chicken", match_id, "Sam", validate_success=False)

    assert response["error"]["code"] == ErrorCode.UNKNOWN_MATCH.value
    assert response["error"]["message"] == str(ErrorCode.UNKNOWN_MATCH)

    assert len(test_server.matches) == 1
    assert test_server.matches[match_id].game.num_players == 1


@pytest.mark.asyncio
async def test_join_match_duplicate_name(test_server):
    player1 = test_server.create_client("Alex")
    player2 = test_server.create_client("Duplicate Alex")

    test_server.register_game("p1-wins", PlayerOneWins, "Player One Wins")
    test_server.register_game("chicken", Chicken, "Chicken")

    response = await test_server.create_match(player1, "p1-wins", "Alex")
    match_id = response["result"]["match-id"]
    response = await test_server.join_match(player2, "p1-wins", match_id, "Alex", validate_success=False)

    assert response["error"]["code"] == ErrorCode.DUPLICATE_PLAYER.value
    assert response["error"]["message"] == str(ErrorCode.DUPLICATE_PLAYER)

    assert len(test_server.matches) == 1
    assert test_server.matches[match_id].game.num_players == 1
