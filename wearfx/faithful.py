"""Check an AI summary against its transcript, claim by claim (method: research/05).

Lexical and deterministic, so every finding is repeatable and points at a transcript segment a
reviewer can play back. `unsupported` is a lead (STT may have misheard), not proof of fabrication;
`supported` means the token occurs, not that the summary used it correctly. Omissions are not
detected.
"""
import re
from pathlib import Path

_UNITS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen".split())}
_UNITS.update({w: i for i, w in enumerate(
    "zeroth first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth "
    "fourteenth fifteenth sixteenth seventeenth eighteenth nineteenth".split()) if i})
_TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if i > 1}
_TENS.update({"twentieth": 20, "thirtieth": 30})
_SCALES = {"hundred": 100, "thousand": 1000, "million": 10**6, "billion": 10**9}
_NUMWORD = set(_UNITS) | set(_TENS) | set(_SCALES)

MONTHS = "january february march april may june july august september october november december".split()
WEEKDAYS = "monday tuesday wednesday thursday friday saturday sunday".split()
# Capitalised sentence starters that are not names: function words and common action-item verbs.
_NOT_NAMES = set("""a an the and but or so then also i we you he she it they this that these those our
their his her its my your there here if when after before during while for to of in on at by with from
agreed decided discussed reviewed confirmed planned noted mentioned asked said talked shared meeting
send review schedule follow call email prepare update check finalize finalise share book confirm discuss
plan set create draft write submit complete arrange organize organise contact reach ask tell get make
buy order pay sign call text remind look find fix test deploy ship start finish continue overview
summary action items item events event key points notes next steps title""".split())


def _kind(w: str) -> str:
    if w in _SCALES:
        return "scale"
    if w in _TENS:
        return "tens"
    return "teen" if _UNITS[w] >= 10 else "unit"


# Which word kind may follow which inside one number: "twenty five", "five hundred", "ten thousand".
# Anything else starts a new number, so "ten thirty" -> "10 30", "nineteen eighty four" -> "19 84".
_FOLLOWS = {None: {"unit", "teen", "tens", "scale"}, "unit": {"scale"}, "teen": {"scale"},
            "tens": {"unit", "scale"}, "scale": {"unit", "teen", "tens", "scale"}}


def _words_to_digits(text: str) -> str:
    """'four thousand five hundred' -> '4500', 'twenty five' -> '25', 'march fourth' -> 'march 4'."""
    out = []
    total = current = 0
    last = None

    def flush():
        nonlocal total, current, last
        if last is not None:
            out.append(str(total + current))
        total = current = 0
        last = None

    for tok in re.findall(r"[a-z0-9:%.$€£₹']+|[^a-z0-9:%.$€£₹'\s]", text):
        if tok == "and" and last == "scale":
            continue  # "five hundred and twenty"
        if tok not in _NUMWORD:
            flush()
            out.append(tok)
            continue
        k = _kind(tok)
        if k not in _FOLLOWS[last]:
            flush()
        if k == "scale":
            if tok == "hundred":
                current = (current or 1) * 100
            else:
                total += (current or 1) * _SCALES[tok]
                current = 0
        else:
            current += _UNITS.get(tok, 0) + _TENS.get(tok, 0)
        last = k
    flush()
    return " ".join(out)


def normalize(text: str) -> str:
    t = text.lower().replace("p.m.", "pm").replace("a.m.", "am").replace("-", " ")
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)          # 4,500 -> 4500
    t = _words_to_digits(t)
    t = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", t)        # 4th -> 4
    t = re.sub(r"(\d)\s+(am|pm)\b", r"\1\2", t)         # 3 pm -> 3pm
    t = re.sub(r"[$€£₹%]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


_TIME = re.compile(r"\b\d{1,2}(?::\d{2})?\s?(?:[ap]m|[ap]\.m\.)(?![a-z])|\b\d{1,2}:\d{2}\b", re.I)
_NUM = re.compile(r"(?<![A-Za-z])[$€£₹]?\d[\d,]*(?:\.\d+)?%?")  # skip digits inside ids like Q3
_QUOTE = re.compile(r"[\"“”]([^\"“”]{3,})[\"“”]")
_CAP = re.compile(r"\b[A-Z][a-zA-Z'’-]+\b")


def extract_claims(summary: str) -> list[dict]:
    """Checkable claims in summary text: quote, time, number, date word, name."""
    claims, seen = [], set()

    def add(kind, raw, norm):
        if norm and (kind, norm) not in seen:
            seen.add((kind, norm))
            claims.append({"type": kind, "claim": raw, "normalized": norm})

    for m in _QUOTE.finditer(summary):
        add("quote", m.group(1), normalize(m.group(1)))
    masked = summary
    for m in _TIME.finditer(summary):
        add("time", m.group(0), normalize(m.group(0)).replace(" ", ""))
        masked = masked.replace(m.group(0), " ")
    for m in _NUM.finditer(masked):
        n = normalize(m.group(0))
        if n:
            add("number", m.group(0), n)
    # A capitalised word mid-sentence is a name. One that only ever starts a sentence, bullet or
    # title ("Budget sync", "Bob sends...") may be an ordinary word: kept as low-confidence "name?".
    caps = []
    for sentence in re.split(r"(?<=[.!?:;\n])\s*|^\s*[-*•]\s*", summary, flags=re.M):
        lead = len(sentence) - len(sentence.lstrip(" \t-*•#>"))
        caps += [(m.group(0).strip("'’"), m.start() == lead) for m in _CAP.finditer(sentence)]
    mid = {w.lower() for w, initial in caps if not initial}
    for w, _ in caps:
        lw = w.lower()
        if lw in MONTHS or lw in WEEKDAYS:
            add("date", w, lw)
        elif lw not in _NOT_NAMES:
            add("name" if lw in mid else "name?", w, lw)
    return claims


def check(segments: list[dict], summary: str) -> dict:
    """segments: [{"text", "speaker"?, "start"?}]. Returns claims with support, plus counts."""
    norm_segs = [normalize(s.get("text") or "") for s in segments]
    norm_spk = [normalize(s.get("speaker") or "") for s in segments]
    results = []
    for c in extract_claims(summary):
        body = re.escape(c["normalized"])
        if c["type"] == "time":
            body = body.replace(":", "[: ]")  # spoken "ten thirty" normalises to "10 30"
        pat = re.compile(r"(?<![a-z0-9])" + body + r"(?![a-z0-9])")
        hit = next((i for i, t in enumerate(norm_segs) if pat.search(t)), None)
        if hit is None and c["type"] in ("name", "name?"):  # "Alice said..." is backed by Alice speaking
            hit = next((i for i, t in enumerate(norm_spk) if pat.search(t)), None)
        if hit is None:
            results.append({**c, "status": "unsupported"})
        else:
            s = segments[hit]
            results.append({**c, "status": "supported", "segment": hit, "speaker": s.get("speaker"),
                            "start": s.get("start"), "context": (s.get("text") or "")[:160]})
    scored = [r for r in results if r["type"] != "name?"]  # low-confidence names are listed, not scored
    sup = sum(r["status"] == "supported" for r in scored)
    return {"checkable": len(scored), "supported": sup, "unsupported": len(scored) - sup,
            "low_confidence": len(results) - len(scored),
            "score": round(sup / len(scored), 3) if scored else None, "claims": results}


# ---- transcript loaders ----------------------------------------------------------------------
_SPEAKER = re.compile(r"^\s*(?:\[(?P<ts>[\d:.,]+)\]\s*)?(?P<spk>[^:\[\]]{1,40}):\s+(?P<text>.+)$")
_SRT_TIME = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->")


def _secs(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def load_srt(text: str) -> list[dict]:
    segs = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip()):
        lines = block.split("\n")
        t = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if t is None:
            continue
        body = " ".join(lines[t + 1:]).strip()
        m = _SPEAKER.match(body)
        start = _secs(*_SRT_TIME.search(lines[t]).groups()) if _SRT_TIME.search(lines[t]) else None
        segs.append({"text": m["text"] if m else body, "speaker": m["spk"].strip() if m else None,
                     "start": start})
    return segs


def load_txt(text: str) -> list[dict]:
    segs = []
    for ln in text.splitlines():
        if not ln.strip():
            continue
        m = _SPEAKER.match(ln)
        segs.append({"text": m["text"] if m else ln.strip(), "speaker": m["spk"].strip() if m else None,
                     "start": m["ts"] if m and m["ts"] else None})
    return segs


def load_transcript(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8-sig")
    return load_srt(text) if path.lower().endswith(".srt") or "-->" in text[:500] else load_txt(text)


def summary_text(conv: dict) -> str:
    """Summary side of an Omi conversation (as normalised by wearfx.omi): title, overview, items, events."""
    parts = [conv.get("title") or "", conv.get("overview") or ""]
    parts += [f"- {a}" for a in conv.get("action_items") or [] if a]
    parts += [f"- {e}" for e in conv.get("events") or [] if e]
    return "\n".join(p for p in parts if p)
