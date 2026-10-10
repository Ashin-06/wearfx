# 07 · Experiment Plan

## Hypotheses
| ID | Hypothesis |
|---|---|
| H1 | Omi caches full transcripts + summaries in SharedPreferences, readable from a logical extraction of a rooted/FFS Android phone |
| H2 | Deleting a conversation in the Omi app removes it from the cloud but leaves it in `cachedConversations` until the next refresh, and in old `wals.json.corrupt-*` copies |
| H3 | WAL audio files of synced recordings persist after sync (`kept_for_transcript_recovery`) |
| H4 | Omi device offline buffer (SD/flash) keeps audio after upload until overwritten |
| H5 | Plaud keeps audio on the device after cloud upload and after in-app deletion |
| H6 | Bee app caches daily summaries locally |
| H7 | Summaries contain claims unsupported by their own transcripts at a measurable rate; the lexical checker finds them with high recall on seeded errors |
| H8 | Speaker labels in transcripts are wrong often enough to matter for attribution |
| H9 | iOS encrypted backups include the Omi prefs plist and `Documents/` |

## Lab tasks
| ID | Task |
|---|---|
| L1 | Omi pendant + Android (rooted) + iPhone, lab account; 20 scripted conversations (TTS personas, known ground-truth script) |
| L2 | Extraction baseline: FFS Android, FFS/backup iOS; run `wearfx` |
| L3 | iOS backup coverage (H9) |
| L4 | Omi device storage: read SD/flash, map firmware layout (H4) |
| L5 | Plaud NotePin: same scripts, device USB/storage, app data, export SRT (H5) |
| L6 | Bee: same scripts, app data (H6) |
| L7 | Transcript vs audio: re-transcribe audio with a second engine (e.g. Whisper locally), diff against the vendor transcript; measure WER and speaker-label errors (H8) |
| L8 | Summary integrity: run `wearfx check` on all summaries vs ground-truth script and vs vendor transcript; seed known errors to measure recall (H7) |
| L9 | Anti-forensics: delete conversation, delete memory, unpair, sign out, uninstall, factory reset device; re-extract (H2, H3) |

## Metrics
- Artifact survival per action × platform (main table).
- Integrity checker: precision/recall on seeded errors; share of real summaries with ≥1 unsupported claim.
- Transcript WER and speaker-label accuracy against the script.

## Schedule (~12 weeks part-time)
1–2 buy and set up · 3–5 Omi (L1–L4) · 6–7 Plaud, Bee (L5, L6) · 8–9 integrity (L7, L8) · 10 anti-forensics (L9) · 11–12 paper, dataset, tool release.
