"""
TUI for Connect Four
"""
import sys
import os
from typing import Optional, List

import click
from colorama import Fore, Style

from chimera.client.api import Match
import chimera.exceptions as exc

from chimera.common.utils import init_chimera


def print_board(grid: List[List[Optional[str]]]) -> None:
    """ Prints the board to the screen

    Args:
        grid: The board to print

    Returns: None
    """

    nrows = len(grid)
    ncols = len(grid[0])

    # Top row
    print(Fore.BLUE + "┌" + ("─┬" * (ncols-1)) + "─┐")

    for r in range(nrows):
        crow = "│"
        for c in range(ncols):
            v = grid[r][c]
            if v == " ":
                crow += " "
            elif v == "R":
                crow += Fore.RED + Style.BRIGHT + "●"
            elif v == "Y":
                crow += Fore.YELLOW + Style.BRIGHT + "●"
            crow += Fore.BLUE + Style.NORMAL + "│"
        print(crow)

        if r < nrows - 1:
            print(Fore.BLUE + "├" + ("─┼" * (ncols-1)) + "─┤")
        else:
            print(Fore.BLUE + "└" + ("─┴" * (ncols-1)) + "─┘" + Style.RESET_ALL)


def play_connect_4(match: Match) -> None:
    """ Plays a game of Connect Four on the terminal through a Chimera server

    Args:
        match: A Chimera Match object

    Returns: None

    """

    # Print the board
    print()
    print_board(match.game_state["board"])
    print()

    # Keep looping until the match is done
    while match.status != Match.STATUS_DONE:

        # Wait for my turn
        turn = match.game_state["turn"]
        while turn != match.player_name and match.status != Match.STATUS_DONE:
            print(f"It is {turn}'s turn. Waiting for their move...")
            match.wait_for_update()
            turn = match.game_state["turn"]

        # While waiting for my turn, the other player
        # may have won, so I only ask for a move
        # if the match is still in progress.
        if match.status != Match.STATUS_DONE:
            # Print the board
            print()
            print_board(match.game_state["board"])
            print()

            # Ask for a column number (and keep asking if an
            # incorrect column number is provided)
            while True:
                v = input(Style.BRIGHT + f"{match.player_name}> " + Style.RESET_ALL)
                if not v.isnumeric():
                    continue
                try:
                    match.game_action("drop", {"column": int(v)-1})
                    break
                except exc.GameIncorrectMove:
                    pass
                except exc.ChimeraClientException as e:
                    print(f"ERROR: {e}")
                    sys.exit(1)

            match.wait_for_update()

        # Print the board
        print()
        print_board(match.game_state["board"])
        print()

    # Print the winner.
    if match.winner is not None:
        print(f"The winner is {match.winner}!")
    else:
        print("It's a tie!")


#
# Command-line interface
#

@click.command(name="connect4-tui")
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

    play_connect_4(chimera_match)


if __name__ == "__main__":
    cmd()
