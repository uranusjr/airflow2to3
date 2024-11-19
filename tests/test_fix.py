from __future__ import annotations

import importlib
import pathlib
import typing

import pytest

from airflow2to3.fix import fix_file


@pytest.mark.parametrize(
    "rule",
    [
        "AIR301",
    ],
)
def test_fix_file(tmp_path: pathlib.Path, rule: str) -> None:
    fixture = pathlib.Path(__file__).parent.joinpath("fixtures", rule)

    target = tmp_path.joinpath(f"{rule}.py")
    target.write_bytes(fixture.joinpath("original.py").read_bytes())

    fixer: typing.Any = importlib.import_module(f"airflow2to3.rules.{rule}")
    fix_file(target, fixers=[fixer], dry_run=False)

    assert target.read_text() == fixture.joinpath("updated.py").read_text()
