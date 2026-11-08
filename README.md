# renamekit

A safe bulk file renamer for the command line.

- **Preview first.** Nothing changes until you pass `--apply`.
- **Conflict checks.** Refuses to overwrite files or create duplicate names.
- **Undo.** `renamekit --undo` restores the last batch.
- **Zero dependencies.** Pure Python 3.9+.

## Install

```bash
pip install renamekit        # once published
# or from source:
git clone https://github.com/<you>/renamekit && cd renamekit
pip install -e .
```

## Usage

```bash
# Preview: replace text in names
renamekit *.txt --replace "draft" "final"

# Apply it
renamekit *.txt --replace "draft" "final" --apply

# Convert to snake_case, lowercase extensions
renamekit photos/* --case snake --lower-ext --apply

# Number files: holiday_001.jpg, holiday_002.jpg ...
renamekit *.jpg --prefix "holiday" --number --apply

# Regex: strip trailing " (1)" copies
renamekit * --regex " \(\d+\)$" "" --apply

# Changed your mind?
renamekit --undo
```

## Options

| Option | What it does |
|---|---|
| `--replace OLD NEW` | Replace text in file names |
| `--regex PATTERN REPL` | Regex substitution on the name (not the extension) |
| `--case {lower,upper,title,snake,kebab}` | Convert case |
| `--prefix / --suffix` | Add text before / after the name |
| `--number` `--start N` `--width N` | Append a sequence number |
| `--lower-ext` | Lowercase extensions |
| `--apply` | Actually rename (default is preview) |
| `--undo` | Undo the last applied rename |

## Development

```bash
python -m unittest discover -s tests
```

## Contributing

Issues and PRs welcome. Ideas: recursive mode, EXIF-date naming, config presets.

## License

MIT
