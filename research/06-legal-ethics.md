# 06 · Legal and Ethical Ground Rules

Not legal advice. Get supervisor or ethics-board approval before recording anyone.

## Lab rules
1. Only devices and accounts bought for the project. Lab accounts use project email addresses.
2. **Record only consenting participants**, or scripted audio played from a speaker (text-to-speech personas). No recording in public spaces.
3. Synthetic personas and scripts for every published dataset. No real names, voices or locations.
4. Turn off webhooks and third-party app integrations on lab accounts, except in the specific test that studies them (then point them at a local server).
5. Delete lab cloud data at the end and record the deletion date.

## Recording-consent law (why it matters for both the study and the casework)
- **One-party vs all-party consent:** US federal law and most states allow recording if one party consents; about a dozen states (e.g. California, Florida, Illinois, Washington) require all parties. Always-on pendants capture bystanders who never consented.
- **EU/UK GDPR:** voices and transcripts are personal data; recording others needs a lawful basis. Household exemption is narrow.
- **India DPDP Act 2023:** personal data, consent-based processing.
- Vendors respond differently: Limitless had a "Consent Mode"; Plaud is button-press; Bee and Omi are always-listening by default.

## Evidence standards
- Audio is primary evidence; transcripts and summaries are derived. Report them as such.
- *Camarillo Hospitality v. G6 Hospitality* (E.D. Cal., Apr 2026, per secondary coverage): an AI transcript was set aside because its accuracy was not shown. The integrity checker exists to support exactly that showing (or to show it cannot be made).
- ISO/IEC 27037, NIST SP 800-86, SWGDE mobile and IoT guidance.

## Dual use
- The tool parses data from devices and exports lawfully in the examiner's hands. It does not bypass app encryption, extract tokens, or access cloud accounts.
- Findings that are vulnerabilities (e.g. data that survives a "delete") go to the vendor first (Omi has a public repo; Plaud lists a trust/security contact) with a fix window before publication.
- Publish a short user guide: "What your AI pendant keeps, and where".
