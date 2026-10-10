import json

from test_omi import CONV, _prefs_xml  # reuse the synthetic Omi fixtures

from wearfx import report


def _case(tmp_path):
    (tmp_path / "shared_prefs").mkdir()
    _prefs_xml(tmp_path / "shared_prefs" / "FlutterSharedPreferences.xml")
    docs = tmp_path / "app_flutter"
    docs.mkdir()
    name = "audio_abc_opus_16000_1_fs160_1759312200.bin"
    (docs / name).write_bytes(b"\x00" * 4)
    (docs / "audio_abc_opus_16000_1_fs160_1759399999.bin").write_bytes(b"\x00")
    (docs / "wals.json").write_text(json.dumps({"wals": [
        {"timer_start": 1759312200, "seconds": 1800, "codec": "opus", "device": "abc", "device_model": "Omi",
         "status": "synced", "storage": "disk", "file_path": name, "conversation_id": "c1"}]}))
    (docs / "wals.json.corrupt-1").write_text("{broken")
    return report.from_root(str(tmp_path))


def test_report_contents(tmp_path):
    rep = _case(tmp_path)
    kinds = [e["kind"] for e in rep["events"]]
    assert {"recording", "conversation", "memory", "audio_file", "audio_file_orphan", "index_error"} <= set(kinds)
    assert kinds[-1] == "index_error"  # no timestamp sorts last
    times = [e["ts"] for e in rep["events"] if e["ts"]]
    assert times == sorted(times)
    integ = rep["integrity"][0]
    assert integ["conversation"] == CONV["id"] and integ["score"] is not None
    assert rep["account"]["webhooks"]


def test_renderers_escape(tmp_path):
    rep = _case(tmp_path)
    rep["events"].append({"time_utc": None, "kind": "memory", "detail": "<script>x</script>", "source": "t"})
    h = report.to_html(rep)
    assert "&lt;script&gt;" in h and "<script>x" not in h
    assert report.to_csv(rep).startswith("time_utc,kind,detail")
    assert json.loads(report.to_json(rep))["integrity"]


def test_errors_reported(tmp_path):
    rep = _case(tmp_path)
    assert rep["errors"] == []
    rep["errors"] = [{"file": "x.plist", "error": "InvalidFileException: bad <data>"}]
    h = report.to_html(rep)
    assert "Unreadable files" in h and "bad &lt;data&gt;" in h
