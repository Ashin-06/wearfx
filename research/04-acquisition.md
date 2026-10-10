# 04 · Acquisition (draft SOPs, lab validation pending)

## Order of volatility
1. **Live sync**: a powered phone near the pendant uploads WALs and refreshes the cache; cloud edits can overwrite the cached summary. Put the phone in airplane mode (Bluetooth **off**) on seizure.
2. Device offline buffer: drained once the app reconnects and syncs. Keep the pendant away from the phone (separate Faraday bags).
3. Phone app files: stable while isolated.
4. Cloud: stable but changeable by the account holder; send a preservation request early.

## Phone
| OS | Method | Gets |
|---|---|---|
| Android | full file system extraction (commercial tool, or rooted lab phone: `adb shell su -c 'tar -C /data/data -cf - com.friend.ios' > omi.tar`) | `shared_prefs/`, `app_flutter/` (Flutter's documents dir: `wals.json`, audio) |
| iOS | full file system extraction; encrypted backup (🧪 L3: does it include `Documents/` and the prefs plist?) | `Library/Preferences/*.plist`, `Documents/` |

Hash everything (SHA-256), keep the original archive, work on copies.
Flutter's `getApplicationDocumentsDirectory()` is `app_flutter/` under the app data dir on Android and `Documents/` on iOS.

## Device
- Omi: 🧪 L4. Read the SD card (devkit) with a write-blocker, or read SPI flash per firmware layout. Pair only with a lab phone and a lab account.
- Plaud: 🧪 L5. The device mounts as USB storage on some models (verify); image it read-only.

## Cloud
- User export from the app, if available, by the account holder (consent cases).
- Legal process to the vendor otherwise.

## What not to do
- Do not open the app on the seized phone: it syncs, re-summarises and may purge synced WALs.
- Do not pair the seized pendant to a new phone without imaging first: pairing triggers offline-buffer upload.
