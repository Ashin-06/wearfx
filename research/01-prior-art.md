# 01 · Prior Art and the Gap

Searched 10 Oct 2026 (web search standard + extended, DFRWS, ScienceDirect, Wiley, GitHub).

## Closest published work

| Work | Device class | What it does | What it leaves open |
|---|---|---|---|
| [Panta, Alsmadi, Baggili, *Seeing the evidence*, DFRWS USA 2026](https://www.sciencedirect.com/science/article/pii/S2666281726000855) | Ray-Ban Meta AI glasses | glasses + Android app + cloud export; anti-forensics (delete, unpair, reset); ALEAPP plugin | not audio-first pendants; no AI-output integrity |
| [*Ex Machina*, DFRWS EU 2026 (FSI:DI)](https://www.sciencedirect.com/science/article/pii/S2666281726000077) | AI companion **apps** (6 apps, 25M+ downloads) | local retention, undocumented APIs, automated profiling tool | no hardware, no recorders |
| [Sakshi et al., *J. Forensic Sci.* 2026](https://onlinelibrary.wiley.com/doi/10.1111/1556-4029.70301) | smartwatches | non-privileged logical extraction framework; weak deletion | not recorders, no AI |
| [TomTom Spark 3 case study](https://www.sciencedirect.com/science/article/pii/S2665910721000293) | fitness watch | device + app + Bluetooth logs | old, no AI |

**No published forensic analysis exists for AI audio-recording wearables**: Omi, Plaud NotePin/Note, Bee, Limitless Pendant. Two extended searches found product reviews and privacy commentary only.

## Why it matters now

- These devices record conversations all day, including **bystanders**, and turn them into transcripts, summaries, action items and a searchable "memory".
- The AI output is the part people read, quote and act on. It is generated, not recorded.
- **Courts are starting to reject unverified AI transcripts.** Secondary coverage reports that in *Camarillo Hospitality LLC v. G6 Hospitality LLC* (E.D. Cal., Apr 2026) the judge sealed an AI-generated meeting transcript and declined to consider it because no party had shown it was accurate. The order itself has not been retrieved yet; verify on CourtListener/PACER before citing.
- A deposition-summarisation paper ([arXiv 2601.15182](https://arxiv.org/html/2601.15182v1)) cites >17% hallucination in leading AI legal tools, even with retrieval.

## Gap statement

> AI audio wearables produce three kinds of evidence: raw audio, machine transcripts, and generated summaries. No published work maps where each lives across device, phone and cloud, what survives deletion, or how an examiner can show whether a summary is supported by the recording. We provide the first evidence map (verified from source for the open-source Omi platform), an acquisition and anti-forensics test plan for closed devices, and an explainable summary-to-transcript integrity checker.

## Monitoring
Google Scholar alert `"AI wearable" forensic`, `Omi pendant`, `Plaud forensic`; DFRWS 2027 programmes.
