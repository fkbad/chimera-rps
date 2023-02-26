

def create_request_msg(operation, msg_id, params=None):
    msg = {}
    msg["type"] = "request"
    msg["id"] = msg_id
    msg["operation"] = operation

    if params is not None:
        msg["params"] = params

    return msg


def validate_notification(msg, expect_scope=None, expect_event=None, expect_match_id=None,
                          expect_match_status=None, expect_match_winner=None,
                          expect_game_id=None, expect_game_state=None):

    assert msg["type"] == "notification"

    if expect_scope:
        assert msg["scope"] == expect_scope

    if expect_event:
        assert msg["event"] == expect_event

    if expect_match_id:
        assert msg["data"]["match-id"] == expect_match_id

    if expect_match_status:
        assert msg["data"]["match-status"] == expect_match_status

    if expect_match_winner:
        assert msg["data"]["match-winner"] == expect_match_winner

    if expect_game_id:
        assert msg["data"]["game-id"] == expect_game_id

    if expect_game_state:
        assert msg["data"]["game-state"] == expect_game_state


def validate_exc_info(exc_info, error_code):
    exc = exc_info.value

    assert exc.code == error_code.value
    assert exc.error_message == str(error_code)
