"""
GUI for Connect Four
"""

import os
import sys
from typing import Optional, List

from chimera.common.utils import init_chimera
from chimera.client.api import Match
import chimera.exceptions as exc

import click

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


WIDTH = 600
HEIGHT = 400


def draw_board(surface: pygame.surface.Surface, grid: List[List[Optional[str]]]) -> None:
    """ Draws the current state of the board in the window

    Args:
        surface: Pygame surface to draw the board on
        grid: The board to print

    Returns: None

    """
    nrows = len(grid)
    ncols = len(grid[0])

    surface.fill((64, 128, 255))

    # Compute the row height and column width
    rh = HEIGHT // nrows + 1
    cw = WIDTH // ncols + 1

    # Draw the borders around each cell
    for row in range(nrows):
        for col in range(ncols):
            rect = (col * cw, row * rh, cw, rh)
            pygame.draw.rect(surface, color=(32, 32, 192),
                             rect=rect, width=2)

    # Draw the circles
    for i, r in enumerate(grid):
        for j, v in enumerate(r):
            if v == " ":
                color = (255, 255, 255)
            elif v == "R":
                color = (255, 0, 0)
            elif v == "Y":
                color = (255, 255, 0)

            center = (j * cw + cw // 2, i * rh + rh // 2)
            radius = rh // 2 - 8
            pygame.draw.circle(surface, color=color,
                               center=center, radius=radius)


def play_connect_4(match: Match) -> None:
    """ Plays a game of Connect Four on a Pygame window

    Args:
        match: A Chimera Match object

    Returns: None

    """

    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("Connect Four")
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Update the display
    draw_board(surface, match.game_state["board"])
    pygame.display.update()

    # Keep looping until the match is done
    while match.status != Match.STATUS_DONE:
        # Wait for my turn
        turn = match.game_state["turn"]
        while turn != match.player_name and match.status != Match.STATUS_DONE:
            print(f"It is {turn}'s turn. Waiting for their move...")
            match.wait_for_update()
            turn = match.game_state["turn"]

        # Update the display
        draw_board(surface, match.game_state["board"])
        pygame.display.update()

        # While waiting for my turn, the other player
        # may have won
        if match.status == Match.STATUS_DONE:
            break

        # Process Pygame events
        # If a key is pressed, check whether it's
        # a column key (1-7).
        # If the user closes the window, quit the game.
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Check for key events
            if event.type == pygame.KEYUP:
                key = event.unicode
                if key in "1234567":
                    v = int(key)
                    try:
                        match.game_action("drop", {"column": int(v) - 1})
                        match.wait_for_update()

                        # Update the display
                        draw_board(surface, match.game_state["board"])
                        pygame.display.update()
                        continue
                    except exc.GameIncorrectMove:
                        pass
                    except exc.ChimeraClientException as e:
                        print(f"ERROR: {e}")
                        sys.exit(1)

        clock.tick(24)

    # Update the display
    draw_board(surface, match.game_state["board"])
    pygame.display.update()

    # Print the winner.
    if match.winner is not None:
        print(f"The winner is {match.winner}!")
    else:
        print("It's a tie!")


#
# Command-line interface
#

@click.command(name="connect4-gui")
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
