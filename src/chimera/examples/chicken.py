from chimera.authoring import TwoPlayerGame
import chimera.decorators


class Chicken(TwoPlayerGame):
    """
    Implements the game of Chicken

    In each round of the game, each player can make only one
    of two moves: "swerve" and "don't swerve" (which we'll
    track using a boolean: Truw if the player swerves, False
    if the player doesn't swerve)

    Once both players have submitted their move, the outcome
    of the round is determined (note that one player can't
    see the move submitted by the other player until both
    of them have submitted their move). Each player will accrue
    some number of points depending on their moves:

      |------------|------------|-----------|-----------|
      | p1 swerve? | p2 swerve? | p1 points | p2 points |
      |------------|------------|-----------|-----------|
      |   TRUE     |   TRUE     |    1      |    1      |
      |   FALSE    |   TRUE     |    3      |    0      |
      |   TRUE     |   FALSE    |    0      |    3      |
      |   FALSE    |   FALSE    |    0      |    0      |
      |------------|------------|-----------|-----------|

    The players keep playing rounds of Chicken until
    both players decide not to swerve, at which point the
    game is over. The winner of the game will be the player
    who accrued the most points. It will, however, be a pyrrhic
    victory, as both players will be in the ICU after being
    involved in a horrific car crash in the final round.
    """

    #
    # Game initialization / cleanup
    #

    def __init__(self, game_options):
        super().__init__(game_options)
        self.points = None
        self.current_round = None
        self.round_outcomes = None

    def on_start(self):
        self.points = [0, 0]
        self.current_round = [None, None]
        self.round_outcomes = []

    def on_end(self):
        pass


    #
    # Game logic
    #

    def move(self, player, swerve):
        if self.current_round[player.id] is None:
            self.current_round[player.id] = swerve
        else:
            # TODO: Shouldn't be allowed to submit a move
            #       more than once per round
            pass

        p1_swerve = self.current_round[0]
        p2_swerve = self.current_round[1]
        if p1_swerve is not None and p2_swerve is not None:
            # Both players have submitted their move.
            # Determine the outcome of this round.
            if p1_swerve and p2_swerve:
                p1_points = 1
                p2_points = 1
            elif p1_swerve and not p2_swerve:
                p1_points = 0
                p2_points = 3
            elif not p1_swerve and p2_swerve:
                p1_points = 3
                p2_points = 0
            elif not p1_swerve and not p2_swerve:
                p1_points = 0
                p2_points = 0

            # Save the outcome
            round_outcome = (p1_swerve, p2_swerve, p1_points, p2_points)
            self.points[0] += p1_points
            self.points[1] += p2_points
            self.round_outcomes.append(round_outcome)
            self.current_round = [None, None]

            # The game state has changed
            self.notify_update()

    @property
    def done(self):
        if len(self.round_outcomes) > 0:
            # The game ends when neither of the players swerve
            p1_swerve, p2_swerve, _, _ = self.round_outcomes[-1]
            return not p1_swerve and not p2_swerve
        else:
            return False

    @property
    def winner(self):
        if self.done:
            if self.points[0] > self.points[1]:
                return self.get_player_by_id(0)
            elif self.points[0] < self.points[1]:
                return self.get_player_by_id(1)
            else:
                return None
        else:
            return None

    #
    # Chimera glue code
    #

    @chimera.decorators.expect_data(["swerve"])
    def action_move(self, player, data):
        swerve = data["swerve"]

        self.move(player, swerve)

        return {"swerve": data["swerve"]}

    @property
    def game_state(self):
        state = {}
        state["p1_points"] = self.points[0]
        state["p2_points"] = self.points[1]
        state["rounds"] = []
        for p1_swerve, p2_swerve, p1_points, p2_points in self.round_outcomes:
            round = {}
            round["p1_swerve"] = p1_swerve
            round["p2_swerve"] = p2_swerve
            round["p1_points"] = p1_points
            round["p2_points"] = p2_points
            state["rounds"].append(round)

        return state
