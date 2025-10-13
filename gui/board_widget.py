"""Simple chess board widget using a QTableWidget grid."""
from __future__ import annotations

from typing import Iterable, Optional

import chess
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

PIECE_SYMBOLS = {
    chess.PAWN: {True: "♙", False: "♟"},
    chess.KNIGHT: {True: "♘", False: "♞"},
    chess.BISHOP: {True: "♗", False: "♝"},
    chess.ROOK: {True: "♖", False: "♜"},
    chess.QUEEN: {True: "♕", False: "♛"},
    chess.KING: {True: "♔", False: "♚"},
}

LIGHT_COLOR = QColor(240, 217, 181)
DARK_COLOR = QColor(181, 136, 99)
HIGHLIGHT_COLOR = QColor(246, 246, 105)
FONT = QFont("DejaVu Sans", 36)


class BoardWidget(QTableWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(8, 8, parent)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        for i in range(8):
            self.setColumnWidth(i, 64)
            self.setRowHeight(i, 64)
        self._current_fen: Optional[str] = None
        self._last_highlight: Optional[Iterable[int]] = None
        self._flipped: bool = False
        self.refresh(chess.STARTING_BOARD_FEN)

    def set_flipped(self, flipped: bool) -> None:
        self._flipped = flipped
        # Refresh board with current FEN to apply orientation
        if self._current_fen:
            self.refresh(self._current_fen)

    def refresh(self, fen: str, highlight: Optional[Iterable[chess.Square]] = None) -> None:
        board = chess.Board(fen)
        self._current_fen = fen
        highlight = set(highlight or [])
        for row in range(8):
            for col in range(8):
                # Flip board if needed
                display_row = 7 - row if not self._flipped else row
                display_col = col if not self._flipped else 7 - col
                square = chess.square(display_col, display_row)
                piece = board.piece_at(square)
                item = QTableWidgetItem()
                if piece:
                    symbol = PIECE_SYMBOLS[piece.piece_type][piece.color]
                    item.setText(symbol)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFont(FONT)
                color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
                if square in highlight:
                    color = HIGHLIGHT_COLOR
                item.setBackground(color)
                self.setItem(row, col, item)

    def current_fen(self) -> Optional[str]:
        return self._current_fen
