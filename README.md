# randomflp

Pick a random FL Studio project folder and open the latest FLP inside.

## Usage

```bash
python3 random_flp.py [directory] [options]
```

## Options

| Option | Description |
| --- | --- |
| `directory` | Path to folder containing projects (default: current directory) |
| `-h`, `--help` | Show help message and exit |
| `-u`, `--unique`, `--no-repeat` | Avoid choosing the same project again until all have been opened |
| `--reset-history` | Reset the history of opened projects |
| `-f`, `--finder` | Open project folder in macOS Finder instead of FL Studio |
| `-r`, `--reveal` | Open Finder and select/highlight the `.flp` file |
| `-l`, `--list` | Print a list of project names (one per line) |
| `-c`, `--clip` | Copy the list of project names to the clipboard (use with `-l`) |
| `--include-backups` | Include files inside Backup folders |
| `--app APP` | Custom FL Studio application path or name |
