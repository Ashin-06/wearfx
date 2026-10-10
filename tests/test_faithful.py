from wearfx import faithful as f

SEGMENTS = [
    {"text": "Okay so we can do four thousand five hundred dollars for the launch.", "speaker": "Alice", "start": 0.0},
    {"text": "Fine. Bob will send the invoice by Tuesday at three p.m.", "speaker": "Carol", "start": 4.2},
    {"text": "And the discount stays at thirty percent.", "speaker": "Alice", "start": 9.0},
]


def test_normalize_spoken_forms():
    assert f.normalize("four thousand five hundred dollars") == "4500 dollars"
    assert f.normalize("twenty five people on March fourth") == "25 people on march 4"
    assert f.normalize("$4,500 at 3 PM") == "4500 at 3pm"
    assert f.normalize("thirty-two") == "32"
    assert f.normalize("five hundred and twenty") == "520"
    # adjacent numbers must not be summed (regression: "ten thirty" became 40)
    assert f.normalize("ten thirty") == "10 30"
    assert f.normalize("nineteen eighty four") == "19 84"
    assert f.normalize("one two three") == "1 2 3"
    assert f.normalize("twenty first") == "21"
    assert f.normalize("two hundred thousand") == "200000"


def test_time_spoken_and_identifier_digits():
    r = f.check([{"text": "meet at ten thirty in q three"}], "Meet at 10:30 for Q3.")
    by = {c["claim"]: c for c in r["claims"]}
    assert by["10:30"]["status"] == "supported"
    assert "3" not in by  # the digit inside "Q3" is not a number claim


def test_supported_claims_point_to_segment():
    summary = "Agreed $4,500 for the launch. Bob sends the invoice by Tuesday 3pm. Discount stays 30%."
    r = f.check(SEGMENTS, summary)
    by = {c["claim"]: c for c in r["claims"]}
    assert by["$4,500"]["status"] == "supported" and by["$4,500"]["segment"] == 0
    assert by["3pm"]["status"] == "supported" and by["3pm"]["speaker"] == "Carol"
    assert by["Tuesday"]["type"] == "date" and by["Tuesday"]["status"] == "supported"
    assert by["Bob"]["type"] == "name" and by["Bob"]["status"] == "supported"
    assert by["30%"]["status"] == "supported"
    assert r["unsupported"] == 0 and r["score"] == 1.0
    assert "Agreed" not in by  # sentence-starting verb is not a name


def test_hallucinated_claims_flagged():
    # $5,000 was never said, Dave never appears, Friday is wrong, the quote was never spoken
    summary = 'Agreed $5,000. Dave sends the invoice on Friday. Alice said "we will double the budget".'
    r = f.check(SEGMENTS, summary)
    unsupported = {c["claim"] for c in r["claims"] if c["status"] == "unsupported"}
    assert {"$5,000", "Dave", "Friday", "we will double the budget"} <= unsupported
    assert any(c["claim"] == "Alice" and c["status"] == "supported" for c in r["claims"])
    assert r["score"] < 0.5


def test_srt_and_txt_loaders(tmp_path):
    srt = tmp_path / "t.srt"
    srt.write_text("1\n00:00:01,500 --> 00:00:03,000\nSpeaker 1: four thousand five hundred\n\n"
                   "2\n00:01:02,000 --> 00:01:04,000\nno speaker line\n", encoding="utf-8")
    segs = f.load_transcript(str(srt))
    assert segs[0] == {"text": "four thousand five hundred", "speaker": "Speaker 1", "start": 1.5}
    assert segs[1]["speaker"] is None and segs[1]["start"] == 62.0
    txt = tmp_path / "t.txt"
    txt.write_text("[00:00:05] Alice: hello there\n\nBob: hi\n", encoding="utf-8")
    segs = f.load_transcript(str(txt))
    assert segs == [{"text": "hello there", "speaker": "Alice", "start": "00:00:05"},
                    {"text": "hi", "speaker": "Bob", "start": None}]


def test_summary_text_from_omi_conversation():
    conv = {"title": "Budget", "overview": "Agreed.", "action_items": ["Bob sends invoice"], "events": []}
    assert f.summary_text(conv) == "Budget\nAgreed.\n- Bob sends invoice"
    assert f.check([], "")["score"] is None
