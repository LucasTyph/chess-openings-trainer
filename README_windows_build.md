# Building Chess Opening Trainer for Windows

## Requirements
- Python 3.x (for building only)
- pip
- PyInstaller (`pip install pyinstaller`)

## Build Instructions
1. Open a command prompt in the project directory.
2. Run `build_windows.bat`.
3. The standalone executable will be created in the `dist/` folder as `ChessOpeningTrainer.exe`.

## Notes
- The `--windowed` flag prevents a console window from appearing for GUI apps.
- All dependencies in `requirements.txt` will be bundled automatically.
- You can distribute the `ChessOpeningTrainer.exe` file to any Windows user.

## Troubleshooting
- If you add new dependencies, re-run `pip install -r requirements.txt` before building.
- If you use data files (like PGNs, JSONs), you may need to adjust the PyInstaller spec to include them.

---
For advanced customization, see the [PyInstaller documentation](https://pyinstaller.org/en/stable/).
