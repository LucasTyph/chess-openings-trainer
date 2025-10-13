"""Auxiliary dialogs for the Chess Opening Trainer GUI."""
from __future__ import annotations

from typing import Iterable

from PyQt5.QtWidgets import QLabel, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout

from core.srs import Card, SRSManager


class StatsDialog(QDialog):
    def __init__(self, cards: Iterable[Card], stats: SRSManager.Stats, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Training Statistics")
        layout = QVBoxLayout(self)

        summary = QLabel(
            (
                f"Total cards: {stats.total_cards}\n"
                f"Due today: {stats.due_today} (overdue: {stats.overdue})\n"
                f"Due within next {stats.horizon_days} days: {stats.due_within_horizon}\n"
                f"Average ease: {stats.average_ease:.2f}\n"
                f"Recent success rate: {stats.last_session_success_rate * 100:.0f}%"
            ),
            self,
        )
        summary.setWordWrap(True)
        layout.addWidget(summary)

        table = QTableWidget(self)
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["FEN", "Due", "Interval", "Ease", "Last Grade"])
        card_list = list(cards)
        table.setRowCount(len(card_list))
        for row, card in enumerate(card_list):
            table.setItem(row, 0, QTableWidgetItem(card.fen))
            table.setItem(row, 1, QTableWidgetItem(card.due.isoformat()))
            table.setItem(row, 2, QTableWidgetItem(str(card.interval)))
            table.setItem(row, 3, QTableWidgetItem(f"{card.ease:.2f}"))
            last_grade = "" if card.last_grade is None else str(card.last_grade)
            table.setItem(row, 4, QTableWidgetItem(last_grade))
        table.resizeColumnsToContents()
        layout.addWidget(table)
