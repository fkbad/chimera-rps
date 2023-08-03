import click
import os
import json

from colorama import Fore, Style
from chimera.client.api import Match
import chimera.exceptions as exc

from chimera.common.utils import init_chimera

def print_winner(match: Match):
    """
    print the winner after a match is done
    """
    assert match.status == Match.STATUS_DONE
    print(f"Final Score:")
    print_points(match)
    print(f"the winner is {match.winner}")

def print_points(match: Match):
    """
    print the current score for the game
    """
    points = match.game_state["points"]
    print(json.dumps(points,indent=2))

def play_rps(match: Match) -> None:
    """
    Play Rock-Paper-Scissors on the terminal!

    Inputs:
        match: a Chimera Match object

    Outputs:
        nothing
    """
    while match.status != Match.STATUS_DONE:

        print_points(match)
        while True:
            player_input = input(Style.BRIGHT + f"{match.player_name}> " + Style.RESET_ALL)

            player_input = player_input.strip()
            try:
                match.game_action("move",data={"move": player_input})
                # successful game action breaks out of loop so we can wait for an update
                # from the server
                break
            except Exception as e:
                print(e)



        # add this or else the loop will eagerly get into the input 
        # and not actually display any updated
        match.wait_for_update()


        print(f"loop done")

    print(f"match done")
    print_winner(match)
        


@click.command(name="rps-tui")
@click.option('--chimera-server', type=click.STRING, default="ws://127.0.0.1:14200")
@click.option('--player-name', type=click.STRING)
@click.option('--join-match', type=click.STRING)
def cmd(chimera_server, player_name, join_match):

    if player_name is None:
        player_name = os.getlogin()

    if join_match is not None:
        match_id = join_match
    else:
        match_id = None

    # Call init_chimera to get a Match object
    chimera_match = init_chimera(chimera_server, player_name, match_id)

    play_rps(chimera_match)


if __name__ == "__main__":
    cmd()
