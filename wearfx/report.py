"""Case report: one timeline from an Omi scan, with per-conversation summary integrity."""
import csv
import html
import io
import json
from datetime import datetime, timezone

from wearfx import faithful, omi


def _epoch(v):
    if isinstance(v, (int, float)):
        return int(v // 1000 if v > 10**11 else v)
    if isinstance(v, str) and v:
        try:
            return int(datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp())
        except ValueError:
            return None
    return None


def build(scan: dict) -> dict:
    events = []
    for r in scan["recordings"]:
        if "_error" in r:
            events.append({"ts": None, "kind": "index_error", "detail": r["_error"], "source": r.get("_file")})
            continue
        events.append({"ts": _epoch(r["start"]), "kind": "recording", "source": r["_file"],
                       "detail": f"{r['seconds']}s on {r['device_model'] or r['device']}, status {r['status']}, "
                                 f"storage {r['storage']}",
                       "lat": r["latitude"], "lon": r["longitude"], "ref": r["conversation_id"]})
    integrity = []
    for c in scan["conversations"]:
        chk = faithful.check(c["segments"], faithful.summary_text(c))
        integrity.append({"conversation": c["id"], "title": c["title"], "score": chk["score"],
                          "unsupported": [x["claim"] for x in chk["claims"] if x["status"] == "unsupported"]})
        flags = [k for k in ("deleted", "discarded") if c.get(k)]
        events.append({"ts": _epoch(c["started_at"] or c["created_at"]), "kind": "conversation",
                       "source": c["_file"], "ref": c["id"],
                       "detail": f"{c['title']!s} ({len(c['segments'])} segments, integrity {chk['score']})"
                                 + (f" [{', '.join(flags)}]" if flags else ""),
                       "lat": c["latitude"], "lon": c["longitude"]})
    for m in scan["memories"]:
        events.append({"ts": _epoch(m["created_at"]), "kind": "memory", "source": m["_file"],
                       "detail": m["content"], "ref": m["conversation_id"]})
    for a in scan["audio_files"]:
        events.append({"ts": a["start"], "kind": "audio_file" if a["in_wal_index"] else "audio_file_orphan",
                       "source": a["_path"], "detail": f"{a['bytes']} bytes, {a['device']} {a['codec']}"})
    events.sort(key=lambda e: (e["ts"] is None, e["ts"] or 0))
    for e in events:
        e["time_utc"] = datetime.fromtimestamp(e["ts"], timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if e["ts"] else None
    return {"account": scan["account"], "prefs_files": scan["prefs_files"], "wal_indexes": scan["wal_indexes"],
            "errors": scan.get("errors", []), "integrity": integrity, "events": events}


def to_json(rep: dict) -> str:
    return json.dumps(rep, indent=2, ensure_ascii=False, default=str)


def to_csv(rep: dict) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["time_utc", "kind", "detail", "ref", "lat", "lon", "source"],
                       extrasaction="ignore")
    w.writeheader()
    w.writerows(rep["events"])
    return buf.getvalue()


def to_html(rep: dict, title: str = "WearFX case report") -> str:
    e = lambda v: html.escape("" if v is None else str(v))
    acc = rep["account"] or {}
    acc_rows = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in acc.items() if k != "webhooks")
    hooks = "".join(f"<li>{e(k)}: {e(v)}</li>" for k, v in (acc.get("webhooks") or {}).items()) or "<li>none</li>"
    errs = "".join(f"<li>{e(x['file'])}: {e(x['error'])}</li>" for x in rep.get("errors", []))
    integ = "".join(f"<tr><td>{e(i['title'])}</td><td>{e(i['score'])}</td><td>{e(', '.join(i['unsupported']))}</td></tr>"
                    for i in rep["integrity"])
    ev = "".join(f"<tr><td>{e(x['time_utc'])}</td><td>{e(x['kind'])}</td><td>{e(x['detail'])}</td>"
                 f"<td>{e(x.get('lat'))},{e(x.get('lon'))}</td><td>{e(x.get('source'))}</td></tr>"
                 for x in rep["events"])
    return ("<!doctype html><meta charset=utf-8>"
            f"<title>{e(title)}</title><style>body{{font:14px system-ui;margin:1rem}}"
            "table{border-collapse:collapse;width:100%;margin-bottom:1rem}td,th{border:1px solid #ccc;"
            "padding:4px 8px;text-align:left;vertical-align:top}th{background:#f0f0f0}</style>"
            f"<h1>{e(title)}</h1><h2>Account and device</h2><table>{acc_rows}</table>"
            f"<h2>Webhook destinations</h2><ul>{hooks}</ul>"
            + (f"<h2>Unreadable files</h2><ul>{errs}</ul>" if rep.get("errors") else "")
            + "<h2>Summary integrity</h2><p>Unsupported = key token not found in the transcript. "
            "A lead to check against the audio, not proof of fabrication.</p>"
            f"<table><tr><th>Conversation</th><th>Score</th><th>Unsupported claims</th></tr>{integ}</table>"
            f"<h2>Timeline ({len(rep['events'])} events)</h2><table><tr><th>UTC</th><th>Kind</th>"
            f"<th>Detail</th><th>Lat,Lon</th><th>Source</th></tr>{ev}</table>")


def from_root(root: str) -> dict:
    return build(omi.scan(root))
