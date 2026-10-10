import json
from xml.sax.saxutils import escape

from wearfx import flutterprefs as fp
from wearfx import omi

CONV = {
    "id": "c1", "created_at": "2026-10-01T10:00:00Z", "started_at": "2026-10-01T09:30:00Z",
    "finished_at": "2026-10-01T10:00:00Z",
    "structured": {"title": "Budget sync", "overview": "Agreed $4,500 for the launch.",
                   "category": "work", "action_items": [{"description": "Bob sends the invoice"}],
                   "events": [{"title": "Launch review"}]},
    "transcript_segments": [
        {"text": "We can do four thousand five hundred dollars.", "speaker": "SPEAKER_00", "is_user": True,
         "start": 0.0, "end": 3.2},
        {"text": "Fine, I will send the invoice.", "speaker": "SPEAKER_01", "is_user": False,
         "start": 3.5, "end": 5.0}],
    "geolocation": {"latitude": 37.77, "longitude": -122.41, "address": "SF"},
    "deleted": False,
}
MEM = {"content": "Bob handles invoices", "category": "work", "created_at": "2026-10-01T10:01:00Z",
       "conversation_id": "c1"}


def _prefs_xml(path):
    lst = lambda items: escape(fp.JSON_LIST_PREFIX + json.dumps([json.dumps(i) for i in items]))
    path.write_text(
        "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n<map>\n"
        '<string name="flutter.uid">u-123</string>\n'
        '<string name="flutter.email">alice@example.com</string>\n'
        f'<string name="flutter.btDevice">{escape(json.dumps({"name": "Omi", "id": "AA:BB:CC:DD:EE:FF"}))}</string>\n'
        '<string name="flutter.webhookOnConversationCreated">https://hooks.example.net/x</string>\n'
        '<string name="flutter.webhookDaySummary"></string>\n'
        f'<string name="flutter.cachedConversations">{lst([CONV])}</string>\n'
        f'<string name="flutter.cachedMemories:u-123">{lst([MEM])}</string>\n'
        "</map>\n", encoding="utf-8")


def test_account_conversations_memories(tmp_path):
    p = tmp_path / "FlutterSharedPreferences.xml"
    _prefs_xml(p)
    prefs = fp.read(str(p))
    acc = omi.account(prefs)
    assert acc["uid"] == "u-123" and acc["bt_device"]["id"] == "AA:BB:CC:DD:EE:FF"
    assert acc["webhooks"] == {"webhookOnConversationCreated": "https://hooks.example.net/x"}  # empty one dropped
    conv = omi.conversations(prefs)[0]
    assert conv["title"] == "Budget sync" and conv["action_items"] == ["Bob sends the invoice"]
    assert conv["segments"][1]["speaker"] == "SPEAKER_01" and conv["latitude"] == 37.77
    assert omi.memories(prefs)[0]["content"] == "Bob handles invoices"


def test_wals_index_and_corrupt():
    idx = {"wals": [{"timer_start": 1760000000, "seconds": 60, "codec": "opus", "device": "abc",
                     "device_model": "Omi", "status": "synced", "storage": "disk",
                     "file_path": "audio_abc_opus_16000_1_fs160_1760000000.bin", "conversation_id": "c1",
                     "geolocation": {"latitude": 1.5, "longitude": 2.5}},
                    "garbage"]}
    rows = omi.wals(json.dumps(idx).encode())
    assert rows[0]["end"] == 1760000060 and rows[0]["latitude"] == 1.5
    assert rows[1] == {"_error": "non-object entry"}
    assert "_error" in omi.wals(b"{not json")[0]


def test_audio_names():
    a = omi.audio_file("audio_abc_opus_16000_1_fs160_1760000000.bin")
    assert a["device"] == "abc" and a["start"] == 1760000000 and a["frame_size"] == 160
    lim = omi.audio_file("audio_limitless_opus_16000_1_fs320_rXy12_1760000000123.bin")
    assert lim["device"] == "limitless" and lim["start"] == 1760000000  # ms -> s
    assert omi.audio_file("notes.txt") is None


def test_scan_directory(tmp_path):
    (tmp_path / "shared_prefs").mkdir()
    _prefs_xml(tmp_path / "shared_prefs" / "FlutterSharedPreferences.xml")
    docs = tmp_path / "app_flutter"
    docs.mkdir()
    name = "audio_abc_opus_16000_1_fs160_1760000000.bin"
    (docs / name).write_bytes(b"\x00" * 10)
    (docs / "audio_abc_opus_16000_1_fs160_1760009999.bin").write_bytes(b"\x00")  # orphan: not in index
    (docs / "wals.json").write_text(json.dumps({"wals": [{"timer_start": 1760000000, "seconds": 60,
                                                          "codec": "opus", "device": "abc", "file_path": name}]}))
    (docs / "wals.json.corrupt-1760000000000000").write_text("{broken")
    r = omi.scan(str(tmp_path))
    assert r["account"]["email"] == "alice@example.com"
    assert len(r["conversations"]) == 1 and len(r["wal_indexes"]) == 2
    linked = {a["file"]: a["in_wal_index"] for a in r["audio_files"]}
    assert linked == {name: True, "audio_abc_opus_16000_1_fs160_1760009999.bin": False}
