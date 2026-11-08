from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import CASES, Options, apply_renames, plan_renames, undo_renames


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="renamekit",
        description="Safe bulk file renamer. Previews by default; use --apply to rename.",
    )
    p.add_argument("files", nargs="*", help="files to rename (use shell globs)")
    p.add_argument("--replace", nargs=2, metavar=("OLD", "NEW"), help="replace text in names")
    p.add_argument("--regex", nargs=2, metavar=("PATTERN", "REPL"), help="regex substitution")
    p.add_argument("--case", choices=sorted(CASES), help="convert name case")
    p.add_argument("--number", action="store_true", help="append a sequence number")
    p.add_argument("--start", type=int, default=1, help="first number (default 1)")
    p.add_argument("--width", type=int, default=3, help="zero-padding width (default 3)")
    p.add_argument("--prefix", default="", help="text to add before the name")
    p.add_argument("--suffix", default="", help="text to add after the name")
    p.add_argument("--lower-ext", action="store_true", help="lowercase file extensions")
    p.add_argument("--apply", action="store_true", help="actually rename (default is preview)")
    p.add_argument("--undo", action="store_true", help="undo the last applied rename")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.undo:
        try:
            n = undo_renames()
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            return 1
        print(f"Restored {n} file(s).")
        return 0

    if not args.files:
        print("No files given. See --help.", file=sys.stderr)
        return 2

    opts = Options(
        replace=tuple(args.replace) if args.replace else None,
        regex=tuple(args.regex) if args.regex else None,
        case=args.case, number=args.number, start=args.start, width=args.width,
        prefix=args.prefix, suffix=args.suffix, lower_ext=args.lower_ext,
    )
    try:
        plan = plan_renames(args.files, opts)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not plan:
        print("Nothing to rename.")
        return 0
    for src, dst in plan:
        print(f"{src.name}  ->  {dst.name}")

    if not args.apply:
        print(f"\nPreview only. {len(plan)} file(s) would change. Add --apply to rename.")
        return 0
    apply_renames(plan)
    print(f"\nRenamed {len(plan)} file(s). Undo with: renamekit --undo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
