import pytest

from tests.common.utils import validate_notification

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins

from tests.common.fixtures import test_server


@pytest.mark.asyncio
async def test_notification_start(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    for c in (c1, c2):
        assert c.num_notifications == 1
        notification = next(c.notifications)

        expect_game_state = {'player1_phrase': None, 'player2_phrase': None}

        validate_notification(notification,
                              expect_scope="match",
                              expect_event="start",
                              expect_match_id=m,
                              expect_match_status="in-progress",
                              expect_game_id="p1-wins",
                              expect_game_state=expect_game_state)


@pytest.mark.asyncio
async def test_notification_update(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    # Skip 'start' notifications
    next(c1.notifications)
    next(c2.notifications)

    await test_server.game_action(c1, m, "move", {"phrase": "Test"})

    for c in (c1, c2):
        assert c.num_notifications == 1
        notification = next(c.notifications)

        expect_game_state = {'player1_phrase': "Test", 'player2_phrase': None}

        validate_notification(notification,
                              expect_scope="match",
                              expect_event="update",
                              expect_match_id=m,
                              expect_match_status="in-progress",
                              expect_game_id="p1-wins",
                              expect_game_state=expect_game_state)


@pytest.mark.asyncio
async def test_notification_end(test_server):
    games = [("p1-wins", PlayerOneWins, "Player One Wins"),
             ("chicken", Chicken, "Chicken")]

    c1, c2, m = await test_server.setup_match(games, "p1-wins", "Alex", "Sam")

    # Skip 'start' notifications
    next(c1.notifications)
    next(c2.notifications)

    await test_server.game_action(c1, m, "move", {"phrase": "Test"})

    # Skip 'update' notifications
    next(c1.notifications)
    next(c2.notifications)

    await test_server.game_action(c2, m, "move", {"phrase": "Test 2"})

    for c in (c1, c2):
        assert c.num_notifications == 1
        notification = next(c.notifications)

        expect_game_state = {'player1_phrase': "Test", 'player2_phrase': "Test 2"}

        validate_notification(notification,
                              expect_scope="match",
                              expect_event="end",
                              expect_match_id=m,
                              expect_match_status="done",
                              expect_match_winner="Alex",
                              expect_game_id="p1-wins",
                              expect_game_state=expect_game_state)