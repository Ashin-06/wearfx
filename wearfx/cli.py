"""wearfx command line. Every command only reads its inputs."""
import argparse
import json
import sys

from wearfx import flutterprefs, omi


def _dump(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def main(argv=None):
    p = argparse.ArgumentParser(prog="wearfx", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prefs", help="decode a Flutter prefs file (Android XML or iOS plist)").add_argument("file")
    sub.add_parser("omi", help="scan an extracted Omi app directory").add_argument("root")
    a = p.parse_args(argv)

    if a.cmd == "prefs":
        _dump(flutterprefs.read(a.file))
    elif a.cmd == "omi":
        _dump(omi.scan(a.root))


if __name__ == "__main__":
    sys.exit(main())
