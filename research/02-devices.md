# 02 · Devices and Ecosystems

| Device | Vendor / status (Oct 2026) | Capture model | Where processing happens | Source available? |
|---|---|---|---|---|
| **Omi** (pendant, devkits) | Based Hardware | always-on while worn | phone streams audio to Omi backend (`/v4/listen` WebSocket, Deepgram STT); offline audio buffered as "WALs" on device and phone, uploaded later | **yes** (`BasedHardware/omi`, app + firmware + backend) |
| **Plaud NotePin / Note** | Plaud (Nicebuild LLC) | button-press recording | audio recorded to device (64 GB listed) offline; transcription and summaries need upload to Plaud cloud; "PCS off" mode keeps recordings on device | no |
| **Bee** (wristband / clip) | Amazon (acquisition reported 2025) | always-listening | phone app + cloud: daily summaries, to-dos, searchable memory | no |
| **Limitless Pendant** | Limitless, acquired by Meta; no longer sold | always-on, "Consent Mode" chime | phone/desktop/web app + cloud | no; **Omi imports legacy Limitless recordings** |

## Omi architecture (verified from source, `BasedHardware/omi@14fab5f`, 10 Oct 2026)

```
[Omi device] --BLE audio (opus/pcm)--> [Omi app, Flutter] --WebSocket /v4/listen--> [Omi backend]
     |  offline: SD card / SPI flash                |  offline: WAL files in Documents/          |
     |  ("sdcard", "flashPage" storage)              |  + wals.json index                          +--> Firestore (conversations, memories)
     |                                               |  SharedPreferences cache                    +--> Pinecone (embeddings)
                                                     |  (account, devices, cached conversations)   +--> GCS (audio files)
```

- App IDs: Android `com.friend.ios` (prod), `com.friend.ios.dev` (dev). iOS bundle is set from a build variable; the development ID is `com.friend-app-with-wearable.ios12.development` (prod ID to confirm on a device).
- Storage packages: `shared_preferences` (classic API), `flutter_secure_storage` (tokens), `path_provider` (files). **No SQL database.**
- Firmware storage (offline audio): `omi/firmware/omi/src/sd_card.c`, `spi_flash.c`; devkit `sdcard.c`, `storage.c`. Device-side offline audio is in [03](03-evidence-map.md) as a lab task.

## What "always-on" means for evidence

- A conversation exists in up to **four** places: device buffer (if offline), phone WAL file, phone cache (`cachedConversations`), cloud (Firestore + GCS).
- Each place holds a different **form**: raw audio, transcript segments with speaker labels and timings, generated `structured` summary (title, overview, action items, events).
- Phone deletion does not reach the cloud, and cloud deletion does not reach a phone that is offline. Both orders need testing ([07](07-experiment-plan.md)).
