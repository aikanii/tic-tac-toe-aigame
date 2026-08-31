"""
game_engine.py
--------------
Pure game logic for Tic-Tac-Toe: board state, move validation, win/draw
detection, and move history. Has zero dependency on any AI/agent framework
so it can be unit-tested and reused on its own.
"""

from dataclasses import dataclass, field
from typing import List, Optional


WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6),             # diagonals
]


@dataclass
class Move:
    player: str          # "X" or "O"
    position: int         # 0-8
    reasoning: str = ""   # the agent's stated reasoning for this move
    board_after: str = "" # snapshot of the board after this move
    duration_s: float = 0.0


@dataclass
class GameState:
    board: List[str] = field(default_factory=lambda: [""] * 9)
    history: List[Move] = field(default_factory=list)
    current_player: str = "X"
    winner: Optional[str] = None      # "X", "O", "Draw", or None
    winning_line: Optional[tuple] = None

    def reset(self):
        self.board = [""] * 9
        self.history = []
        self.current_player = "X"
        self.winner = None
        self.winning_line = None

    def available_moves(self) -> List[int]:
        return [i for i, cell in enumerate(self.board) if cell == ""]

    def is_valid_move(self, position: int) -> bool:
        return isinstance(position, int) and 0 <= position <= 8 and self.board[position] == ""

    def apply_move(self, player: str, position: int, reasoning: str = "", duration_s: float = 0.0) -> Move:
        if self.winner is not None:
            raise ValueError("Game already finished.")
        if player != self.current_player:
            raise ValueError(f"It is not {player}'s turn.")
        if not self.is_valid_move(position):
            raise ValueError(f"Position {position} is not a legal move.")

        self.board[position] = player
        move = Move(
            player=player,
            position=position,
            reasoning=reasoning,
            board_after=self.board_to_string(),
            duration_s=duration_s,
        )
        self.history.append(move)

        self._check_game_over()
        if self.winner is None:
            self.current_player = "O" if player == "X" else "X"

        return move

    def _check_game_over(self):
        for line in WIN_LINES:
            a, b, c = line
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                self.winner = self.board[a]
                self.winning_line = line
                return
        if not self.available_moves():
            self.winner = "Draw"

    def board_to_string(self) -> str:
        """Human/LLM-readable board, positions shown for empty cells."""
        rows = []
        for r in range(3):
            cells = []
            for c in range(3):
                idx = r * 3 + c
                cells.append(self.board[idx] if self.board[idx] else str(idx))
            rows.append(" | ".join(cells))
        return "\n---------\n".join(rows)

    def is_over(self) -> bool:
        return self.winner is not None


if __name__ == "__main__":
    # Quick self-test
    gs = GameState()
    print(gs.board_to_string())
    gs.apply_move("X", 4)
    gs.apply_move("O", 0)
    gs.apply_move("X", 1)
    gs.apply_move("O", 8)
    gs.apply_move("X", 7)  # X: 4,1,7 -> vertical win on column 1 (1,4,7)
    print(gs.board_to_string())
    print("Winner:", gs.winner, "Line:", gs.winning_line)
    assert gs.winner == "X"
    assert gs.winning_line == (1, 4, 7)
    print("Self-test passed.")