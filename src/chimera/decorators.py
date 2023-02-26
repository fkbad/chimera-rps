import chimera.exceptions as exc


def validate_turn(func):
    def _decorator(self, player, data):
        if player is not self.current_player:
            raise exc.NotPlayerTurn()
        return func(self, player, data)

    return _decorator


def expect_data(valid_fields):
    def _decorator(func):
        def _wrapper(self, player, data):
            for field in valid_fields:
                if field not in data:
                    raise exc.IncorrectActionData(f"Missing data field: {field}")
            for field in data:
                if field not in valid_fields:
                    raise exc.IncorrectActionData(f"Unexpected data field: {field}")

            return func(self, player, data)
        return _wrapper

    return _decorator
