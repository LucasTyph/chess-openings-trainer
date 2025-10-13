"""Core training loop that combines the repertoire and SRS managers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional

import chess

from .repertoire import RepertoireManager
from .srs import Card, SRSManager


@dataclass
class TrainingResult:
    fen: str
    success: bool
    expected_moves: Dict[str, str]
    provided_move: Optional[str]
    next_fen: Optional[str]
    message: str


class Trainer:
    """Coordinates repertoire lookups and SRS scheduling."""

    def __init__(self, repertoire: RepertoireManager, srs: SRSManager) -> None:
        self.repertoire = repertoire
        self.srs = srs

    def sync_with_repertoire(self) -> None:
        white_fens = list(self.repertoire.white_tree.keys())
        black_fens = list(self.repertoire.black_tree.keys())
        all_fens = white_fens + black_fens
        for fen in all_fens:
            self.srs.get(fen)
        self.srs.remove_cards(all_fens)

    def next_card(self, side: str, today: Optional[date] = None) -> Optional[Card]:
        # Only show cards for the selected side
        if side == "white":
            allowed_fens = set(self.repertoire.white_tree.keys())
        else:
            allowed_fens = set(self.repertoire.black_tree.keys())
        cards = [card for card in self.srs.due_cards(today=today) if card.fen in allowed_fens]
        return cards[0] if cards else None

    def available_moves(self, fen: str, side: str) -> Dict[str, str]:
        moves = self.repertoire.get_available_moves(fen, side)
        return dict(sorted(moves.items()))

    def _normalize_move(self, fen: str, move_text: str) -> Optional[str]:
        board = chess.Board(fen)
        text = move_text.strip()
        if not text:
            return None
        try:
            move = board.parse_san(text)
            return board.san(move)
        except ValueError:
            pass
        try:
            move = chess.Move.from_uci(text.lower())
        except ValueError:
            return None
        if move not in board.legal_moves:
            return None
        return board.san(move)

    def grade_answer(self, fen: str, move_text: str, side: str, success_grade: int = 5, failure_grade: int = 1) -> TrainingResult:
        available = self.available_moves(fen, side)
        if not available:
            return TrainingResult(
                fen=fen,
                success=False,
                expected_moves={},
                provided_move=None,
                next_fen=None,
                message="No moves stored for this position.",
            )

        normalized = self._normalize_move(fen, move_text)
        if normalized and normalized in available:
            next_fen = available[normalized]
            self.srs.schedule(fen, grade=success_grade)
            return TrainingResult(
                fen=fen,
                success=True,
                expected_moves=available,
                provided_move=normalized,
                next_fen=next_fen,
                message="Correct!",)
        else:
            self.srs.schedule(fen, grade=failure_grade)
            return TrainingResult(
                fen=fen,
                success=False,
                expected_moves=available,
                provided_move=normalized,
                next_fen=None,
                message="Incorrect. Review the expected move.",
            )

    def record_manual_grade(self, fen: str, grade: int) -> Card:
        return self.srs.schedule(fen, grade=grade)

    def cards_due_today(self, today: Optional[date] = None) -> List[Card]:
        return list(self.srs.due_cards(today=today))
