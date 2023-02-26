from chimera.authoring import TwoPlayerGame, TwoPlayerTurnBasedGame
import chimera.decorators


class PlayerOneWins(TwoPlayerTurnBasedGame):
    """
    Implements the game "Player One Wins", a fun game
    (for Player 1), because no matter what any of the players
    do, Player 1 always wins!

    The game involves a single round where Player 1 says a phrase,
    and then Player 2 says a phrase. Once both players have said
    a phrase, the game is over and, no matter what each player said,
    Player 1 always wins.
    """

    #
    # Game initialization / cleanup
    #

    def __init__(self, game_options):
        super().__init__(game_options)
        self.player_phrases = None

    def on_start(self):
        self.player_phrases = [None] * self.num_players

    def on_end(self):
        pass

    #
    # Game logic
    #

    def move(self, player, phrase):
        # Set the player's phrase
        self.player_phrases[player.id] = phrase

        # Turn advances to next player
        self.turn_to_next_player()

        # The game state has changed
        self.notify_update()

    @property
    def done(self):
        return all(phrase is not None for phrase in self.player_phrases)

    @property
    def winner(self):
        if self.done:
            return self.get_player_by_id(0)
        else:
            return None

    #
    # Chimera glue code
    #

    @property
    def game_state(self):
        return {"player1_phrase": self.player_phrases[0],
                "player2_phrase": self.player_phrases[1]}

    @chimera.decorators.validate_turn
    @chimera.decorators.expect_data(["phrase"])
    def action_move(self, player, data):
        phrase = data["phrase"]

        self.move(player, phrase)

        return {"received": data["phrase"]}