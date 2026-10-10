# 05 · AI Summary Integrity

## The problem
A wearable produces three layers:

| Layer | Made by | Reliability |
|---|---|---|
| Audio | microphone | best evidence; can be authenticated |
| Transcript | speech-to-text model | errors in words and **speaker labels** |
| Summary, action items, "memories" | LLM | can add facts that were never said (hallucination) or drop the one that matters (omission) |

People quote the summary. Courts want the audio. The examiner needs to show, claim by claim, whether the summary is backed by the transcript, and then check the transcript against the audio.

## Method (implemented in `wearfx/faithful.py`)
Deterministic and explainable: every finding points to a transcript segment and time, so a reviewer can check it by ear.

1. **Extract checkable claims** from the summary text (title, overview, action items, events, memories):
   - numbers, money, percentages (`$4,500`, `30%`, `12`)
   - times and dates (`3pm`, `15:30`, `Tuesday`, `March 4`)
   - proper names (capitalised words not at the start of a sentence, plus capitalised words anywhere that are not common words)
   - quoted phrases (`"..."`)
2. **Normalise** both sides: case, punctuation, thousands separators; number words to digits (`three` → `3`, `twenty five` → `25`).
3. **Search the transcript** for each claim. Report `supported` with the segment index, speaker and start time, or `unsupported`.
4. **Action-item owners:** a name in an action item that never appears in the transcript is flagged.
5. **Score** = supported / checkable claims, reported with the list, never alone.

## What the check proves and does not prove
- `unsupported` means the claim's key token is absent from the transcript. It is a **lead**, not proof of fabrication: STT may have misheard the word, or the summary may paraphrase.
- `supported` means the token appears somewhere. It does **not** prove the summary used it correctly (e.g. right number, wrong person).
- It does not detect omissions. Pair it with a human read of the transcript for decisive passages.
- It does not check the transcript against the audio. That is lab task L7 (re-transcribe the audio with a second engine and diff).

## Why lexical, not an LLM judge
An LLM judge is itself a generated opinion that would need its own validation, and its output can change between runs. A lexical check is repeatable, explainable in court, and runs offline on sensitive evidence. An LLM-based semantic pass can be added later as a second, clearly labelled opinion.

## Inputs supported
- Omi cached conversation JSON (structured + transcript_segments)
- Plaud or other exports: transcript as **SRT** or **TXT** (`Speaker: text` lines), summary as text/Markdown
