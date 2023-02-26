import copy
from enum import Enum
from typing import Optional, List

from chimera.exceptions import IncorrectMove, IncorrectActionData
from chimera.authoring import TwoPlayerGame, TwoPlayerTurnBasedGame
import chimera.decorators


PieceColor = Enum("PieceColor", ["RED", "YELLOW"])
"""
Enum type for representing piece colors.
"""


class ConnectMBoard:
    """
    Class for representing a Connect-M board
    """

    #
    # PRIVATE ATTRIBUTES
    #

    # The board itself
    _board: List[List[Optional[PieceColor]]]

    # Number of rows and columns
    _nrows: int
    _ncols: int

    # Number of contiguous pieces needed to win
    _m: int

    # The winner (if any) on the board
    _winner: Optional[PieceColor]

    #
    # PUBLIC METHODS
    #

    def __init__(self, nrows: int, ncols: int, m: int):
        """
        Constructor

        Args:
            nrows (int): Number of rows
            ncols (int): Number of columns
            m (int): Number of contiguous pieces needed to win
        """
        if nrows < m:
            raise ValueError(f"Number of rows ({nrows}) must be at least M ({m}")

        if ncols < m:
            raise ValueError(f"Number of columns ({ncols}) must be at least M ({m}")

        self._board = [[None] * ncols for _ in range(nrows)]
        self._top = [0] * ncols
        self._nrows = nrows
        self._ncols = ncols
        self._m = m
        self._winner = None

    def __str__(self) -> str:
        """ Returns a string representation of the board """
        s = "-" * self._ncols + "\n"
        for row in self._board:
            for value in row:
                if value is None:
                    s += " "
                else:
                    s += value.name[0]
            s += "\n"
        s += "-" * self._ncols

        return s

    #
    # PUBLIC METHODS
    #

    def can_drop(self, col: int) -> bool:
        """ Checks if a piece can be dropped into a column

        Args:
            col (int): Column index

        Raises:
            IndexError: if col is not a valid column index

        Returns:
            bool: True if a piece can be dropped in the
            specified column. False otherwise.

        """
        return self._top[col] < self._nrows

    def drop_wins(self, col: int, color: PieceColor) -> bool:
        """ Checks whether dropping a piece in this
        column will result in a win.

        Args:
            col: Column index
            color: Color of the piece to drop

        Raises:
            ValueError: if col is not a valid column index,
            or if the column is already full.

        Returns:
            bool: True if dropping a piece of the given
            color would result in a win; False otherwise.

        """
        # If we can't drop a piece in the column, it
        # naturally won't result in a win
        if not self.can_drop(col):
            return False

        # Temporarily drop the piece into the column,
        # check if there is a winner, and undo the drop
        row = self._top[col]
        self._set(row, col, color)
        winner = self._winner_at(row, col)
        self._set(row, col, None)

        return winner

    def drop(self, col: int, color: PieceColor) -> None:
        """ Drops a piece in a column

        Args:
            col: Column index
            color: Color of the piece to drop

        Raises:
            ValueError: if col is not a valid column index,
            or if the column is already full.

        Returns: None

        """
        if not self.can_drop(col):
            raise ValueError(f"Cannot drop a piece in column {col}")

        row = self._top[col]
        self._set(row, col, color)
        self._top[col] += 1

        if self._winner_at(row, col):
            self._winner = color

    def reset(self) -> None:
        """ Resets the board (removes all pieces)

        Args: None

        Returns: None

        """
        for row in self._board:
            for i, _ in enumerate(row):
                row[i] = None

        for i, _ in enumerate(self._top):
            self._top[i] = 0

        self._winner = None

    def is_done(self) -> bool:
        """ Checks whether the game is done

        A game can be done either because there is a winner,
        or because no more pieces can be dropped

        Args: None

        Returns:
            bool: True if the game is done. False otherwise.

        """
        if self.get_winner() is not None:
            return True
        else:
            # Check if all the columns are full
            for top_row in self._top:
                if top_row < self._nrows:
                    return False
            return True

    def get_winner(self) -> Optional[PieceColor]:
        """ Returns the winner (if any) in the board

        Returns:
            Optional[PieceColor]: If there is a winner,
            return its color. Otherwise, return None.

        """
        return self._winner

    def get_num_cols(self) -> int:
        """ Returns the number of columns in the board"""
        return self._ncols

    def to_piece_grid(self) -> List[List[Optional[PieceColor]]]:
        """ Returns the board as a list of list of PieceColors

        Not suitable for JSON serialization, but can be useful
        to display the board in a GUI or TUI.

        Returns:
            list[list[PieceColor]]: A list of lists with the same
            dimensions as the board. In each row, the values
            in the list will be None (no piece), PieceColor.RED
            (red piece), or PieceColor.YELLOW (yellow piece)
        """

        # The expected return type happens to be our internal
        # representation for the board, so we just return a copy
        return copy.deepcopy(self._board)

    def to_str_grid(self) -> List[List[str]]:
        """ Returns the board as a list of list of strings

        The returned list is suitable for JSON serialization.

        Returns:
            list[list[str]]: A list of lists with the same
            dimensions as the board. In each row, the values
            in the list will be " " (no piece), "R" (red piece),
            or "Y" (yellow piece)
        """
        rv = []
        for row in self._board:
            lst = []
            for value in row:
                if value is None:
                    lst.append(" ")
                else:
                    lst.append(value.name[0])
            rv.append(lst)
        return rv

    #
    # PRIVATE METHODS
    #

    def _get(self, row: int, col: int) -> Optional[PieceColor]:
        """ Gets piece color (if any) at a given location.

        Rows are numbered from 0 starting at the bottom of the board.

        Args:
            row (int): Row index
            col (int): Column index

        Returns:
            Optional[PieceColor]: If there is a piece in the provided
            location, returns the PieceColor object at that location.
            Otherwise, returns None. Also returns None if the (row, col)
            coordinates are not valid.
        """
        if not (0 <= row < self._nrows):
            return None
        elif not (0 <= col < self._ncols):
            return None
        else:
            return self._board[(self._nrows - 1) - row][col]

    def _set(self, row: int, col: int, color: Optional[PieceColor]) -> None:
        """ Sets piece color at a given location.

        Rows are numbered from 0 starting at the bottom of the board.

        Args:
            row (int): Row index
            col (int): Column index
            color (Optional[PieceColor]): Color to set the location to.
              Can also be None to clear the piece in that location.

        Raises:
            ValueError: If the provided location is not valid

        Returns: None
        """
        assert 0 <= row < self._nrows
        assert 0 <= col < self._ncols

        self._board[(self._nrows - 1) - row][col] = color

    def _winner_at(self, row: int, col: int) -> bool:
        """ Checks for a winner at a location

        Checks whether the specified location contains
        a winning row, column, or diagonal.

        Args:
            row (int): Row index
            col (int): Column index

        Returns:
            bool: True if there is a winner at the specified
            location. False otherwise.
        """

        dirs = [(+1, -1), (+1, 0), (+1, +1),
                ( 0, -1),          ( 0, +1),
                (-1, -1), (-1, 0), (-1, +1)]

        # For every possible direction, count the number
        # of adjacent pieces, up to a maximum on m-1
        adj_dir = {}
        origin_piece = self._get(row, col)
        for dr, dc in dirs:
            adj_dir[(dr, dc)] = 0

            # Start at the 'origin' (row, col)
            ir, ic = row, col
            for _ in range(self._m-1):
                # At each step, add the direction (dr, dc)
                # Get the piece at that location, and compare
                # it with the original piece
                ir, ic = ir + dr, ic + dc
                piece = self._get(ir, ic)
                if piece == origin_piece:
                    adj_dir[(dr, dc)] += 1
                else:
                    break

            # If there are M-1 adjacent pieces in this
            # direction, we know we have a winner.
            if adj_dir[(dr, dc)] == self._m - 1:
                return True

        # If after looking in each direction we didn't see
        # M contiguous piece, we now need to check whether
        # adding the contiguous pieces along a row, column,
        # or the two diagonals yields a winner.

        # Rows
        if adj_dir[(0, -1)] + 1 + adj_dir[(0, +1)] >= self._m:
            return True

        # Columns
        if adj_dir[(+1, 0)] + 1 + adj_dir[(-1, 0)] >= self._m:
            return True

        # Diagonal \
        if adj_dir[(+1, -1)] + 1 + adj_dir[(-1, +1)] >= self._m:
            return True

        # Diagonal /
        if adj_dir[(-1, -1)] + 1 + adj_dir[(+1, +1)] >= self._m:
            return True

        return False


class ConnectM(TwoPlayerTurnBasedGame):

    def __init__(self, game_options):
        super().__init__(game_options)
        self._board = ConnectMBoard(6, 7, 4)
        self._player_color = {}
        self._color_player = {}

    def on_start(self):
        player1 = self.get_player_by_id(0)
        player2 = self.get_player_by_id(1)

        self._player_color[player1] = PieceColor.RED
        self._player_color[player2] = PieceColor.YELLOW

        self._color_player[PieceColor.RED] = player1
        self._color_player[PieceColor.YELLOW] = player2

    def on_end(self):
        pass

    #
    # Game logic
    #

    def drop(self, player, column):
        try:
            if not self._board.can_drop(column):
                raise IncorrectMove(f"Cannot drop piece in column {column}")
        except IndexError:
            raise IncorrectMove(f"Incorrect column number: {column}")

        color = self._player_color[player]

        self._board.drop(column, color)

        # Turn advances to next player
        self.turn_to_next_player()

        # The game state has changed
        self.notify_update()

    @property
    def done(self):
        return self._board.get_winner() is not None

    @property
    def winner(self):
        winning_color = self._board.get_winner()

        if winning_color is None:
            return None
        else:
            return self._color_player[winning_color]

    #
    # Chimera glue code
    #

    @chimera.decorators.validate_turn
    @chimera.decorators.expect_data(["column"])
    def action_drop(self, player, data):
        column = data["column"]

        if not isinstance(column, int):
            raise IncorrectActionData(f"Provided column is not an integer: {column}")

        self.drop(player, column)

        return {"column": data["column"]}

    @chimera.decorators.expect_data([])
    def action_drop_info(self, player, data):

        rv = {"can_drop": [], "drop_wins": {"Y":[], "R":[]}}

        for col in range(self._board.get_num_cols()):
            can_drop = self._board.can_drop(col)
            rv["can_drop"].append(can_drop)

            drop_wins_y = self._board.drop_wins(col, PieceColor.YELLOW)
            rv["drop_wins"]["Y"].append(drop_wins_y)
            drop_wins_r = self._board.drop_wins(col, PieceColor.YELLOW)
            rv["drop_wins"]["R"].append(drop_wins_r)

        return rv

    @property
    def game_state(self):
        player1 = self.get_player_by_id(0)
        player2 = self.get_player_by_id(1)

        player1_color = self._player_color[player1]
        player2_color = self._player_color[player2]

        state = {}
        state["turn"] = self.current_player.name
        state["players"] = {player1.name: player1_color.name[0],
                            player2.name: player2_color.name[0]}
        state["board"] = self._board.to_str_grid()

        return state
