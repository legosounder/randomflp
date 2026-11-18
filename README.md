# Random FLP

A macOS CLI utility and launcher that selects a random FL Studio project (`.flp`) from your project folders and opens it in FL Studio or reveals it in Finder.

## Features

- Scans project directories recursively for FL Studio (`.flp`) projects.
- Automatically ignores backup directories and autosaved files by default.
- If a project directory contains multiple `.flp` files, picks the most recently modified file.
- **No-Repeat Mode (`-u` / `--unique`)**: Tracks opened projects in `.flp_history.json` so you do not repeat projects until all have been opened.
- **Finder Integration (`-f` / `--finder`, `-r` / `--reveal`)**: Open the project folder directly in macOS Finder or highlight the `.flp` file.
- macOS notification support when launching projects.

## Usage

### Run via Command Line

```bash
# Pick a random project from current directory and open in FL Studio
python3 random_flp.py

# Specify a project directory
python3 random_flp.py "/path/to/FL Studio/Projects"

# Pick without repeats until all projects have been opened
python3 random_flp.py -u

# Open the project folder in Finder instead of FL Studio
python3 random_flp.py -f

# Reveal the specific FLP file in Finder
python3 random_flp.py -r

# Reset history tracking
python3 random_flp.py --reset-history
```

### macOS Double-Click Launchers

- `Open Random FLP.command`: Double-click in Finder to randomly select and launch a project in FL Studio.
- `Open Random Folder in Finder.command`: Double-click in Finder to randomly select and reveal a project folder in macOS Finder.
