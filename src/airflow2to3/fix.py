from __future__ import annotations

import typing

import libcst as cst
from libcst.codemod import CodemodContext

if typing.TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from libcst import Module


class Fixer(typing.Protocol):
    def fix(self, module: Module, context: CodemodContext) -> Module: ...


def fix_file(
    path: Path,
    *,
    fixers: Sequence[Fixer],
    dry_run: bool,
    encoding: str = "utf8",  # Probably don't need to support other encodings.
) -> None:
    if path.suffix != ".py":  # Only support Python files for now.
        return
    orig_module = module = cst.parse_module(path.read_text(encoding=encoding))
    context = CodemodContext(filename=str(path))
    for fixer in fixers:
        module = fixer.fix(module, context)
    if dry_run:
        if module.deep_equals(orig_module):
            print(f"Nothing to fix in {path}")
        else:
            print(path)
            print("-" * 40)
            print(module.code)
            print()
    else:
        if not module.deep_equals(orig_module):
            path.write_text(module.code, encoding=encoding)
