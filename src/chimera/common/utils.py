"""
Miscellaneous helper functions
"""
import sys

from typing import Optional
from urllib.parse import urlparse
from chimera.client import Chimera
from chimera.client.api import Match
import chimera.exceptions as exc


def init_chimera(server_uri: str, player_name, match_id: Optional[str]) -> Match:
    """ Connects to Chimera Server and creates or joins a match

    Args:
        server_uri: URI of the Chimera server
        player_name: Player Name
        match_id: If None, a new match will be created. If
           a string, then we will try to join that match.

    Returns: Chimera Match object

    """
    parsed_uri = urlparse(server_uri)
    hostname = parsed_uri.hostname
    port = parsed_uri.port

    # Connect to Chimera server
    try:
        chimera = Chimera(hostname, port)
    except exc.ChimeraConnectionRefusedException:
        print(f"ERROR: Could not connect to chimera server at {server_uri}")
        sys.exit(1)

    # Get list of games, and make sure "connectm" is supported
    games = chimera.get_games()
    if "connectm" not in games:
        print(f"ERROR: Server at {server_uri} does not support game 'connectm'")
        sys.exit(1)

    # Try to create or join a match.
    # If there is a duplicate player, we will try appending
    # the strings 2..9 to the player, and will give up after that.
    # TODO: Make this configurable
    suffix = None
    while True:
        try:
            if suffix is not None:
                pname = player_name + str(suffix)
            else:
                pname = player_name

            if match_id is None:
                match = games["connectm"].create_match(pname)
                print(f"Your match ID is {match.id}")
                print("Waiting for other player to join...")
                while match.status != Match.STATUS_IN_PROGRESS:
                    match.wait_for_update()
            else:
                match = games["connectm"].join_match(match_id, pname)
                while match.status != Match.STATUS_IN_PROGRESS:
                    match.wait_for_update()

            return match
        except exc.UnknownMatch:
            print(f"ERROR: No such match: {match_id}")
            sys.exit(1)
        except exc.AlreadyInAMatch:
            print(f"ERROR: You are already in another match (or are trying to join the same match twice)")
            sys.exit(1)
        except exc.DuplicatePlayer:
            if suffix is None:
                suffix = 2
            elif suffix == 9:
                print(f"ERROR: There is already a player called '{player_name}' in match '{match_id}")
                print(f"       (tried '{player_name}2' through '{player_name}9' and they were also taken)")
                sys.exit(1)
            else:
                suffix += 1
        except exc.ChimeraClientException as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    return match