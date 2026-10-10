# 08 · Paper Plan

**Working title:** "Recorded, Transcribed, Summarised: Forensic Analysis of AI Audio Wearables and the Integrity of Their Generated Evidence"

**Venues:** DFRWS USA/EU (FSI: Digital Investigation) first; *Forensic Science International: Digital Investigation* journal for the extended version; a law-and-technology venue for the integrity angle.

## Outline
1. Introduction: always-on AI recorders; three evidence layers; the Camarillo exclusion
2. Background: Omi (open), Plaud, Bee, Limitless; capture-to-summary pipelines
3. Related work: Ray-Ban Meta, AI companion apps, smartwatch frameworks, summarisation faithfulness
4. Methodology: devices, scripted personas, ground truth, extraction, anti-forensics, ethics
5. Evidence map: phone, device, cloud; per vendor
6. Results: survival matrix; deletion behaviour; cross-vendor comparison (Limitless → Omi import)
7. Integrity: transcript WER and speaker errors; summary unsupported-claim rates; checker validation
8. Tool: `wearfx` design, validation
9. Discussion: guidance for examiners, courts and users
10. Conclusion

## Contributions
1. First evidence map for AI audio wearables (verified from source for Omi).
2. Anti-forensics survival study across four ecosystems.
3. Measurement of transcript and summary error in real devices against ground truth.
4. `wearfx`: Omi parser + explainable summary integrity checker, open source.
