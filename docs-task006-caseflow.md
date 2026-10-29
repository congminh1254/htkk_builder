# Trusted caseflow (TASK-006)

Private tracker: https://github.com/htkk-net/htkk_web/issues/7.

`htkk-native-cases.json` is the reviewed registry for adapter plugins and synthetic cases. Current native plugin is D1/01GTGT 2.8.3, HTKK 5.8.1, 13 cases. Unknown native adapters are blocked, never converted into zero-valued passing cases. Application case plans may supply descriptors, never executable commands or unreviewed privacy validators. Expected monetary oracle values remain independent of the producer.

Run `python scripts/generate-native-cases.py --check` and `python -m unittest discover -s scripts -p 'test_*.py'`. Generated PowerShell formats/workflow case options must match the trusted registry. The batch launcher strips all source/Actions/relay credentials and Node options before private product code executes; XSD/producer diagnostics stay private.

After supplier cleanup, input/output publication preserves raw bytes privately. Request-scoped input context pins source/unit/profile/producer/XML/plan. Append-only private tags retain every immutable input/output, even when convenience branches move. Only GET 404 permits creation, never auth/422 fallback. Existing tag targets must match exactly.

Release waits for the exact immutable input cohort, verifies complete successful native runs including poststeps/cleanup, and pins all 13 proofs in private `.htkk-build.json`. Pages reauthenticates these pinned run/attempt/input/native commits; mutable statuses only discover runs. Current-main guards, stale callback suppression and release/case concurrency protect superseded work. GitHub statuses have no atomic compare-and-swap; qualification relies on the immutable cohort, not status write ordering.

Old private source without a case plan remains supported by the trusted fixed-case launcher. New source plans are checked against the immutable source blob before refs are written. No app source, taxpayer data, XML or credentials may enter this public repository/log/artifact. No qualification/filing flag is enabled by this infrastructure. Retrospective tests and synthetic API fixtures are not fresh Windows evidence.
