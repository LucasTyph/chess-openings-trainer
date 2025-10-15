# Chess Opening Trainer

A desktop app to practice chess openings through SRS (spaced repetition system). Made using `python-chess` and PyQt5.

## Features

- Visualise board positions from your repertoire.
- Import PGN files to build and extend your repertoire tree.
- Review positions due for study using an SM-2 style spaced repetition
  scheduler.
- Record your answers in Standard Algebraic Notation (SAN) or coordinate (UCI)
  format and receive immediate feedback.
- Track scheduling details – ease factor, intervals and due dates – through a
  statistics dialog.

## Getting Started

### Local environment

1. **Install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\\Scripts\\activate`
   pip install -r requirements.txt
   ```

2. **Run the application**

   ```bash
   python main.py
   ```

3. **Import a PGN** via *File → Import PGN* and start training. There are separate PGNs you can use for black or white pieces.

## License

Distributed under the MIT License. See `LICENSE` for details.
