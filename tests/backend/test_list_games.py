import pytest
from pytest_unordered import unordered
import json

from tests.common.utils import create_request_msg

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins

from tests.common.fixtures import test_server


@pytest.mark.asyncio
async def test_list_games_empty(test_server):
    client = test_server.create_client()

    msg_id = "foobar-42"
    request = create_request_msg("list-games", msg_id)
    request = json.dumps(request)

    await test_server.fake_send_message(client, request)

    assert client.num_responses == 1
    response = next(client.responses)

    assert response["type"] == "response"
    assert response["id"] == msg_id
    assert response["result"] == {"games": []}


@pytest.mark.asyncio
async def test_list_games_single(test_server):
    client = test_server.create_client()

    msg_id = "foobar-42"
    request = create_request_msg("list-games", msg_id)
    request = json.dumps(request)

    test_server.register_game("p1-wins", PlayerOneWins, "Player One Wins")

    await test_server.fake_send_message(client, request)

    assert client.num_responses == 1
    response = next(client.responses)

    expected_games = [{"id": "p1-wins",
                       "description": "Player One Wins"}]

    assert response["type"] == "response"
    assert response["id"] == msg_id
    assert response["result"] == {"games": expected_games}


@pytest.mark.asyncio
async def test_list_games_multiple(test_server):
    client = test_server.create_client()

    msg_id = "foobar-42"
    request = create_request_msg("list-games", msg_id)
    request = json.dumps(request)

    test_server.register_game("p1-wins", PlayerOneWins, "Player One Wins")
    test_server.register_game("chicken", Chicken, "Chicken")

    await test_server.fake_send_message(client, request)

    assert client.num_responses == 1
    response = next(client.responses)

    expected_games = [{"id": "p1-wins",
                       "description": "Player One Wins"},
                      {"id": "chicken",
                       "description": "Chicken"}]

    assert response["type"] == "response"
    assert response["id"] == msg_id
    assert response["result"] == {"games": unordered(expected_games)}
