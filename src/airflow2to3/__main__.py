from __future__ import annotations

import argparse
import functools
import importlib
import os
import pathlib
import sys
import typing

from airflow2to3.fix import Fixer, fix_file

if typing.TYPE_CHECKING:
    from collections.abc import Collection, Sequence


def _load_fixer(v: str) -> Fixer:
    if v.isdigit():
        v = f"AIR{v:0>3}"
    try:
        module = importlib.import_module(f"{__package__}.rules.{v}")
    except ModuleNotFoundError:
        raise ValueError(f"unknown rule: {v}") from None
    return typing.cast(Fixer, module)


# Named as such for error message; this is supposed to be private.
def select(value: str) -> Collection[Fixer]:
    return [_load_fixer(v) for v in value.split(",")]


def main(args: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser("airflow2to3")
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="path",
        type=pathlib.Path,
        help="List of files or directories to check",
    )
    parser.add_argument(
        "--select",
        dest="fixers",
        type=select,
        help="Comma-separated Airflow lint codes",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print result to stdout instead of modifying the file."
    )
    ns = parser.parse_args(args)

    _fix_file = functools.partial(
        fix_file,
        fixers=ns.fixers,
        dry_run=ns.dry_run,
    )

    for path in ns.paths:
        if path.is_file():
            _fix_file(path)
        elif path.is_dir():
            for root, _, files in os.walk(path, followlinks=True):
                for fn in files:
                    _fix_file(pathlib.Path(root, fn))
        else:
            print(f"Ignoring entry {path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
