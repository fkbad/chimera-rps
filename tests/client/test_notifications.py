from chimera.backend.fake import FakeChimeraServer
from chimera.client import FakeChimera
from chimera.client.api import Match, MatchNotification

from chimera.examples.chicken import Chicken
from chimera.examples.p1wins import PlayerOneWins

from tests.common.fixtures import test_client_p1wins


def test_notification_start(test_client_p1wins):
    c1, c2, m1, m2 = test_client_p1wins

    c1.process_notifications()
    c2.process_notifications()

    for match in (m1, m2):
        assert match._notifications.qsize() == 1
        notif = match.next_notification()

        expect_game_state = {'player1_phrase': None, 'player2_phrase': None}

        assert notif.event == MatchNotification.EVENT_START
        assert notif.match_status == Match.STATUS_IN_PROGRESS
        assert notif.winner is None
        assert notif.game_state == expect_game_state

        assert match.status == Match.STATUS_UNKNOWN
        assert match.game_state is None
        assert match.winner is None
        notif.process()
        assert match.status == Match.STATUS_IN_PROGRESS
        assert match.game_state == expect_game_state
        assert match.winner is None


def test_notification_update(test_client_p1wins):
    c1, c2, m1, m2 = test_client_p1wins

    m1.game_action("move", {"phrase": "Test"})

    c1.process_notifications()
    c2.process_notifications()

    # Skip 'start' notifications
    m1.next_notification().process()
    m2.next_notification().process()

    for match in (m1, m2):
        assert match._notifications.qsize() == 1
        notif = match.next_notification()

        expect_game_state = {'player1_phrase': "Test", 'player2_phrase': None}

        assert notif.event == MatchNotification.EVENT_UPDATE
        assert notif.match_status == Match.STATUS_IN_PROGRESS
        assert notif.winner is None
        assert notif.game_state == expect_game_state

        assert match.status ==  Match.STATUS_IN_PROGRESS
        assert match.game_state == {'player1_phrase': None, 'player2_phrase': None}
        assert match.winner is None
        notif.process()
        assert match.status == Match.STATUS_IN_PROGRESS
        assert match.game_state == expect_game_state
        assert match.winner is None


def test_notification_end(test_client_p1wins):
    c1, c2, m1, m2 = test_client_p1wins

    m1.game_action("move", {"phrase": "Test"})
    m2.game_action("move", {"phrase": "Test 2"})

    c1.process_notifications()
    c2.process_notifications()

    # Skip 'start' notifications
    m1.next_notification().process()
    m2.next_notification().process()

    # Skip 'update' notifications
    m1.next_notification().process()
    m2.next_notification().process()

    for match in (m1, m2):
        assert match._notifications.qsize() == 1
        notif = match.next_notification()

        expect_game_state = {'player1_phrase': "Test", 'player2_phrase': "Test 2"}

        assert notif.event == MatchNotification.EVENT_END
        assert notif.match_status == Match.STATUS_DONE
        assert notif.winner == m1.player_name
        assert notif.game_state == expect_game_state

        assert match.status == Match.STATUS_IN_PROGRESS
        assert match.game_state == {'player1_phrase': "Test", 'player2_phrase': None}
        assert match.winner is None
        notif.process()
        assert match.status == Match.STATUS_DONE
        assert match.game_state == expect_game_state
        assert match.winner == m1.player_name


def test_notification_callback():
    notif = None

    def callback(notification):
        nonlocal notif
        notification.process()
        notif = notification

    fs = FakeChimeraServer()
    c1 = FakeChimera(fs, notification_callback=callback)
    c2 = FakeChimera(fs)

    c1.add_game("p1-wins", PlayerOneWins, "Player One Wins")
    c1.add_game("chicken", Chicken, "Chicken")

    m1 = c1.get_games()["p1-wins"].create_match("Alex")
    m2 = c2.get_games()["p1-wins"].join_match(m1.id, "Sam")

    c1.process_notifications()

    # Check start notification
    expect_game_state = {'player1_phrase': None, 'player2_phrase': None}

    assert notif.event == MatchNotification.EVENT_START
    assert notif.match_status == Match.STATUS_IN_PROGRESS
    assert notif.winner is None
    assert notif.game_state == expect_game_state

    assert m1.status == Match.STATUS_IN_PROGRESS
    assert m1.game_state == expect_game_state
    assert m1.winner is None

    m1.game_action("move", {"phrase": "Test"})
    c1.process_notifications()

    # Check update notification
    expect_game_state = {'player1_phrase': "Test", 'player2_phrase': None}

    assert notif.event == MatchNotification.EVENT_UPDATE
    assert notif.match_status == Match.STATUS_IN_PROGRESS
    assert notif.winner is None
    assert notif.game_state == expect_game_state

    assert m1.status == Match.STATUS_IN_PROGRESS
    assert m1.game_state == expect_game_state
    assert m1.winner is None

    m2.game_action("move", {"phrase": "Test 2"})
    c1.process_notifications()

    # Check end notification
    expect_game_state = {'player1_phrase': "Test", 'player2_phrase': "Test 2"}

    assert notif.event == MatchNotification.EVENT_END
    assert notif.match_status == Match.STATUS_DONE
    assert notif.winner == m1.player_name
    assert notif.game_state == expect_game_state

    assert m1.status == Match.STATUS_DONE
    assert m1.game_state == expect_game_state
    assert m1.winner == m1.player_name
