"""Analysis service: the integrity checker and case report behind an API, with a custody log.

    POST /v1/check             AI summary vs transcript, claim by claim [analyse]
    POST /v1/report            case report for a zipped Omi app extraction (body = the zip) [analyse]
    GET  /v1/analyses[/{id}]   the custody log: who submitted what, when, with input hashes [read]
    GET  /healthz, /readyz, /metrics

Evidence is analysed in memory or in a temporary directory that is removed afterwards, and is
not stored: each analysis keeps the SHA-256 of its inputs, the counts it found and who asked.
Callers send an API key whose role decides the permissions in brackets; settings come from
WEARFX_* variables (see ops.py and docs/runbook.md).

    python -m wearfx serve
"""
from __future__ import annotations

import hashlib
import io
import json
import tempfile
import threading
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from . import db, faithful, ops, report

settings = ops.load_settings()
ops.setup_logging(settings.log_level)
engine = db.connect(settings.database_url)
_lock = threading.Lock()

app = FastAPI(title="WearFX analysis service", version="1.0.0")
ops.install(app, settings, {"database": lambda: engine.connect().close()})

MAX_TEXT = 2_000_000          # characters of transcript or summary
MAX_MEMBERS = 20_000          # files in one extraction zip
MAX_UNZIPPED = 500_000_000    # bytes once extracted


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _log(ident: dict, kind: str, label: str, inputs: Dict[str, str], summary: Dict[str, Any]) -> str:
    aid = uuid.uuid4().hex
    with _lock, engine.begin() as c:
        c.execute(text("INSERT INTO analyses VALUES (:i, :t, :u, :k, :l, :n, :s)"),
                  {"i": aid, "t": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
                   "u": ident["user"] or "demo", "k": kind, "l": label, "n": json.dumps(inputs),
                   "s": json.dumps(summary)})
    return aid


class CheckRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=MAX_TEXT)
    transcript_format: Literal["srt", "txt", "auto"] = "auto"
    summary: str = Field(..., min_length=1, max_length=MAX_TEXT)
    label: str = Field("", max_length=200, description="case or exhibit reference, for the custody log")


@app.post("/v1/check")
def check(req: CheckRequest, ident: dict = Depends(ops.require("analyse"))) -> Dict[str, Any]:
    fmt = req.transcript_format
    if fmt == "auto":
        fmt = "srt" if "-->" in req.transcript[:500] else "txt"
    segments = (faithful.load_srt if fmt == "srt" else faithful.load_txt)(req.transcript)
    if not segments:
        raise HTTPException(422, "the transcript has no segments")
    result = faithful.check(segments, req.summary)
    inputs = {"transcript": _sha(req.transcript.encode()), "summary": _sha(req.summary.encode())}
    counts = {k: result[k] for k in ("checkable", "supported", "unsupported", "low_confidence", "score")}
    ops.DECISIONS.labels(decision="summary_checked").inc()
    if result["unsupported"]:
        ops.DECISIONS.labels(decision="unsupported_claims").inc()
    return {"analysis_id": _log(ident, "check", req.label, inputs, counts), "inputs": inputs, **result}


def _extract(data: bytes, dest: Path) -> int:
    """Unpack a zip into dest, refusing absolute paths, '..', links and zip bombs."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise HTTPException(422, "the body is not a zip file") from None
    members = zf.infolist()
    if len(members) > MAX_MEMBERS:
        raise HTTPException(413, f"the zip holds more than {MAX_MEMBERS} files")
    if sum(m.file_size for m in members) > MAX_UNZIPPED:
        raise HTTPException(413, "the zip expands beyond the size limit")
    for m in members:
        name = PurePosixPath(m.filename.replace("\\", "/"))
        if name.is_absolute() or ".." in name.parts or (m.external_attr >> 16) & 0o170000 == 0o120000:
            raise HTTPException(422, "the zip holds an unsafe path")
        target = dest.joinpath(*name.parts)
        if m.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(m) as src, open(target, "wb") as out:
            left = m.file_size  # never write more than the header declared, whatever the stream holds
            while left > 0 and (chunk := src.read(min(1 << 20, left))):
                out.write(chunk)
                left -= len(chunk)
    return len(members)


def _relative(obj, root: str):
    """Source paths in the report, relative to the zip's root instead of the temporary directory."""
    if isinstance(obj, str) and obj.startswith(root):
        return obj[len(root):].lstrip("/\\").replace("\\", "/")
    if isinstance(obj, dict):
        return {k: _relative(v, root) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_relative(v, root) for v in obj]
    return obj


@app.post("/v1/report")
async def case_report(request: Request, fmt: Literal["json", "csv", "html"] = Query("json", alias="format"),
                      label: str = Query("", max_length=200),
                      ident: dict = Depends(ops.require("analyse"))) -> Response:
    data = await request.body()
    if not data:
        raise HTTPException(422, "send the zipped extraction as the request body")
    with tempfile.TemporaryDirectory(prefix="wearfx-") as tmp:
        files = _extract(data, Path(tmp))
        rep = _relative(report.from_root(tmp), tmp)
        out = {"json": report.to_json, "csv": report.to_csv, "html": report.to_html}[fmt](rep)
    counts = {"files": files, "events": len(rep["events"]), "conversations": len(rep["integrity"]),
              "errors": len(rep["errors"]),
              "conversations_with_unsupported_claims": sum(1 for i in rep["integrity"] if i["unsupported"])}
    aid = _log(ident, "report", label, {"extraction_zip": _sha(data)}, counts)
    ops.DECISIONS.labels(decision="case_report").inc()
    media = {"json": "application/json", "csv": "text/csv; charset=utf-8", "html": "text/html; charset=utf-8"}[fmt]
    return Response(out, media_type=media, headers={"x-analysis-id": aid, "x-input-sha256": _sha(data)})


def _row(r) -> Dict[str, Any]:
    d = dict(r)
    for k in ("inputs", "summary"):
        if k in d:
            d[k] = json.loads(d[k])
    return d


@app.get("/v1/analyses", dependencies=[Depends(ops.require("read"))])
def list_analyses(limit: int = Query(50, ge=1, le=1000)) -> Dict[str, Any]:
    with engine.connect() as c:
        rows = c.execute(text("SELECT * FROM analyses ORDER BY created_at DESC LIMIT :n"), {"n": limit}).mappings().all()
    return {"analyses": [_row(r) for r in rows]}


@app.get("/v1/analyses/{analysis_id}", dependencies=[Depends(ops.require("read"))])
def get_analysis(analysis_id: str) -> Dict[str, Any]:
    with engine.connect() as c:
        r = c.execute(text("SELECT * FROM analyses WHERE id = :i"), {"i": analysis_id[:64]}).mappings().first()
    if r is None:
        raise HTTPException(404, "analysis not found")
    return _row(r)
