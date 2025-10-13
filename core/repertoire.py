"""Repertoire management utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

import chess
import chess.pgn

from .persistence import load_json, save_json

RepertoireTree = Dict[str, Dict[str, str]]


class RepertoireManager:
    """Load, update and query a repertoire stored as a FEN tree."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._tree: RepertoireTree = {}

    @property
    def tree(self) -> RepertoireTree:
        return self._tree

    def load(self) -> None:
        raw = load_json(self.path)
        if isinstance(raw, dict):
            self._tree = {
                fen: {move: next_fen for move, next_fen in moves.items() if isinstance(move, str) and isinstance(next_fen, str)}
                for fen, moves in raw.items()
                if isinstance(fen, str) and isinstance(moves, dict)
            }
        else:
            self._tree = {}

    def save(self) -> None:
        save_json(self.path, self._tree)

    # repertoire operations
    def get_next_position(self, fen: str, move: str) -> Optional[str]:
        return self._tree.get(fen, {}).get(move)

    def get_available_moves(self, fen: str) -> Dict[str, str]:
        return dict(self._tree.get(fen, {}))

    def add_line(self, board: chess.Board, moves: Iterable[chess.Move]) -> None:
        for move in moves:
            fen_before = board.fen()
            san_move = board.san(move)
            board.push(move)
            fen_after = board.fen()
            self._tree.setdefault(fen_before, {})[san_move] = fen_after

    def add_game(self, game: chess.pgn.Game) -> None:
        board = game.board()
        self.add_line(board, game.mainline_moves())

    def import_pgn(self, source: Path) -> int:
        """Import a PGN file and merge it into the repertoire.

        Returns the number of games processed.
        """
        count = 0
        with source.open("r", encoding="utf-8") as fh:
            while True:
                game = chess.pgn.read_game(fh)
                if game is None:
                    break
                self.add_game(game)
                count += 1
        return count

    def to_dict(self) -> RepertoireTree:
        return self._tree

    def replace(self, data: RepertoireTree) -> None:
        self._tree = data
