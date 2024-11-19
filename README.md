# airflow2to3

This is a command line program that rewrites Airflow DAG files to be compatible
with Airflow 3, so users can upgrade more smoothly.

Example usage:

```console
$ airflow2to3 --select AIR301 -- path/to/dag.py
```

The `--select` flag takes a comma-separated codes for the tool to fix. The
codes are from [Ruff's Airflow rules] with the `AIR` prefix removed.

We only implement 2-to-3 rules with code 3xx.

[Ruff's Airflow rules]: https://docs.astral.sh/ruff/rules/#airflow-air
