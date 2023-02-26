import pytest

from chimera.client import FakeChimera
from chimera.common import ErrorCode
from chimera.exceptions import AlreadyInAMatch
from tests.common.utils import validate_exc_info

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins

from tests.common.fixtures import test_server


def test_create_match():
    chimera = FakeChimera()

    chimera.add_game("p1-wins", PlayerOneWins, "Player One Wins")
    chimera.add_game("chicken", Chicken, "Chicken")

    games = chimera.get_games()

    assert len(games) == 2
    assert "p1-wins" in games
    p1wins = games["p1-wins"]
    assert "chicken" in games
    chicken = games["chicken"]

    match = p1wins.create_match("Alex")
    assert match._game == p1wins
    assert isinstance(match.id, str)


def test_create_match_already_in_match():
    chimera = FakeChimera()

    chimera.add_game("p1-wins", PlayerOneWins, "Player One Wins")
    chimera.add_game("chicken", Chicken, "Chicken")

    games = chimera.get_games()

    assert len(games) == 2
    assert "p1-wins" in games
    p1wins = games["p1-wins"]
    assert "chicken" in games
    chicken = games["chicken"]

    p1wins.create_match("Alex")

    with pytest.raises(AlreadyInAMatch) as exc_info:
        chicken.create_match("Sam")

    validate_exc_info(exc_info, ErrorCode.ALREADY_IN_MATCH)
