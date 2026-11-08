from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path

UNDO_FILE = ".renamekit-undo.json"


@dataclass
class Options:
    replace: tuple[str, str] | None = None
    regex: tuple[str, str] | None = None
    case: str | None = None  # lower, upper, title, snake, kebab
    number: bool = False
    start: int = 1
    width: int = 3
    prefix: str = ""
    suffix: str = ""
    lower_ext: bool = False


def _words(s: str) -> str:
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)  # split camelCase
    return re.sub(r"[\W_]+", " ", s).strip()


def to_snake(s: str) -> str:
    return _words(s).replace(" ", "_").lower()


def to_kebab(s: str) -> str:
    return _words(s).replace(" ", "-").lower()


CASES = {
    "lower": str.lower,
    "upper": str.upper,
    "title": str.title,
    "snake": to_snake,
    "kebab": to_kebab,
}


def transform(path: Path, index: int, opts: Options) -> str:
    stem, ext = path.stem, path.suffix
    if opts.replace:
        stem = stem.replace(*opts.replace)
    if opts.regex:
        stem = re.sub(opts.regex[0], opts.regex[1], stem)
    if opts.case:
        stem = CASES[opts.case](stem)
    stem = f"{opts.prefix}{stem}{opts.suffix}"
    if opts.number:
        stem = f"{stem}_{index + opts.start:0{opts.width}d}"
    if opts.lower_ext:
        ext = ext.lower()
    return stem + ext


def plan_renames(paths, opts: Options) -> list[tuple[Path, Path]]:
    """Return [(src, dst)] for files that would change. Raises ValueError on conflicts."""
    files = sorted(Path(p) for p in paths if Path(p).is_file())
    plan = []
    for i, src in enumerate(files):
        dst = src.with_name(transform(src, i, opts))
        if dst != src:
            plan.append((src, dst))

    dsts = [d for _, d in plan]
    if len(set(dsts)) != len(dsts):
        dupes = sorted({str(d) for d in dsts if dsts.count(d) > 1})
        raise ValueError(f"Multiple files would be renamed to: {', '.join(dupes)}")
    sources = {s for s, _ in plan}
    for dst in dsts:
        if dst.exists() and dst not in sources:
            raise ValueError(f"Target already exists: {dst}")
    return plan


def apply_renames(plan, undo_dir: Path | str = ".") -> Path | None:
    """Rename via temp names (so swaps/chains work) and write an undo log."""
    if not plan:
        return None
    staged = []
    for src, dst in plan:
        tmp = src.with_name(f".{uuid.uuid4().hex}.renamekit-tmp")
        src.rename(tmp)
        staged.append((tmp, dst))
    for tmp, dst in staged:
        tmp.rename(dst)
    log = Path(undo_dir) / UNDO_FILE
    log.write_text(
        json.dumps([[str(s.resolve()), str(d.resolve())] for s, d in plan], indent=2)
    )
    return log


def undo_renames(undo_dir: Path | str = ".") -> int:
    log = Path(undo_dir) / UNDO_FILE
    if not log.exists():
        raise FileNotFoundError("Nothing to undo (no undo log found).")
    pairs = [(Path(s), Path(d)) for s, d in json.loads(log.read_text())]
    staged = []
    for orig, current in pairs:
        tmp = current.with_name(f".{uuid.uuid4().hex}.renamekit-tmp")
        current.rename(tmp)
        staged.append((tmp, orig))
    for tmp, orig in staged:
        tmp.rename(orig)
    log.unlink()
    return len(pairs)
