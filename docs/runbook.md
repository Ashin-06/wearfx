# Runbook

How to deploy and operate the analysis service. Commands assume the repository root.

## Deploy

```bash
docker build -t wearfx:1.0.0 .
python -m wearfx.ops keygen            # one API key per examiner, viewer and monitor
docker run -d --name wearfx -p 8102:8102 -v wearfx-data:/data \
  -e WEARFX_KEYS_FILE=/run/secrets/wearfx-keys.json \
  wearfx:1.0.0
curl -fsS http://127.0.0.1:8102/readyz
```

The image runs in production mode as a non-root user with its custody log in SQLite under `/data`.
It refuses to start, and logs why, without hashed API keys or a database URL.

## Use

```bash
curl -fsS -H "x-api-key: $KEY" -H "content-type: application/json" \
  -d '{"transcript": "...", "summary": "...", "label": "case 17 exhibit 3"}' http://127.0.0.1:8102/v1/check
cd extracted && zip -qr ../case.zip . && cd ..
curl -fsS -H "x-api-key: $KEY" --data-binary @case.zip "http://127.0.0.1:8102/v1/report?format=html&label=phone%20A" > case.html
```

Zip a hash-verified working copy of the extraction, never the original.

## Configure

| Variable | Required in production | Meaning |
|---|---|---|
| `WEARFX_ENV` | — | `development` (default) or `production` |
| `WEARFX_API_KEYS` / `WEARFX_KEYS_FILE` | yes | JSON `{"sha256:<hex>": {"user": "...", "role": "..."}}`. Roles: `examiner` (analyse, read), `viewer`, `monitor`, `admin` |
| `WEARFX_DATABASE_URL` | yes | the custody log: `sqlite:////data/wearfx.db` or `postgresql://...` |
| `WEARFX_HOST`, `WEARFX_PORT` | — | default `127.0.0.1:8102`; any other address needs API keys |
| `WEARFX_RATE_LIMIT`, `WEARFX_MAX_BODY_BYTES` | — | default 120/min per client, 50,000,000 bytes |
| `WEARFX_CORS_ORIGINS` | — | comma-separated origins allowed to call the API from a browser |

## Watch

- `GET /healthz`; `GET /readyz` (database); `GET /metrics` (role `monitor`): requests, latency,
  errors, `wearfx_decisions_total{decision="summary_checked|unsupported_claims|case_report"}`.
- Logs are JSON lines with a request ID; they never contain evidence.

## Rotate keys

Add the new API key hash, restart, hand over the key, remove the old hash, restart.

## Back up and restore

Back up the custody log like any SQLite or Postgres database (`python -m wearfx migrate` creates
the schema on a fresh one). It is small: one row per analysis.

## Incidents

1. **Leaked API key.** Remove its hash and restart; list that user's entries in `/v1/analyses`.
2. **A result is challenged.** Find the entry by analysis ID, compare its input hash with the
   exhibit's hash, and re-run the same input with the same version.
