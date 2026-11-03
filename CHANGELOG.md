# Changelog

All notable changes to this project. Versions follow [semantic versioning](https://semver.org/).

## 1.0.0 — 2026-11-03

### Added
- An analysis API (`wearfx serve`): `POST /v1/check` checks an AI summary against a transcript,
  `POST /v1/report` builds the case report from a zipped Omi extraction (JSON, CSV or HTML), and
  `GET /v1/analyses[/{id}]` reads the custody log. Evidence is not stored; each analysis records
  its input SHA-256s, the counts found and who asked, in SQLite or Postgres with numbered
  migrations (`wearfx migrate`).
- Zip uploads refuse absolute paths, `..`, symlinks and zip bombs.
- Settings from `WEARFX_*` environment variables, checked at startup; production refuses to start
  without hashed API keys and a database. Roles on keys, rate limit, body cap, security headers,
  JSON logs with request IDs, `/healthz`, `/readyz` and Prometheus `/metrics`.
- `pyproject.toml` 1.0.0 (Python 3.12+), pinned lock files, a container image (slim, non-root,
  health check), CI with ruff, bandit, pip-audit and coverage.
- `SECURITY.md`, `docs/threat-model.md`, `docs/runbook.md`, MIT licence.

### Changed
- Android preference files are parsed with `defusedxml`, so a crafted file can't use entity
  expansion against the examiner's machine.

### Unchanged
- The parsers, the integrity checker and their results; the 17 original tests pass unchanged.
