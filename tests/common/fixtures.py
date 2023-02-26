import pytest
import json

from chimera.backend.fake import FakeChimeraServer
from chimera.client import FakeChimera
from tests.common.utils import create_request_msg

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins


class TestChimeraServer(FakeChimeraServer):

    def __init__(self, init_msg_id=1):
        super().__init__()
        self.msg_id = init_msg_id

    def _get_msg_id(self):
        msg_id = self.msg_id
        self.msg_id += 1
        return msg_id

    async def create_match(self, client, match_game, player_name, validate_success=True):
        msg_id = self._get_msg_id()
        params = {"game": match_game, "player-name": player_name}
        request = create_request_msg("create-match", msg_id, params)
        request = json.dumps(request)

        await self.fake_send_message(client, request)

        assert client.num_responses == 1
        response = next(client.responses)

        assert response["type"] == "response"
        assert response["id"] == msg_id

        if validate_success:
            assert "match-id" in response["result"]
            assert isinstance(response["result"]["match-id"], str)

            match_id = response["result"]["match-id"]
            assert match_id in self.matches

            match = self.matches[match_id]
            assert match.game.num_players == 1
            assert match.game.get_player_by_id(0).name == player_name

        return response

    async def join_match(self, client, match_game, match_id, player_name, validate_success=True):
        msg_id = self._get_msg_id()
        params = {"game": match_game, "match-id": match_id, "player-name": player_name}
        request = create_request_msg("join-match", msg_id, params)
        request = json.dumps(request)

        await self.fake_send_message(client, request)

        assert client.num_responses == 1
        response = next(client.responses)

        assert response["type"] == "response"
        assert response["id"] == msg_id

        if validate_success:
            assert response["result"] == {}

            assert match_id in self.matches
            match = self.matches[match_id]

            assert match.game.num_players >= 2
            assert any(p.name == player_name for p in match.game._players)

        return response

    async def setup_match(self, games, match_game, p1_name, p2_name):
        player1 = self.create_client(p1_name)
        player2 = self.create_client(p2_name)

        for game_id, game_cls, description in games:
            self.register_game(game_id, game_cls, description)

        response = await self.create_match(player1, match_game, p1_name)
        match_id = response["result"]["match-id"]
        await self.join_match(player2, match_game, match_id, p2_name)

        match = self.matches[match_id]
        assert match.game.num_players == 2
        assert match.game.get_player_by_id(0).name == p1_name
        assert match.game.get_player_by_id(1).name == p2_name

        return player1, player2, match_id

    async def game_action(self, client, match_id, action, data):
        msg_id = self._get_msg_id()
        params = {"match-id": match_id, "action": action, "data": data}
        request = create_request_msg("game-action", msg_id, params)
        request = json.dumps(request)

        await self.fake_send_message(client, request)

        assert client.num_responses == 1
        response = next(client.responses)

        assert response["type"] == "response"
        assert response["id"] == msg_id

        return response


@pytest.fixture
def test_server():
    return TestChimeraServer()


@pytest.fixture()
def test_client_chicken():
    fs = FakeChimeraServer()
    c1 = FakeChimera(fs)
    c2 = FakeChimera(fs)

    c1.add_game("p1-wins", PlayerOneWins, "Player One Wins")
    c1.add_game("chicken", Chicken, "Chicken")

    gs1 = c1.get_games()
    g1 = gs1["chicken"]
    m1 = g1.create_match("Alex")

    gs2 = c2.get_games()
    g2 = gs2["chicken"]
    m2 = g2.join_match(m1.id, "Sam")

    return c1, c2, m1, m2


@pytest.fixture()
def test_client_p1wins():
    fs = FakeChimeraServer()
    c1 = FakeChimera(fs)
    c2 = FakeChimera(fs)

    c1.add_game("p1-wins", PlayerOneWins, "Player One Wins")
    c1.add_game("chicken", Chicken, "Chicken")

    gs1 = c1.get_games()
    g1 = gs1["p1-wins"]
    m1 = g1.create_match("Alex")

    gs2 = c2.get_games()
    g2 = gs2["p1-wins"]
    m2 = g2.join_match(m1.id, "Sam")

    return c1, c2, m1, m2
