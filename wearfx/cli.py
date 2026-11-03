"""wearfx command line. Every command only reads its inputs."""
import argparse
import json
import sys
from pathlib import Path

from wearfx import faithful, flutterprefs, omi, report


def _dump(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def main(argv=None):
    p = argparse.ArgumentParser(prog="wearfx", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prefs", help="decode a Flutter prefs file (Android XML or iOS plist)").add_argument("file")
    sub.add_parser("omi", help="scan an extracted Omi app directory").add_argument("root")
    ck = sub.add_parser("check", help="check an AI summary against a transcript (.srt or .txt)")
    ck.add_argument("--transcript", required=True)
    ck.add_argument("--summary", required=True, help="summary text / Markdown file")
    sub.add_parser("check-omi", help="check every cached Omi conversation's summary").add_argument("root")
    rp = sub.add_parser("report", help="case report for an extracted Omi app directory")
    rp.add_argument("root")
    rp.add_argument("--format", choices=["json", "csv", "html"], default="json")
    sv = sub.add_parser("serve", help="analysis API (settings: WEARFX_* environment variables)")
    sv.add_argument("--host", help="default WEARFX_HOST or 127.0.0.1; any other address needs API keys")
    sv.add_argument("--port", type=int, help="default WEARFX_PORT or 8102")
    sub.add_parser("migrate", help="apply database migrations to WEARFX_DATABASE_URL")
    a = p.parse_args(argv)

    if a.cmd in ("serve", "migrate"):
        return _service(a)

    if a.cmd == "prefs":
        _dump(flutterprefs.read(a.file))
    elif a.cmd == "omi":
        _dump(omi.scan(a.root))
    elif a.cmd == "check":
        segs = faithful.load_transcript(a.transcript)
        _dump(faithful.check(segs, Path(a.summary).read_text(encoding="utf-8-sig")))
    elif a.cmd == "check-omi":
        _dump([{"conversation": c["id"], "title": c["title"], "_file": c["_file"],
                **faithful.check(c["segments"], faithful.summary_text(c))}
               for c in omi.scan(a.root)["conversations"]])
    elif a.cmd == "report":
        rep = report.from_root(a.root)
        print({"json": report.to_json, "csv": report.to_csv, "html": report.to_html}[a.format](rep))


def _service(a) -> int:
    import os

    from wearfx import db, ops

    if a.cmd == "serve":
        for flag, var in (("host", "WEARFX_HOST"), ("port", "WEARFX_PORT")):
            if getattr(a, flag) is not None:
                os.environ[var] = str(getattr(a, flag))
    try:
        settings = ops.load_settings()  # fail here, before uvicorn, with a readable message
    except ops.ConfigError as e:
        print(f"configuration error: {e}", file=sys.stderr)
        return 1
    if a.cmd == "migrate":
        print(*(db.migrate(db.engine(settings.database_url)) or ["up to date"]), sep="\n")
        return 0
    import uvicorn

    ops.setup_logging(settings.log_level)
    uvicorn.run("wearfx.api:app", host=settings.host, port=settings.port, log_config=None, access_log=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
