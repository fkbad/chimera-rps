import pytest

from tests.common.utils import validate_notification
from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins

from tests.common.fixtures import test_server


def check_notification(clients, event, match_id, status, game_state):
    for c in clients:
        assert c.num_notifications == 1
        notification = next(c.notifications)

        validate_notification(notification,
                              expect_scope="match",
                              expect_event=event,
                              expect_match_id=match_id,
                              expect_match_status=status,
                              expect_game_id="chicken",
                              expect_game_state=game_state)


@pytest.mark.asyncio
async def test_chicken(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "chicken", "Alex", "Sam")

    check_notification((c1,c2), "start", m, "in-progress", {})

    response = await test_server.game_action(c1, m, "move", {"swerve": True})
    response = await test_server.game_action(c2, m, "move", {"swerve": True})

    response = await test_server.game_action(c1, m, "move", {"swerve": False})
    response = await test_server.game_action(c2, m, "move", {"swerve": True})

    response = await test_server.game_action(c1, m, "move", {"swerve": True})
    response = await test_server.game_action(c2, m, "move", {"swerve": False})

    response = await test_server.game_action(c1, m, "move", {"swerve": False})
    response = await test_server.game_action(c2, m, "move", {"swerve": False})

