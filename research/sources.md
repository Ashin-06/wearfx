# Sources (accessed 10 Oct 2026)

## Primary source code
| Repo | Commit | Files |
|---|---|---|
| [BasedHardware/omi](https://github.com/BasedHardware/omi) | `14fab5f` (2026-10-10) | `app/pubspec.yaml`, `app/lib/backend/preferences.dart`, `app/lib/services/wals/wal.dart`, `app/lib/services/wals/local_wal_sync.dart`, `app/lib/utils/wal_file_manager.dart`, `app/lib/backend/schema/conversation.dart`, `app/lib/backend/schema/transcript_segment.dart`, `app/android/app/build.gradle`, `app/ios/Runner.xcodeproj/project.pbxproj`, firmware file list |
| [flutter/packages](https://github.com/flutter/packages) | main | `shared_preferences_android/.../SharedPreferencesPlugin.kt`, `LegacySharedPreferencesPlugin.kt` (list/double prefixes, file name) |

## Documentation
- Omi backend deep dive: https://docs.omi.me/doc/developer/backend/backend_deepdive.md
- Omi storing conversations: https://docs.omi.me/doc/developer/backend/StoringConversations.md
- Plaud trust center: https://www.plaud.ai/pages/trust-center
- Plaud privacy policy: https://www.plaud.ai/pages/privacy-policy
- Plaud AI trust index (independent): https://verifywise.ai/ai-trust-index/plaud

## Prior and related work
- Ray-Ban Meta glasses, DFRWS USA 2026: https://www.sciencedirect.com/science/article/pii/S2666281726000855
- *Ex Machina*, AI companion apps, DFRWS EU 2026: https://www.sciencedirect.com/science/article/pii/S2666281726000077
- Smart wearables hidden artifacts, J. Forensic Sci. 2026: https://onlinelibrary.wiley.com/doi/10.1111/1556-4029.70301
- TomTom Spark 3: https://www.sciencedirect.com/science/article/pii/S2665910721000293
- Deposition summarisation hallucination: https://arxiv.org/html/2601.15182v1
- AI summary QA / Camarillo coverage: https://hackernoon.com/your-ai-meeting-summary-is-probably-missing-something
- LLM-as-judge for meeting summaries: https://www.testdevlab.com/blog/evaluating-ai-meeting-summaries-llm-as-a-judge

## Device reviews (context only)
- Bee review: https://www.layer3labs.io/gear/reviews/bee-ai-pendant
- Limitless review: https://www.layer3labs.io/gear/reviews/limitless-pendant
- Pendant roundup: https://www.layer3labs.io/guides/best-ai-wearable-pendants-2026
- NextPit Plaud review: https://nextpit.com/plaud-notepin-review

## Upstream re-check
- 10 Oct 2026, through `BasedHardware/omi@7d4da97`: the only change to the storage files since `14fab5f` adds a UI flag `speakerLabelingTipShown` (a one-time tip). No change to conversation, memory, WAL or account formats.
