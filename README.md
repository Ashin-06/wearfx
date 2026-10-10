# WearFX: Forensics for AI Audio Wearables

**Project 2 of 5** · Status: research complete, tool built and tested (17 tests), lab work not started
Research cut-off: 10 Oct 2026 (Omi `BasedHardware/omi@14fab5f`)

## What this is

AI pendants (Omi, Plaud NotePin, Bee, Limitless) record conversations all day and turn them into transcripts, summaries, action items and a searchable "memory". When one of these, or the paired phone, becomes evidence, nobody has documented:

- where the audio, transcript and summary live (device, phone, cloud);
- what survives deletion, unpairing and reset;
- whether the AI summary people quote is actually backed by what was said.

That last point already matters in court. In April 2026 a federal judge set aside an AI meeting transcript because nobody had shown it was accurate (see [research/01](research/01-prior-art.md)).

WearFX provides:
- an **evidence map**, verified from source for the open-source Omi platform;
- **acquisition and anti-forensics plans** for Omi, Plaud and Bee;
- a **tool** that parses Omi phone artifacts and **checks AI summaries claim by claim against their transcripts**, including Plaud SRT/TXT exports;
- a **paper** plan on the DFRWS model.

## Why it is novel

| Exists | Covers | Missing |
|---|---|---|
| Ray-Ban Meta, DFRWS USA 2026 | AI glasses + app + cloud | audio pendants; AI-output integrity |
| *Ex Machina*, DFRWS EU 2026 | AI companion apps | hardware, recorders |
| Smartwatch frameworks (JFS 2026) | wearables, weak deletion | AI, audio |
| Summary-hallucination research | LLM faithfulness in general | forensic method, device evidence |

## Key findings so far (Omi, from source)

1. **No SQL database.** The phone app keeps everything in `FlutterSharedPreferences.xml` (Android) or the prefs plist (iOS), plus files.
2. **Cached conversations hold full transcripts and the AI summary**, with speaker labels, timings and GPS.
3. **`wals.json` indexes every offline recording**: start time, duration, device, upload and sync status, GPS, linked conversation. If the index is ever judged corrupt, the app **renames it to `wals.json.corrupt-<µs>` instead of deleting it**, so older copies can survive.
4. **Webhook URLs** in preferences show which third-party servers received the user's conversations.
5. **Omi imports Limitless pendant recordings** (`audio_limitless_…bin`), linking a second vendor's device to an Omi account.

## Repository layout

```
02-ai-wearable-forensics/
├── README.md
├── research/
│   ├── 01-prior-art.md              gap, Camarillo case, monitoring
│   ├── 02-devices.md                Omi, Plaud, Bee, Limitless architectures
│   ├── 03-evidence-map.md           every artifact, per platform
│   ├── 04-acquisition.md            order of volatility, phone/device/cloud SOPs
│   ├── 05-ai-summary-integrity.md   the claim-checking method and its limits
│   ├── 06-legal-ethics.md           consent law, lab rules, dual use
│   ├── 07-experiment-plan.md        hypotheses H1-H9, lab tasks L1-L9
│   ├── 08-paper-outline.md
│   └── sources.md
├── wearfx/                          Python package, standard library only, read-only
│   ├── flutterprefs.py              Flutter shared_preferences: Android XML + iOS plist, list/double encodings
│   ├── omi.py                       Omi: account, devices, webhooks, conversations, memories, WAL index, audio
│   ├── faithful.py                  AI summary vs transcript, claim by claim; SRT/TXT/Omi loaders
│   ├── report.py                    merged timeline + integrity table; JSON/CSV/HTML
│   └── cli.py                       `wearfx` command
├── tests/                           pytest suite (17 tests)
└── pyproject.toml
```

## Tool

```bash
python -m venv .venv && .venv/Scripts/pip install -e .[test]   # Linux/macOS: .venv/bin/pip
pytest -q
```

Every command only reads its inputs. Run it on a hash-verified copy of the extraction.

```bash
wearfx prefs     FlutterSharedPreferences.xml                  # decode any Flutter prefs file
wearfx omi       extracted/com.friend.ios/                     # every Omi artifact found, with source paths
wearfx check     --transcript call.srt --summary summary.md    # Plaud/any export: claim-by-claim integrity
wearfx check-omi extracted/com.friend.ios/                     # integrity of every cached Omi conversation
wearfx report    extracted/com.friend.ios/ --format html > case.html
```

How to read an integrity result:
- `supported` gives the transcript segment, speaker and start time, so you can play it back.
- `unsupported` means the claim's key word or number is not in the transcript. That is a lead (the speech-to-text may have misheard), not proof of fabrication.
- `name?` is a capitalised word that only starts a sentence or title. It might be an ordinary word, so it is listed and checked but not counted in the score.
- Omissions (something important the summary left out) are not detected.

| Feature | Checked against | Status |
|---|---|---|
| Flutter prefs (Android XML, iOS binary plist, list/double/BigInteger encodings) | encodings from `flutter/packages` source | ✅ tests |
| Omi account, devices, webhooks, conversations, memories | field names from `BasedHardware/omi@14fab5f` | ✅ tests; ⏳ real extraction is lab task L2 |
| WAL index incl. `.corrupt-*` copies, audio names (incl. Limitless), orphan audio | `wal.dart`, `wal_file_manager.dart` | ✅ tests |
| Integrity checker: numbers, money, %, times, dates, names, quotes; spoken-number grammar | seeded hallucinations, regressions ("ten thirty" ≠ 40) | ✅ tests; ⏳ recall on real summaries is lab task L8 |
| Report: timeline, integrity, unreadable files; HTML escaped | synthetic case | ✅ tests |

### Known gaps
- **Plaud, Bee, Limitless app data** are closed and not parsed yet (lab tasks L5, L6). Plaud **exports** (SRT/TXT) already work with `check`.
- **Omi device storage** (SD card, SPI flash) not parsed (lab task L4).
- **Audio** is listed and linked, not decoded or compared with the transcript (lab task L7).
- **Older Android list encoding** (Java-serialised) is kept raw, not decoded.
- No real-device validation yet: all tests use data built from the apps' own source.

## Ethics in one line
Lab recordings use consenting participants or scripted text-to-speech personas only, on project-owned devices and accounts. Details in [research/06](research/06-legal-ethics.md).
