"""Main window for the Chess Opening Trainer application."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import chess
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.repertoire import RepertoireManager
from core.trainer import Trainer
from core.srs import Card, SRSManager
from .board_widget import BoardWidget
from .dialogs import StatsDialog


class MainWindow(QMainWindow):
    def __init__(self, srs: SRSManager, trainer: Trainer, data_dir: Path) -> None:
        super().__init__()
        # Use two separate repertoire files for white and black
        self.white_repertoire_path = data_dir / "repertoire_white.json"
        self.black_repertoire_path = data_dir / "repertoire_black.json"
        self.repertoire = RepertoireManager(self.white_repertoire_path, self.black_repertoire_path)
        self.srs = srs
        self.trainer = trainer
        self.data_dir = data_dir
        self.current_card: Optional[Card] = None
        self.training_side = "white"  # default side to train

        self.setWindowTitle("Chess Opening Trainer")
        self.resize(720, 820)
        self._build_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self.statusBar().showMessage("Ready")
        self._latest_stats = self.srs.statistics()
        self.refresh_state()

    def _build_ui(self) -> None:
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignTop)

        self.board = BoardWidget(self)
        layout.addWidget(self.board)

        self.due_label = QLabel("Due today: 0", self)
        layout.addWidget(self.due_label)

        self.position_label = QLabel("", self)
        self.position_label.setWordWrap(True)
        layout.addWidget(self.position_label)

        self.move_input = QLineEdit(self)
        self.move_input.setPlaceholderText("Enter your move in SAN (e.g. Nf3) or UCI (e2e4)")
        layout.addWidget(self.move_input)

        self.feedback_label = QLabel("", self)
        self.feedback_label.setWordWrap(True)
        layout.addWidget(self.feedback_label)

        self.check_button = QPushButton("Check Move", self)
        self.check_button.clicked.connect(self.on_check_move)
        layout.addWidget(self.check_button)

        self.forgot_button = QPushButton("I Forgot", self)
        self.forgot_button.clicked.connect(self.on_mark_incorrect)
        layout.addWidget(self.forgot_button)

        self.correct_button = QPushButton("Mark Correct", self)
        self.correct_button.clicked.connect(self.on_mark_correct)
        layout.addWidget(self.correct_button)

        self.skip_button = QPushButton("Skip", self)
        self.skip_button.clicked.connect(self.load_next_card)
        layout.addWidget(self.skip_button)

        self.switch_side_button = QPushButton("Switch Training Side", self)
        self.switch_side_button.clicked.connect(self.set_training_side)
        layout.addWidget(self.switch_side_button)

        self.setCentralWidget(central)

    def _create_actions(self) -> None:
        self.import_action = QAction("Import PGN", self)
        self.import_action.triggered.connect(self.import_pgn)

        self.export_action = QAction("Export Repertoire", self)
        self.export_action.triggered.connect(self.export_repertoire)

        self.show_stats_action = QAction("Show Statistics", self)
        self.show_stats_action.triggered.connect(self.show_statistics)

        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.close)

    def _create_menus(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.import_action)
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.show_stats_action)

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.addAction(self.import_action)
        toolbar.addAction(self.show_stats_action)
        self.addToolBar(toolbar)

    def refresh_state(self) -> None:
        self.trainer.sync_with_repertoire()
        self.repertoire.save()
        self.srs.save()
        self._latest_stats = self.srs.statistics()
        self.load_next_card()

    def import_pgn(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Import PGN", str(self.data_dir), "PGN Files (*.pgn)")
        if not filename:
            return
        path = Path(filename)
        # Ask user which side to import for
        side, ok = self._ask_side_dialog("Which side is this PGN for?")
        if not ok:
            return
        try:
            if side == "white":
                games = self.repertoire.import_pgn_white(path)
            else:
                games = self.repertoire.import_pgn_black(path)
            self.repertoire.save()
            self.statusBar().showMessage(f"Imported {games} games for {side} from {path.name}")
        except Exception as exc:
            QMessageBox.critical(self, "Import Error", f"Failed to import PGN: {exc}")
            return
        self.refresh_state()

    def _ask_side_dialog(self, prompt: str):
        from PyQt5.QtWidgets import QInputDialog
        sides = ["white", "black"]
        side, ok = QInputDialog.getItem(self, "Select Side", prompt, sides, 0, False)
        return side, ok

    def export_repertoire(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Export Repertoire", str(self.data_dir / "repertoire_export.json"), "JSON Files (*.json)")
        if not filename:
            return
        try:
            data = json.dumps(self.repertoire.tree, indent=2, sort_keys=True)
            Path(filename).write_text(data, encoding="utf-8")
            QMessageBox.information(self, "Export Complete", f"Repertoire exported to {filename}")
        except Exception as exc:  # noqa: BLE001 - show error to user
            QMessageBox.critical(self, "Export Error", f"Failed to export repertoire: {exc}")

    def show_statistics(self) -> None:
        stats = self.srs.statistics()
        dialog = StatsDialog(self.srs.all_cards().values(), stats, self)
        dialog.exec_()

    def load_next_card(self) -> None:
        card = self.trainer.next_card()
        self.current_card = card
        self._latest_stats = self.srs.statistics()
        self._update_summary_labels()
        # Flip board if training side is black
        self.board.set_flipped(self.training_side == "black")
        if card is None:
            self.board.refresh(chess.STARTING_BOARD_FEN)
            self.feedback_label.setText("No cards due for review. Import a PGN or wait until the next review date.")
            self.position_label.setText("")
            self.check_button.setEnabled(False)
            self.forgot_button.setEnabled(False)
            self.correct_button.setEnabled(False)
            return

        self.check_button.setEnabled(True)
        self.forgot_button.setEnabled(True)
        self.correct_button.setEnabled(True)
        self.board.refresh(card.fen)
        self.position_label.setText(f"Current position FEN: {card.fen} | Training side: {self.training_side}")
        self.feedback_label.setText("Enter your prepared move and press 'Check Move'.")
        self.move_input.clear()
        self.move_input.setFocus()

    def set_training_side(self):
        side, ok = self._ask_side_dialog("Which side do you want to train?")
        if ok:
            self.training_side = side
            self.board.set_flipped(self.training_side == "black")
            self.load_next_card()

    def on_check_move(self) -> None:
        if self.current_card is None:
            return
        move_text = self.move_input.text()
        result = self.trainer.grade_answer(self.current_card.fen, move_text, self.training_side)
        self._handle_training_result(result)

    def on_mark_incorrect(self) -> None:
        if self.current_card is None:
            return
        result = self.trainer.grade_answer(self.current_card.fen, "", self.training_side, success_grade=5, failure_grade=1)
        self._handle_training_result(result, override_message="Marked as incorrect. Review the expected move.")

    def on_mark_correct(self) -> None:
        if self.current_card is None:
            return
        self.trainer.record_manual_grade(self.current_card.fen, grade=5)
        self.feedback_label.setText("Marked as correct.")
        self.srs.save()
        self.load_next_card()

    def _handle_training_result(self, result, override_message: Optional[str] = None) -> None:
        expected_moves = ", ".join(result.expected_moves.keys()) if result.expected_moves else "(none)"
        message = override_message or result.message
        if result.success:
            detail = f"Expected: {expected_moves}. You played: {result.provided_move}."
        else:
            provided = result.provided_move or "(invalid move)"
            detail = f"Expected: {expected_moves}. You played: {provided}."
        self.feedback_label.setText(f"{message}\n{detail}")
        self.srs.save()
        if result.next_fen:
            self.trainer.sync_with_repertoire()
        self._latest_stats = self.srs.statistics()
        self.load_next_card()

    def _update_summary_labels(self) -> None:
        stats = self._latest_stats
        self.due_label.setText(
            (
                f"Due today: {stats.due_today}"
                f" | Overdue: {stats.overdue}"
                f" | Next {stats.horizon_days} days: {stats.due_within_horizon}"
            )
        )

    def closeEvent(self, event) -> None:  # noqa: N802 - PyQt API
        self.srs.save()
        super().closeEvent(event)
