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

    def __init__(self, white_path: Path, black_path: Path) -> None:
        self.white_path = white_path
        self.black_path = black_path
        self._white_tree: RepertoireTree = {}
        self._black_tree: RepertoireTree = {}

    @property
    def white_tree(self) -> RepertoireTree:
        return self._white_tree

    @property
    def black_tree(self) -> RepertoireTree:
        return self._black_tree

    def load(self) -> None:
        raw_white = load_json(self.white_path)
        raw_black = load_json(self.black_path)
        if isinstance(raw_white, dict):
            self._white_tree = {
                fen: {move: next_fen for move, next_fen in moves.items() if isinstance(move, str) and isinstance(next_fen, str)}
                for fen, moves in raw_white.items()
                if isinstance(fen, str) and isinstance(moves, dict)
            }
        else:
            self._white_tree = {}
        if isinstance(raw_black, dict):
            self._black_tree = {
                fen: {move: next_fen for move, next_fen in moves.items() if isinstance(move, str) and isinstance(next_fen, str)}
                for fen, moves in raw_black.items()
                if isinstance(fen, str) and isinstance(moves, dict)
            }
        else:
            self._black_tree = {}

    def save(self) -> None:
        save_json(self.white_path, self._white_tree)
        save_json(self.black_path, self._black_tree)

    # repertoire operations
    def get_next_position(self, fen: str, move: str, side: str) -> Optional[str]:
        tree = self._white_tree if side == "white" else self._black_tree
        return tree.get(fen, {}).get(move)

    def get_available_moves(self, fen: str, side: str) -> Dict[str, str]:
        tree = self._white_tree if side == "white" else self._black_tree
        return dict(tree.get(fen, {}))

    def add_line(self, board: chess.Board, moves: Iterable[chess.Move], side: str) -> None:
        tree = self._white_tree if side == "white" else self._black_tree
        for move in moves:
            fen_before = board.fen()
            san_move = board.san(move)
            board.push(move)
            fen_after = board.fen()
            tree.setdefault(fen_before, {})[san_move] = fen_after

    def add_game(self, game: chess.pgn.Game, side: str) -> None:
        board = game.board()
        self.add_line(board, game.mainline_moves(), side)

    def import_pgn_white(self, source: Path) -> int:
        """Import a PGN file and merge it into the white repertoire."""
        count = 0
        with source.open("r", encoding="utf-8") as fh:
            while True:
                game = chess.pgn.read_game(fh)
                if game is None:
                    break
                self.add_game(game, side="white")
                count += 1
        return count

    def import_pgn_black(self, source: Path) -> int:
        """Import a PGN file and merge it into the black repertoire."""
        count = 0
        with source.open("r", encoding="utf-8") as fh:
            while True:
                game = chess.pgn.read_game(fh)
                if game is None:
                    break
                self.add_game(game, side="black")
                count += 1
        return count

    def to_dict(self, side: str) -> RepertoireTree:
        return self._white_tree if side == "white" else self._black_tree

    def replace(self, data: RepertoireTree) -> None:
        self._tree = data
