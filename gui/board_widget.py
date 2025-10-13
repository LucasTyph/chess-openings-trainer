"""Simple chess board widget using a QTableWidget grid with rank/file labels."""
from __future__ import annotations

from typing import Iterable, Optional

import chess
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QTableWidget,
    QWidget,
    QLabel,
    QGridLayout,
)

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
LABEL_FONT = QFont("DejaVu Sans", 10)


def _rgb(qc: QColor) -> str:
    return f"{qc.red()},{qc.green()},{qc.blue()}"


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

        # Iterate table cells (row 0..7 top->bottom, col 0..7 left->right)
        for row in range(8):
            for col in range(8):
                # Determine which square this cell represents depending on orientation
                if not self._flipped:
                    display_row = 7 - row  # table row 0 -> rank 8, row 7 -> rank 1
                    display_col = col
                else:
                    display_row = row  # table row 0 -> rank 1 (flipped)
                    display_col = 7 - col

                square = chess.square(display_col, display_row)
                piece = board.piece_at(square)

                # Choose tile background color
                base_color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
                tile_color = HIGHLIGHT_COLOR if square in highlight else base_color
                bg_rgb = _rgb(tile_color)

                # Compute file letter and rank number for the given square (based on display coords)
                file_letter = chr(ord("a") + display_col)
                rank_number = str(display_row + 1)

                # Create cell container widget
                cell = QWidget()
                layout = QGridLayout(cell)
                layout.setContentsMargins(2, 2, 2, 2)
                layout.setSpacing(0)

                # Piece label (center)
                piece_label = QLabel()
                piece_label.setAttribute(Qt.WA_TranslucentBackground)
                piece_label.setAlignment(Qt.AlignCenter)
                piece_label.setFont(FONT)
                piece_label.setText(PIECE_SYMBOLS[piece.piece_type][piece.color] if piece else "")
                # Use the same text color for pieces (unicode glyphs differ between white/black pieces)
                piece_label.setStyleSheet("background: transparent;")

                # File label (bottom-left) — only on bottom table row
                file_label = QLabel()
                file_label.setFont(LABEL_FONT)
                file_label.setAttribute(Qt.WA_TranslucentBackground)
                file_label.setStyleSheet("background: transparent;")
                file_label.setText(file_letter if row == 7 else "")
                file_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

                # Rank label (top-right) — only on rightmost table column
                rank_label = QLabel()
                rank_label.setFont(LABEL_FONT)
                rank_label.setAttribute(Qt.WA_TranslucentBackground)
                rank_label.setStyleSheet("background: transparent;")
                rank_label.setText(rank_number if col == 7 else "")
                rank_label.setAlignment(Qt.AlignRight | Qt.AlignTop)

                # Choose a readable label color depending on tile brightness
                # Simple brightness heuristic: light tile -> dark text, dark tile -> light text
                if (base_color.red() * 0.299 + base_color.green() * 0.587 + base_color.blue() * 0.114) > 186:
                    label_color = "0,0,0"
                else:
                    label_color = "255,255,255"

                file_label.setStyleSheet(f"background: transparent; color: rgb({label_color});")
                rank_label.setStyleSheet(f"background: transparent; color: rgb({label_color});")

                # Set the background color on the container so transparent labels reveal it
                cell.setStyleSheet(f"background-color: rgb({bg_rgb});")

                # Add widgets to the same grid cell and align them accordingly (they will overlap)
                # We put them in a single 1x1 cell and rely on alignment flags
                layout.addWidget(piece_label, 0, 0, Qt.AlignCenter)
                layout.addWidget(file_label, 0, 0, Qt.AlignLeft | Qt.AlignBottom)
                layout.addWidget(rank_label, 0, 0, Qt.AlignRight | Qt.AlignTop)

                # Finally place the composed widget into the table
                self.setCellWidget(row, col, cell)

    def current_fen(self) -> Optional[str]:
        return self._current_fen
