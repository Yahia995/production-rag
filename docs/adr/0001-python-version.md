# ADR 0001: Python version

## Decision

Use Python 3.11.14 for the project.

The Python version is pinned in `pyproject.toml` so that development and
deployment use the same baseline.

## Why

The project needs a stable Python environment across the API, workers,
evaluation code, and supporting scripts.

Python 3.11 gives us a mature baseline with good support across the libraries
we expect to use.

I'm deliberately using 3.11.14 rather than moving to a newer Python release
just because it exists. For this project, consistency is more useful than
chasing the newest runtime.

## Consequences

All project code should remain compatible with Python 3.11.

Docker images and local development environments should use the same Python
version.

If the project moves to another Python version later, that change should be
made deliberately and tested rather than happening implicitly through a base
image update.
