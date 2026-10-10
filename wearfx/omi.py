"""Omi companion-app artifacts (BasedHardware/omi@14fab5f): prefs cache, WAL recording index, audio files.

Field names come from app/lib/backend/preferences.dart, services/wals/wal.dart,
utils/wal_file_manager.dart and backend/schema/conversation.dart. Parsing is tolerant: unknown
or missing fields come back as None rather than raising.
"""
import json
import os
import re

from wearfx import flutterprefs

AUDIO_RE = re.compile(
    r"^audio_(?P<device>[a-z0-9]+)_(?P<codec>[A-Za-z0-9.]+)_(?P<rate>\d+)_(?P<ch>\d+)_fs(?P<fs>\d+)_"
    r"(?:r[A-Za-z0-9]+_)?(?P<ts>\d+)\.bin$")


def _json(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def _list(v) -> list:
    return v if isinstance(v, list) else []


def account(prefs: dict) -> dict:
    return {
        "uid": prefs.get("uid"), "email": prefs.get("email"),
        "given_name": prefs.get("givenName"), "family_name": prefs.get("familyName"),
        "device_name": prefs.get("deviceName"), "device_id_hash": prefs.get("deviceIdHash"),
        "bt_device": _json(prefs.get("btDevice")),
        "bt_devices": [_json(x) for x in _list(prefs.get("btDevices"))],
        "location_enabled": prefs.get("locationEnabled"),
        "webhooks": {k: v for k, v in prefs.items() if k.startswith("webhook") and v},
    }


def _conversation(c: dict) -> dict:
    s = c.get("structured") or {}
    geo = c.get("geolocation") or {}
    return {
        "id": c.get("id"),
        "created_at": c.get("created_at"), "started_at": c.get("started_at"), "finished_at": c.get("finished_at"),
        "title": s.get("title"), "overview": s.get("overview"), "category": s.get("category"),
        "action_items": [a.get("description") if isinstance(a, dict) else a for a in _list(s.get("action_items"))],
        "events": [e.get("title") if isinstance(e, dict) else e for e in _list(s.get("events"))],
        "segments": [{"text": g.get("text"), "speaker": g.get("speaker"), "is_user": g.get("is_user"),
                      "start": g.get("start"), "end": g.get("end")}
                     for g in _list(c.get("transcript_segments")) if isinstance(g, dict)],
        "latitude": geo.get("latitude"), "longitude": geo.get("longitude"), "address": geo.get("address"),
        "source": c.get("source"), "language": c.get("language"), "status": c.get("status"),
        "deleted": c.get("deleted"), "discarded": c.get("discarded"),
    }


def conversations(prefs: dict) -> list[dict]:
    """Cached conversations. Plain `cachedMemories` is the pre-migration name for the same list."""
    out = []
    for key in ("cachedConversations", "cachedMemories"):
        for raw in _list(prefs.get(key)):
            c = _json(raw)
            if isinstance(c, dict) and ("transcript_segments" in c or "structured" in c):
                out.append({**_conversation(c), "_key": key})
    return out


def memories(prefs: dict) -> list[dict]:
    """Facts the AI extracted: `cachedMemories:<uid>` (user-scoped) and `pendingMemories`."""
    out = []
    for key, val in prefs.items():
        if key.startswith("cachedMemories:") or key == "pendingMemories":
            for raw in _list(val):
                m = _json(raw)
                if isinstance(m, dict):
                    out.append({"content": m.get("content"), "category": m.get("category"),
                                "created_at": m.get("created_at"), "conversation_id": m.get("conversation_id"),
                                "_key": key})
    return out


def wals(data: bytes) -> list[dict]:
    """Parse a wals.json / wals_backup.json / wals.json.corrupt-* index."""
    try:
        doc = json.loads(data)
    except ValueError as e:
        return [{"_error": f"not JSON: {e}"}]
    entries = doc.get("wals") if isinstance(doc, dict) else doc
    out = []
    for w in _list(entries):
        if not isinstance(w, dict):
            out.append({"_error": "non-object entry"})
            continue
        geo = w.get("geolocation") or {}
        start, secs = w.get("timer_start"), w.get("seconds")
        out.append({
            "id": f"{w.get('device')}_{start}",
            "start": start, "seconds": secs,
            "end": start + secs if isinstance(start, int) and isinstance(secs, int) else None,
            "device": w.get("device"), "device_model": w.get("device_model"),
            "codec": w.get("codec"), "sample_rate": w.get("sample_rate"), "channel": w.get("channel"),
            "status": w.get("status"), "storage": w.get("storage"), "original_storage": w.get("original_storage"),
            "file_path": w.get("file_path"), "conversation_id": w.get("conversation_id"),
            "owner_uid": w.get("owner_uid"), "uploaded_at": w.get("uploaded_at"), "synced_at": w.get("synced_at"),
            "retry_count": w.get("retry_count"),
            "latitude": geo.get("latitude"), "longitude": geo.get("longitude"),
        })
    return out


def audio_file(name: str) -> dict | None:
    """Parse an `audio_<device>_<codec>_<rate>_<ch>_fs<frame>_[r<rand>_]<ts>.bin` name. ts: s or ms."""
    m = AUDIO_RE.match(name)
    if not m:
        return None
    ts = int(m["ts"])
    return {"file": name, "device": m["device"], "codec": m["codec"], "sample_rate": int(m["rate"]),
            "channels": int(m["ch"]), "frame_size": int(m["fs"]),
            "start": ts // 1000 if ts > 10**11 else ts}


def scan(root: str) -> dict:
    """Walk an extracted Omi app directory and return every artifact found, with source paths."""
    result = {"prefs_files": [], "account": None, "conversations": [], "memories": [],
              "wal_indexes": [], "recordings": [], "audio_files": []}
    for dirpath, _dirs, files in os.walk(root):
        for f in sorted(files):
            path = os.path.join(dirpath, f)
            if f == "FlutterSharedPreferences.xml" or (f.endswith(".plist") and "Preferences" in dirpath):
                prefs = flutterprefs.read(path)
                if not any(k in prefs for k in ("uid", "cachedConversations", "btDevice", "email")):
                    continue  # some other app's plist
                result["prefs_files"].append(path)
                result["account"] = account(prefs)
                result["conversations"] += [{**c, "_file": path} for c in conversations(prefs)]
                result["memories"] += [{**m, "_file": path} for m in memories(prefs)]
            elif f.startswith("wals") and ".json" in f:
                result["wal_indexes"].append(path)
                result["recordings"] += [{**w, "_file": path} for w in wals(open(path, "rb").read())]
            elif (a := audio_file(f)) is not None:
                result["audio_files"].append({**a, "_path": path, "bytes": os.path.getsize(path)})
    linked = {os.path.basename(r.get("file_path") or "") for r in result["recordings"]}
    for a in result["audio_files"]:
        a["in_wal_index"] = a["file"] in linked
    return result
