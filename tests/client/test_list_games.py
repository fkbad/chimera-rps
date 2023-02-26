from chimera.client import FakeChimera
from chimera.client.api import Game

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins


def test_list_games_empty():
    chimera = FakeChimera()

    games = chimera.get_games()

    assert len(games) == 0


def test_list_games_single():
    chimera = FakeChimera()

    chimera.add_game("p1-wins", PlayerOneWins, "Player One Wins")

    games = chimera.get_games()

    assert len(games) == 1
    assert "p1-wins" in games
    game = games["p1-wins"]

    assert isinstance(game, Game)
    assert game.id == "p1-wins"
    assert game.description == "Player One Wins"


def test_list_games_multiple():
    chimera = FakeChimera()

    chimera.add_game("p1-wins", PlayerOneWins, "Player One Wins")
    chimera.add_game("chicken", Chicken, "Chicken")

    games = chimera.get_games()

    assert len(games) == 2
    assert "p1-wins" in games
    p1wins = games["p1-wins"]
    assert "chicken" in games
    chicken = games["chicken"]

    assert p1wins.id == "p1-wins"
    assert p1wins.description == "Player One Wins"

    assert chicken.id == "chicken"
    assert chicken.description == "Chicken"
