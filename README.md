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

## Windows Standalone Build

You can build and run Chess Opening Trainer as a standalone Windows executable using PyInstaller:

### Build Instructions

1. Install Python 3.x and pip (for building only).
2. Install PyInstaller:
  ```bash
  pip install pyinstaller
  ```
3. Run the build script:
  ```bash
  build_windows.bat
  ```
  The executable will be created in the `dist/` folder as `ChessOpeningTrainer.exe`.

### Usage

- Double-click `ChessOpeningTrainer.exe` to launch the app.
- All your data (PGNs, training progress) will be saved in your user folder under `ChessOpeningTrainerData`.
- No need for Python or dependencies on the target machine.

### Troubleshooting

- If you add new dependencies, re-run `pip install -r requirements.txt` before building.
- If you use data files, they will be stored in your user folder for persistence.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
