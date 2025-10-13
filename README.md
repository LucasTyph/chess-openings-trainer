# Chess Opening Trainer

A desktop application that combines a chess opening repertoire explorer with a
spaced repetition system (SRS) to help you memorise your favourite openings.
The project is implemented in Python using PyQt5 for the graphical user
interface and `python-chess` for move validation and PGN parsing.

## Features

- Visualise board positions from your repertoire.
- Import PGN files to build and extend your repertoire tree.
- Review positions due for study using an SM-2 style spaced repetition
  scheduler.
- Record your answers in Standard Algebraic Notation (SAN) or coordinate (UCI)
  format and receive immediate feedback.
- Track scheduling details – ease factor, intervals and due dates – through a
  statistics dialog.

## Project Layout

```
├── core/
│   ├── persistence.py   # JSON storage helpers
│   ├── repertoire.py    # Repertoire loading and PGN importing
│   ├── srs.py           # SM-2 scheduling logic
│   └── trainer.py       # Glue between GUI, repertoire and SRS
├── gui/
│   ├── board_widget.py  # Chess board grid widget
│   ├── dialogs.py       # Statistics dialog
│   └── main_window.py   # Main application window
├── data/
│   ├── repertoire.json  # Default repertoire store
│   └── srs_state.json   # Default SRS state store
├── requirements.txt     # Python dependencies
└── main.py              # Application entry point
```

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

3. **Import a PGN** via *File → Import PGN* and start training.

### Running inside GitHub Codespaces

GitHub Codespaces already ships with Python and Qt libraries, so you can launch
the trainer without additional system packages.

1. **Install the project dependencies** (once per Codespace):

   ```bash
   pip install --user -r requirements.txt
   ```

2. **Launch the GUI** using VS Code's integrated terminal. Codespaces runs in a
   headless environment, so wrap the command with `xvfb-run` to provide a
   virtual display:

   ```bash
   xvfb-run -a python main.py
   ```

   If you're connecting through the VS Code desktop client, the window will be
   tunneled back automatically. Inside the browser client you can open the
   *Ports* panel and click the forwarded display link when prompted.

3. **Persisting data** – repertoire and scheduling files live in `data/`. These
   files are committed to the repository so your work-in-progress repertoire is
   saved across Codespace restarts. Use *File → Export Repertoire* to back up a
   copy externally.

## Development Notes

- Repertoire and SRS data are stored as JSON in the `data/` directory by
  default. Use the *File → Export Repertoire* menu to save a copy elsewhere.
- Moves entered in the training view can be in SAN (`Nf3`, `dxe5+`) or UCI
  (`g1f3`, `d7d5`). Only legal moves present in your repertoire tree are marked
  as correct.
- The SM-2 algorithm is implemented with adjustable ease factors (minimum 1.3)
  and will reschedule cards based on your answers. Cards marked incorrect are
  scheduled for the next day by default.
- Training statistics now surface in the *View → Show Statistics* dialog,
  providing total card counts, overdue numbers and an estimated recent success
  rate to help steer your study sessions.
- Launch `python main.py --data-dir <path>` to keep multiple repertoires (for
  example one per opening) without duplicating the codebase.

## License

Distributed under the MIT License. See `LICENSE` for details (add one if you
plan to distribute the project).
