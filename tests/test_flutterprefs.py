import json
import plistlib

from wearfx import flutterprefs as fp

XML = ("<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n<map>\n"
       '    <string name="flutter.email">alice@example.com</string>\n'
       '    <boolean name="flutter.locationEnabled" value="true" />\n'
       '    <long name="flutter.speaker_label_last_used_ms" value="1760000000000" />\n'
       f'    <string name="flutter.cachedConversations">{fp.JSON_LIST_PREFIX}{json.dumps(["{}", "{}"])}</string>\n'
       f'    <string name="flutter.ratio">{fp.DOUBLE_PREFIX}0.5</string>\n'
       f'    <string name="flutter.old">{fp.LIST_PREFIX}rO0ABXNy</string>\n'
       '    <set name="flutter.tags"><string>a</string><string>b</string></set>\n'
       "</map>\n")


def test_android_xml(tmp_path):
    p = tmp_path / "FlutterSharedPreferences.xml"
    p.write_text(XML, encoding="utf-8")
    d = fp.read(str(p))
    assert d["email"] == "alice@example.com"
    assert d["locationEnabled"] is True
    assert d["speaker_label_last_used_ms"] == 1760000000000
    assert d["cachedConversations"] == ["{}", "{}"]
    assert d["ratio"] == 0.5
    assert d["old"] == {"_legacy_java_list_base64": "rO0ABXNy"}
    assert d["tags"] == ["a", "b"]


def test_ios_plist_binary(tmp_path):
    p = tmp_path / "com.example.plist"
    p.write_bytes(plistlib.dumps({"flutter.uid": "u1", "flutter.cachedConversations": ["{}"], "NSOther": 1},
                                 fmt=plistlib.FMT_BINARY))
    d = fp.read(str(p))
    assert d == {"uid": "u1", "cachedConversations": ["{}"], "NSOther": 1}
