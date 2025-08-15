import numpy as np
from functools import lru_cache


class GameState:
    EMPTY = 0
    RED = 1
    YELLOW = 2
    NOONE = -1

    def __init__(self, rows=6, cols=7, state=None, move_count=0):
        self.rows = rows
        self.cols = cols
        if state is None:
            self.state = np.zeros((rows, cols), dtype=np.int8)
        else:
            self.state = np.copy(state)
        self.move_count = move_count

    @lru_cache(maxsize=None)
    def getChainsOptimized(self, player):
        """
        Returns True if player has a chain of 4 or more.
        Optimized for speed by using NumPy operations for diagonal checks.
        """
        rows = self.rows
        cols = self.cols
        state = self.state

        # Pre-calculate bounds for efficiency.
        # These represent the maximum starting row/column index for a 4-in-a-row to fit.
        rows_check_limit = (
            rows - 3
        )  # e.g., for 6 rows, can start at row 0,1,2 (0-indexed)
        cols_check_limit = (
            cols - 3
        )  # e.g., for 7 cols, can start at col 0,1,2,3 (0-indexed)

        # Iterate through each cell on the board
        for r in range(rows):
            for c in range(cols):
                # If the current cell doesn't belong to the player, skip checks from here
                if state[r, c] != player:
                    continue

                # --- Check Horizontal (4 in a row) ---
                # Ensure there's enough space to the right for a 4-in-a-row
                if c < cols_check_limit:
                    # Use np.all on a slice for fast check
                    if np.all(state[r, c : c + 4] == player):
                        return True

                # --- Check Vertical (4 in a column) ---
                # Ensure there's enough space downwards for a 4-in-a-row
                if r < rows_check_limit:
                    # Use np.all on a slice for fast check
                    if np.all(state[r : r + 4, c] == player):
                        return True

                # --- Check Diagonal / (top-right to bottom-left) ---
                # This diagonal goes up-right from (r,c) -> (r-1, c+1) -> (r-2, c+2) -> (r-3, c+3)
                # Requires starting row 'r' to be at least 3 (to go up 3 steps)
                # Requires starting col 'c' to have enough space to the right (c <= cols - 4)
                if r >= 3 and c < cols_check_limit:
                    # Explicitly create a small NumPy array from the 4 diagonal elements
                    # and then use np.all for a fast check.
                    if np.all(
                        np.array(
                            [
                                state[r, c],
                                state[r - 1, c + 1],
                                state[r - 2, c + 2],
                                state[r - 3, c + 3],
                            ]
                        )
                        == player
                    ):
                        return True

                # --- Check Diagonal \ (top-left to bottom-right) ---
                # This diagonal goes down-right from (r,c) -> (r+1, c+1) -> (r+2, c+2) -> (r+3, c+3)
                # Requires starting row 'r' to have enough space downwards (r <= rows - 4)
                # Requires starting col 'c' to have enough space to the right (c <= cols - 4)
                if r < rows_check_limit and c < cols_check_limit:
                    # Explicitly create a small NumPy array from the 4 diagonal elements
                    # and then use np.all for a fast check.
                    if np.all(
                        np.array(
                            [
                                state[r, c],
                                state[r + 1, c + 1],
                                state[r + 2, c + 2],
                                state[r + 3, c + 3],
                            ]
                        )
                        == player
                    ):
                        return True
        return False

    def getChains(self, player):
        """Returns True if player has a chain of 4 or more."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.state[r, c] != player:
                    continue
                # Horizontal
                if c <= self.cols - 4 and np.all(self.state[r, c : c + 4] == player):
                    return True
                # Vertical
                if r <= self.rows - 4 and np.all(self.state[r : r + 4, c] == player):
                    return True
                # Diagonal /
                if (
                    r >= 3
                    and c <= self.cols - 4
                    and all(self.state[r - i, c + i] == player for i in range(4))
                ):
                    return True
                # Diagonal \
                if (
                    r <= self.rows - 4
                    and c <= self.cols - 4
                    and all(self.state[r + i, c + i] == player for i in range(4))
                ):
                    return True
        return False

    @property
    def possible_next_moves(self):
        """Returns a list of columns (indices) where a token can be dropped."""
        return [c for c in range(self.cols) if self.state[0, c] == self.EMPTY]

    @property
    def next_player(self):
        """Returns the player index for the next move."""
        return self.RED if self.move_count % 2 == 0 else self.YELLOW

    @property
    def next_player_str(self):
        return "RED" if self.next_player == self.RED else "YELLOW"

    def applyMove(self, col):
        """Returns a new GameState after applying a move in the given column."""
        if self.state[0, col] != self.EMPTY:
            raise ValueError("Column is full")
        new_state = np.copy(self.state)
        for row in range(self.rows - 1, -1, -1):
            if new_state[row, col] == self.EMPTY:
                new_state[row, col] = self.next_player
                break
        return GameState(self.rows, self.cols, new_state, self.move_count + 1)

    def removeMove(self, col):
        """Returns a new GameState after removing/unapplying the move in the given column"""
        pass

    def __str__(self):
        """Returns a string representation of the game state."""
        symbols = {self.EMPTY: ".", self.RED: "R", self.YELLOW: "Y"}
        return (
            "\n".join(
                " ".join(symbols[self.state[r, c]] for c in range(self.cols))
                for r in range(self.rows)
            )
            + f"\n{symbols[self.next_player]} to play"
        )

    def __eq__(self, other):
        """Checks if two game states are equal."""
        if not isinstance(other, GameState):
            return False
        return (
            self.rows == other.rows
            and self.cols == other.cols
            and np.array_equal(self.state, other.state)
            and self.move_count == other.move_count
        )

    def __hash__(self):
        """Returns a hash of the game state."""
        return hash((self.rows, self.cols, self.state.tobytes(), self.move_count))

    @lru_cache(maxsize=None)
    def isTerminal(self):
        """Checks if the game state is terminal (i.e., a player has won or the board is full)."""
        return (
            self.getChainsOptimized(self.RED)
            or self.getChainsOptimized(self.YELLOW)
            or self.move_count == self.rows * self.cols
        )

    @lru_cache(maxsize=None)
    def getWinner(self):
        """Returns the winner of the game if there is one, otherwise returns None."""
        if self.getChainsOptimized(self.RED):
            return self.RED
        elif self.getChainsOptimized(self.YELLOW):
            return self.YELLOW
        elif self.move_count == self.rows * self.cols:
            return self.NOONE
        else:
            return None

    def reset(self):
        """Resets the game state to the initial state."""
        self.state = np.zeros((self.rows, self.cols), dtype=np.int8)
        self.move_count = 0
        return self

    def copy(self):
        """Returns a copy of the game state."""
        return GameState(self.rows, self.cols, np.copy(self.state), self.move_count)

    # def __repr__(self):
    #     """Returns a string representation of the game state for debugging."""
    #     return f"GameState(rows={self.rows}, cols={self.cols}, move_count={self.move_count}, state=\n{self.state})"

    # def to_tuple(self):
    #     """Returns a tuple representation of the game state."""
    #     return (self.rows, self.cols, tuple(map(tuple, self.state)), self.move_count)

    # @classmethod
    # def from_tuple(cls, state_tuple):
    #     """Creates a GameState from a tuple representation."""
    #     rows, cols, state, move_count = state_tuple
    #     state_array = np.array(state, dtype=np.int8)
    #     return cls(rows, cols, state_array, move_count)

    # def __getstate__(self):
    #     """Returns the state for pickling."""
    #     return self.to_tuple()

    # def __setstate__(self, state_tuple):
    #     """Sets the state from a tuple for unpickling."""
    #     game_state = self.from_tuple(state_tuple)
    #     self.rows = game_state.rows
    #     self.cols = game_state.cols
    #     self.state = game_state.state
    #     self.move_count = game_state.move_count

    # def __reduce__(self):
    #     """Returns a tuple for pickling."""
    #     return (self.__class__, (self.rows, self.cols, self.state, self.move_count))

    # def __len__(self):
    #     """Returns the number of moves made in the game."""
    #     return self.move_count

    # def __contains__(self, col):
    #     """Checks if a column is a valid move."""
    #     return 0 <= col < self.cols and self.state[0, col] == self.EMPTY

    # def __iter__(self):
    #     """Returns an iterator over the columns."""
    #     return (c for c in range(self.cols) if self.state[0, c] == self.EMPTY)

    # def __getitem__(self, col):
    #     """Returns the topmost row of the specified column."""
    #     if col < 0 or col >= self.cols:
    #         raise IndexError("Column index out of range")
    #     for row in range(self.rows):
    #         if self.state[row, col] != self.EMPTY:
    #             return self.state[row, col]
    #     return self.EMPTY

    # def __setitem__(self, col, player):
    #     """Sets the topmost row of the specified column to the given player."""
    #     if col < 0 or col >= self.cols:
    #         raise IndexError("Column index out of range")
    #     if player not in (self.RED, self.YELLOW):
    #         raise ValueError("Invalid player")
    #     for row in range(self.rows - 1, -1, -1):
    #         if self.state[row, col] == self.EMPTY:
    #             self.state[row, col] = player
    #             break
    #     else:
    #         raise ValueError("Column is full")

    # def __delitem__(self, col):
    #     """Removes the topmost token from the specified column."""
    #     if col < 0 or col >= self.cols:
    #         raise IndexError("Column index out of range")
    #     for row in range(self.rows - 1, -1, -1):
    #         if self.state[row, col] != self.EMPTY:
    #             self.state[row, col] = self.EMPTY
    #             break
    #     else:
    #         raise ValueError("Column is already empty")

    # def __bool__(self):
    #     """Returns True if the game state is not empty."""
    #     return np.any(self.state != self.EMPTY)

    # def __nonzero__(self):
    #     """Python 2 compatibility for boolean evaluation."""
    #     return self.__bool__()

    # def __format__(self, format_spec):
    #     """Formats the game state for printing."""
    #     symbols = {self.EMPTY: ".", self.RED: "R", self.YELLOW: "Y"}
    #     formatted_rows = []
    #     for r in range(self.rows):
    #         formatted_row = " ".join(symbols[self.state[r, c]] for c in range(self.cols))
    #         formatted_rows.append(formatted_row)

    #     return "\n".join(formatted_rows)

    # def __dir__(self):
    #     """Returns a list of attributes and methods of the game state."""
    #     return super().__dir__() + [
    #         "EMPTY", "RED", "YELLOW", "get_chains", "possible_next_moves",
    #         "next_player", "apply_move", "is_terminal", "get_winner",
    #         "reset", "copy", "to_tuple", "from_tuple"
    #     ]

    # def __getattr__(self, name):


class MCTSGameState:
    def __init__(self, state: GameState, parent_state=None, last_move=-1):
        self.state = state
        num_moves = state.cols

        self.w = 0  # Total Action Value to get to this state from its parent (from immediate previous player's perspective)
        self.q = 0  # Mean Action value to get to this state from its parent (from immediate previous player's perspective)
        self.v = 0  # State value for this state (from immediate previous player's perspective)
        self.visits = 0  # Visits to this state

        self.prior = np.array(
            [0] * num_moves, dtype=np.float32
        )  # Prior (action probabilities for children)

        self.is_leaf = True
        self.children = None
        self.parent: MCTSGameState = parent_state
        self.last_move: int = last_move

    @classmethod
    def createMCTSState(cls, state, parent=None, last_move=-1):
        if state == None:
            return None
        else:
            return MCTSGameState(state, parent, last_move)

    def isTerminal(self):
        return self.state.isTerminal()

    def createChildrenStates(self) -> bool:
        if self.state.isTerminal() == True:
            return False
        else:
            children = [None] * self.state.cols
            next_moves = self.state.possible_next_moves
            for move in next_moves:
                children[move] = self.state.applyMove(move)

            self.children = [
                MCTSGameState.createMCTSState(state, self, move)
                for move, state in enumerate(children)
            ]
            self.is_leaf = False

            return True

    @property
    def next_player(self):
        return self.state.next_player
