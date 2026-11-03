"""Read Flutter `shared_preferences` files: Android FlutterSharedPreferences.xml or an iOS prefs plist.

Encodings from flutter/packages shared_preferences_android (SharedPreferencesPlugin.kt,
LegacySharedPreferencesPlugin.kt). Read-only; returns {key_without_"flutter."_prefix: value}.
"""
import json
import plistlib
import defusedxml.ElementTree as ET  # a seized phone's file is hostile input: no entity expansion, no DTDs
from pathlib import Path

LIST_PREFIX = "VGhpcyBpcyB0aGUgcHJlZml4IGZvciBhIGxpc3Qu"         # "This is the prefix for a list."
JSON_LIST_PREFIX = LIST_PREFIX + "!"
DOUBLE_PREFIX = "VGhpcyBpcyB0aGUgcHJlZml4IGZvciBEb3VibGUu"       # "...for Double."
BIG_INTEGER_PREFIX = "VGhpcyBpcyB0aGUgcHJlZml4IGZvciBCaWdJbnRlZ2Vy"  # "...for BigInteger"


def _decode_string(v: str):
    if v.startswith(JSON_LIST_PREFIX):
        return json.loads(v[len(JSON_LIST_PREFIX):])
    if v.startswith(LIST_PREFIX):
        # ponytail: older plugin versions Java-serialised the list; kept raw, decode if a case needs it
        return {"_legacy_java_list_base64": v[len(LIST_PREFIX):]}
    if v.startswith(DOUBLE_PREFIX):
        return float(v[len(DOUBLE_PREFIX):])
    if v.startswith(BIG_INTEGER_PREFIX):
        return int(v[len(BIG_INTEGER_PREFIX):], 36)
    return v


def _strip(key: str) -> str:
    return key[len("flutter."):] if key.startswith("flutter.") else key


def read_android_xml(data: bytes) -> dict:
    out = {}
    for el in ET.fromstring(data):
        name, tag = el.get("name"), el.tag
        if tag == "string":
            val = _decode_string(el.text or "")
        elif tag == "boolean":
            val = el.get("value") == "true"
        elif tag in ("int", "long"):
            val = int(el.get("value"))
        elif tag == "float":
            val = float(el.get("value"))
        elif tag == "set":
            val = [s.text or "" for s in el]
        else:
            val = el.get("value", el.text)
        out[_strip(name)] = val
    return out


def read_plist(data: bytes) -> dict:
    return {_strip(k): v for k, v in plistlib.loads(data).items()}


def read(path: str) -> dict:
    data = Path(path).read_bytes()
    if data.lstrip()[:5] == b"<?xml" and b"<map" in data[:4096]:
        return read_android_xml(data)
    return read_plist(data)  # binary or XML plist
