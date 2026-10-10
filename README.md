# WearFX: Forensics for AI Audio Wearables

**Project 2 of 5** · Status: research complete, tool in progress, lab work not started
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
```

## Ethics in one line
Lab recordings use consenting participants or scripted text-to-speech personas only, on project-owned devices and accounts. Details in [research/06](research/06-legal-ethics.md).
