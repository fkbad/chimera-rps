import pytest

from chimera.client import FakeChimera
from chimera.common import ErrorCode
from chimera.exceptions import AlreadyInAMatch, UnknownMatch, DuplicatePlayer
from chimera.backend.fake import FakeChimeraServer
from tests.common.utils import validate_exc_info

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins


def test_join_match():
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


def test_join_match_already_playing():
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

    with pytest.raises(AlreadyInAMatch) as exc_info:
        gs1["chicken"].create_match("Jamie")

    validate_exc_info(exc_info, ErrorCode.ALREADY_IN_MATCH)

    with pytest.raises(AlreadyInAMatch) as exc_info:
        gs2["chicken"].create_match("Jessie")

    validate_exc_info(exc_info, ErrorCode.ALREADY_IN_MATCH)


def test_join_match_twice():
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

    with pytest.raises(AlreadyInAMatch) as exc_info:
        g2.join_match(m1.id, "Sam")

    validate_exc_info(exc_info, ErrorCode.ALREADY_IN_MATCH)


def test_join_match_no_matches():
    chimera = FakeChimera()

    chimera.add_game("p1-wins", PlayerOneWins, "Player One Wins")
    chimera.add_game("chicken", Chicken, "Chicken")

    games = chimera.get_games()

    with pytest.raises(UnknownMatch) as exc_info:
        games["chicken"].join_match("foobar", "Sam")

    validate_exc_info(exc_info, ErrorCode.UNKNOWN_MATCH)


def test_join_match_wrong_match():
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

    with pytest.raises(UnknownMatch) as exc_info:
        g2.join_match(m1.id+"foobar", "Sam")

    validate_exc_info(exc_info, ErrorCode.UNKNOWN_MATCH)


def test_join_match_wrong_game():
    fs = FakeChimeraServer()
    c1 = FakeChimera(fs)
    c2 = FakeChimera(fs)

    c1.add_game("p1-wins", PlayerOneWins, "Player One Wins")
    c1.add_game("chicken", Chicken, "Chicken")

    gs1 = c1.get_games()
    g1 = gs1["p1-wins"]
    m1 = g1.create_match("Alex")

    gs2 = c2.get_games()
    g2 = gs2["chicken"]

    with pytest.raises(UnknownMatch) as exc_info:
        g2.join_match(m1.id, "Sam")

    validate_exc_info(exc_info, ErrorCode.UNKNOWN_MATCH)


def test_join_match_duplicate_name():
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

    with pytest.raises(DuplicatePlayer) as exc_info:
        g2.join_match(m1.id, "Alex")

    validate_exc_info(exc_info, ErrorCode.DUPLICATE_PLAYER)
