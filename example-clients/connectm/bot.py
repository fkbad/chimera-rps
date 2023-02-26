"""
Random Bot for Connect-M
"""

import sys
import random
import click

from chimera.common.utils import init_chimera
from chimera.client.api import Match
import chimera.exceptions as exc


def random_bot(match):

    # Keep looping until the match is done
    while match.status != Match.STATUS_DONE:

        # Wait for my turn
        turn = match.game_state["turn"]
        while turn != match.player_name and match.status != Match.STATUS_DONE:
            print(f"It is {turn}'s turn. Waiting for their move...")
            match.wait_for_update()
            turn = match.game_state["turn"]

        # While waiting for my turn, the other player
        # may have won, so we only make a move if
        # the match isn't done
        if match.status != Match.STATUS_DONE:

            # Get the status of the columns
            try:
                drop_info = match.game_action("drop_info")
            except exc.ChimeraClientException as e:
                print(f"ERROR: {e}")
                sys.exit(1)

            # Choose a column at random
            possible_cols = []
            for col, can_drop in enumerate(drop_info["can_drop"]):
                if can_drop:
                    possible_cols.append(col)

            col = random.choice(possible_cols)
            print(f"I have decided to drop a piece in column {col}")

            # Make the move
            try:
                match.game_action("drop", {"column": col})
            except exc.ChimeraClientException as e:
                print(f"ERROR: {e}")
                sys.exit(1)

            # Make sure we have the latest game state
            # before looping again
            match.wait_for_update()

    # Print the winner.
    if match.winner is not None:
        print(f"The winner is {match.winner}!")
    else:
        print("It's a tie!")


#
# Command-line interface
#

@click.command(name="connect4-bot")
@click.argument('MATCH_ID', type=click.STRING)
@click.option('--chimera-server', type=click.STRING, default="ws://127.0.0.1:14200")
@click.option('--bot-name', type=click.STRING, default="Chimera Bot")
def cmd(match_id, chimera_server, bot_name):
    # Call init_chimera to get a Match object
    chimera_match = init_chimera(chimera_server, bot_name, match_id)

    random_bot(chimera_match)


if __name__ == "__main__":
    cmd()
