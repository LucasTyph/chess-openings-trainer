"""Spaced repetition scheduler based on the SM-2 algorithm."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import fmean
from typing import Dict, Iterable, Optional, Sequence

from .persistence import load_json, save_json

ISO_FORMAT = "%Y-%m-%d"
DEFAULT_EASE = 2.5
MIN_EASE = 1.3


def _parse_date(value: str) -> date:
    return datetime.strptime(value, ISO_FORMAT).date()


def _format_date(value: date) -> str:
    return value.strftime(ISO_FORMAT)


@dataclass
class Card:
    fen: str
    ease: float = DEFAULT_EASE
    interval: int = 0
    repetitions: int = 0
    due: date = field(default_factory=date.today)
    last_grade: Optional[int] = None
    last_reviewed: Optional[date] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "ease": self.ease,
            "interval": self.interval,
            "repetitions": self.repetitions,
            "due": _format_date(self.due),
            "last_grade": self.last_grade,
            "last_reviewed": _format_date(self.last_reviewed) if self.last_reviewed else None,
        }

    @classmethod
    def from_dict(cls, fen: str, data: Dict[str, object]) -> "Card":
        due = date.today()
        stored_due = data.get("due")
        if isinstance(stored_due, str):
            try:
                due = _parse_date(stored_due)
            except ValueError:
                due = date.today()
        last_reviewed = None
        stored_reviewed = data.get("last_reviewed")
        if isinstance(stored_reviewed, str):
            try:
                last_reviewed = _parse_date(stored_reviewed)
            except ValueError:
                last_reviewed = None
        return cls(
            fen=fen,
            ease=float(data.get("ease", DEFAULT_EASE)),
            interval=int(data.get("interval", 0)),
            repetitions=int(data.get("repetitions", 0)),
            due=due,
            last_grade=int(data["last_grade"]) if isinstance(data.get("last_grade"), int) else None,
            last_reviewed=last_reviewed,
        )


class SRSManager:
    """Manage spaced repetition scheduling for repertoire positions."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._cards: Dict[str, Card] = {}

    def load(self) -> None:
        raw = load_json(self.path)
        if not isinstance(raw, dict):
            self._cards = {}
            return
        cards: Dict[str, Card] = {}
        for fen, data in raw.items():
            if isinstance(fen, str) and isinstance(data, dict):
                cards[fen] = Card.from_dict(fen, data)
        self._cards = cards

    def save(self) -> None:
        payload = {fen: card.to_dict() for fen, card in self._cards.items()}
        save_json(self.path, payload)

    def get(self, fen: str) -> Card:
        if fen not in self._cards:
            # New card: set due date to today
            self._cards[fen] = Card(fen=fen, due=date.today())
        return self._cards[fen]

    def schedule(self, fen: str, grade: int, today: Optional[date] = None) -> Card:
        today = today or date.today()
        card = self.get(fen)
        card.last_grade = grade
        card.last_reviewed = today
        if grade < 3:
            card.repetitions = 0
            card.interval = 1
        else:
            if card.repetitions == 0:
                card.interval = 1
            elif card.repetitions == 1:
                card.interval = 6
            else:
                card.interval = int(round(card.interval * card.ease)) or 1
            card.repetitions += 1
            card.ease = max(MIN_EASE, card.ease + 0.1 - (5 - grade) * 0.08)
        card.due = today + timedelta(days=card.interval)
        self._cards[fen] = card
        return card

    def due_cards(self, today: Optional[date] = None) -> Iterable[Card]:
        today = today or date.today()
        return sorted((card for card in self._cards.values() if card.due <= today), key=lambda c: (c.due, c.ease))

    def next_due(self, today: Optional[date] = None) -> Optional[Card]:
        cards = list(self.due_cards(today=today))
        return cards[0] if cards else None

    def all_cards(self) -> Dict[str, Card]:
        return dict(self._cards)

    def remove_cards(self, fens_to_keep: Sequence[str]) -> None:
        allowed = set(fens_to_keep)
        to_remove = [fen for fen in self._cards if fen not in allowed]
        for fen in to_remove:
            self._cards.pop(fen, None)

    @dataclass
    class Stats:
        total_cards: int
        due_today: int
        overdue: int
        due_within_horizon: int
        horizon_days: int
        average_ease: float
        last_session_success_rate: float

    def statistics(self, today: Optional[date] = None, horizon_days: int = 7) -> "SRSManager.Stats":
        today = today or date.today()
        cards = list(self._cards.values())
        total_cards = len(cards)
        if not cards:
            return self.Stats(
                total_cards=0,
                due_today=0,
                overdue=0,
                due_within_horizon=0,
                horizon_days=horizon_days,
                average_ease=0.0,
                last_session_success_rate=0.0,
            )

        due_today = sum(1 for card in cards if card.due <= today)
        overdue = sum(1 for card in cards if card.due < today)
        horizon_limit = today + timedelta(days=horizon_days)
        due_within_horizon = sum(1 for card in cards if today <= card.due <= horizon_limit)
        average_ease = fmean(card.ease for card in cards)

        graded_cards = [card for card in cards if card.last_grade is not None]
        if graded_cards:
            success = sum(1 for card in graded_cards if card.last_grade and card.last_grade >= 3)
            last_session_success_rate = success / len(graded_cards)
        else:
            last_session_success_rate = 0.0

        return self.Stats(
            total_cards=total_cards,
            due_today=due_today,
            overdue=overdue,
            due_within_horizon=due_within_horizon,
            horizon_days=horizon_days,
            average_ease=average_ease,
            last_session_success_rate=last_session_success_rate,
        )
