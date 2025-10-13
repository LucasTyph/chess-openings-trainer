"""Entry point for the Chess Opening Trainer desktop application."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from core.repertoire import RepertoireManager
from core.srs import SRSManager
from core.trainer import Trainer
from gui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chess Opening Trainer")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "data",
        help="Directory containing repertoire.json and srs_state.json",
    )
    args = parser.parse_args(argv)

    base_dir = Path(__file__).resolve().parent
    data_dir = args.data_dir.resolve()
    white_repertoire_path = data_dir / "repertoire_white.json"
    black_repertoire_path = data_dir / "repertoire_black.json"
    srs_path = data_dir / "srs_state.json"

    repertoire = RepertoireManager(white_repertoire_path, black_repertoire_path)
    repertoire.load()

    srs_manager = SRSManager(srs_path)
    srs_manager.load()

    trainer = Trainer(repertoire, srs_manager)
    trainer.sync_with_repertoire()

    app = QApplication(sys.argv)
    window = MainWindow(srs_manager, trainer, data_dir)
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
