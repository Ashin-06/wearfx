# Threat model

What the analysis service protects, from whom, and what is still open. Written for the 1.0.0 code;
nobody independent has reviewed it.

## What it protects

| Asset | Where it lives |
|---|---|
| Submitted evidence (extractions, transcripts, AI summaries) | request bodies and a per-request temporary directory; never stored |
| The custody log (who submitted which input hash, when, and the counts found) | `analyses` table |
| API keys | callers hold the key; the service holds only SHA-256 hashes |

Evidence is highly personal: recorded conversations, locations, contacts. Findings feed criminal
and civil cases, so a wrong or tampered result matters as much as a leak.

## Trust boundaries

1. **Examiner → service.** Uploads are hostile by default: a seized device's files may have been
   crafted to break forensic tools.
2. **Service → database.** The custody log holds hashes and counts only.

## Threats and what stops them

| Threat | Mitigation | Residual risk |
|---|---|---|
| A crafted zip escapes the temporary directory | Absolute paths, `..` and symlink entries are refused before anything is written | — |
| Zip bomb or oversized upload | 50 MB body cap (with or without content-length), 20,000 files and 500 MB unpacked per zip, each member written only up to its declared size | Disk use is bounded per request, not across concurrent requests |
| Hostile XML preferences (entity expansion) | `defusedxml` refuses entity declarations and DTDs | Binary plists are parsed by `plistlib` |
| Script injection into the HTML report | Every value is HTML-escaped | — |
| Someone reads the custody log or submits evidence | API keys with roles; no CORS unless listed | Every `viewer` sees every analysis |
| Evidence leaks through errors or logs | Validation errors don't echo input; unhandled errors return only a request ID; logs carry no bodies | — |
| A report is disputed later | The log keeps the SHA-256 of every input and the response carries it (`x-input-sha256`), so a result can be tied to an exhibit | The log itself is not signed or hash-chained |
| Wrong conclusions from the checker | Results say `unsupported` (a lead), never "fabricated"; low-confidence names are not scored | Misses and false flags still happen (see the README) |

## Not covered

- Acquisition: the service analyses extractions; it does not image devices.
- Signing reports or anchoring the custody log.
- TLS (terminate it at the ingress).
