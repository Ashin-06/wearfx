# 03 · Evidence Map

Legend: ✅ confirmed in source (Omi) · 🧪 lab task · ❓ unknown (closed source)

## Omi phone app (Android `/data/data/com.friend.ios/`, iOS app container)

| Artifact | Location | Content | Status |
|---|---|---|---|
| Preferences | Android `shared_prefs/FlutterSharedPreferences.xml`; iOS `Library/Preferences/<bundle>.plist` | every key prefixed `flutter.` | ✅ |
| Account | `flutter.uid`, `flutter.email`, `flutter.givenName`, `flutter.familyName` | **owner identity** | ✅ |
| Paired device | `flutter.btDevice`, `flutter.btDevices`, `flutter.deviceName`, `flutter.deviceIdHash`, `flutter.deviceIsV2` | which pendant, BLE identity | ✅ |
| Cached conversations | `flutter.cachedConversations` (legacy `flutter.cachedMemories`) - string list of JSON | **transcript segments + AI summary** per conversation: `id, created_at, started_at, finished_at, structured{title, overview, emoji, category, action_items, events}, transcript_segments[{text, speaker, is_user, person_id, start, end}], geolocation, source, language, status, deleted, discarded, starred, folder_id` | ✅ |
| Cached memories (facts) | `flutter.cachedMemories:<uid>`, `pendingMemories`, `migratedMemories` | facts the AI extracted about the user and others | ✅ |
| Locally edited conversations | `flutter.modifiedConversationDetails` | user edits not yet synced | ✅ |
| **Webhooks** | `flutter.webhookOnConversationCreated`, `webhookOnTranscriptReceived`, `webhookDaySummary` | **third-party URLs that received the user's conversations** | ✅ |
| Location | `flutter.locationEnabled`, `locationPermissionRequested`; per-recording `geolocation` | whether recordings carry GPS | ✅ |
| Offline recording index | `Documents/wals.json`, `Documents/wals_backup.json` | `{"wals": [...]}`: `timer_start` (epoch s), `seconds`, `codec`, `sample_rate`, `channel`, `device`, `device_model`, `status` (inProgress, miss, uploaded, synced, corrupted, outsideRecoveryWindow, unsupportedAudio, uploadRejected), `storage` (mem, disk, sdcard, flashPage), `original_storage`, `file_path`, `geolocation`, `conversation_id`, `recording_session_id`, `owner_uid`, `retry_count`, `last_retry_at`, `uploaded_at`, `synced_at` | ✅ |
| Quarantined index | `Documents/wals.json.corrupt-<microseconds>` | original bytes of an index the app judged invalid, **kept, not deleted** | ✅ |
| Audio segments | `Documents/audio_<device>_<codec>_<rate>_<ch>_fs<frame>_<timerStart>.bin` | raw BLE audio frames (opus or pcm) | ✅ name · 🧪 frame format |
| Imported Limitless audio | `audio_limitless_opus_16000_1_fs320_r<rand>_<epochMs>.bin`; migration flag `flutter.limitless_wal_migration_v1` | recordings from a **Limitless** pendant, linked to an Omi account | ✅ |
| Tokens | `flutter_secure_storage` (Android Keystore / iOS Keychain) | auth tokens | ✅ exists · not parsed (credentials) |

Android string-list encoding (Flutter `shared_preferences_android`): a list is stored as the string `VGhpcyBpcyB0aGUgcHJlZml4IGZvciBhIGxpc3Qu` + `!` + JSON array. An older form without `!` holds a base64 Java-serialised list. Doubles carry the prefix `VGhpcyBpcyB0aGUgcHJlZml4IGZvciBEb3VibGUu`.

## Omi device
| Artifact | Status |
|---|---|
| offline audio on SD card / SPI flash, file layout per firmware `sd_card.c`, `spi_flash.c` | 🧪 L4 |
| BLE identity, firmware version | 🧪 |

## Omi cloud
| Artifact | Access |
|---|---|
| Firestore conversations + memories, GCS audio | legal process to Based Hardware; user data export if offered 🧪 |

## Plaud, Bee, Limitless (closed source)
| Question | Plaud | Bee | Limitless |
|---|---|---|---|
| Audio on device | yes, offline (64 GB) | ❓ | ❓ |
| App cache of transcripts/summaries | ❓ L5 | ❓ L6 | ❓ (app discontinued) |
| User export | MP3, WAV, TXT, **SRT**, Markdown, DOCX, PDF, PNG | ❓ | ❓ |
| Cloud region | AWS Frankfurt / Oregon / Singapore / Japan | Amazon | Meta |

The integrity checker ([05](05-ai-summary-integrity.md)) takes Plaud TXT/SRT exports directly, so it works for closed devices without parsing their apps.

## Questions each artifact answers
- **Who recorded:** account uid/email; device name/ID; `owner_uid` per recording.
- **When and how long:** `timer_start` + `seconds`; conversation `started_at`/`finished_at`.
- **Where:** `geolocation` per recording and per conversation.
- **What was said:** transcript segments (machine output, with speaker labels that may be wrong).
- **What the AI claims was said:** `structured` summary, action items, memories, so **check it against the transcript**.
- **Where it went:** cloud sync status (`uploaded_at`, `synced_at`), webhooks.
- **Was it deleted or tampered with:** `deleted`/`discarded` flags, quarantined indexes, WAL entries without a conversation.
