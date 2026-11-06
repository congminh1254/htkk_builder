# Bounded recovery before tax execution

The immutable native cohort still requires all case workflows, raw publications,
source/input/request bindings and stopped supplier processes. Statuses only discover
proof; a retry never grants success or qualification.

`native_preflight_retry.py` permits exactly one failed-job rerun (attempt 1 → 2)
for three narrow cases on the exact trusted main builder/workflow:

- Framework UIA readiness timed out after phase `complete`, process stopped, and
  the supplier probe step was skipped. The source test loads fixed assembly identities
  and fixed public cmdlet data; it never starts HTKK.
- The original supplier is still starting, synthetic login is hidden but the next
  profile window has not been identified, GUI declaration automation has not started,
  and no tax data/roundtrip ran. A mandatory explicit permit boundary attests a
  unique initially-absent path, no authorization attempt and continued absence after
  supplier/helper shutdown, checked before owned-file deletion. Missing attestation
  disables startup retry; a null collected GUI result alone never proves no progress.
  The helper cannot mutate/save the profile or navigate to tax without this permit.
  Source/signature/isolation and complete supplier/helper
  shutdown must be attested. Only the registered web-import driver is eligible.

- The issued GUI permit let the helper save only the synthetic profile header: original
  Save returned success 0002, all 8 saved-header checks matched with mask 0, and the
  single original `Đóng` request was made, but the retained `frmWinToKhai` owner was
  still visible when the fixed 60-second `gtgt-web-import-inspect` budget expired
  (GUI status `timed-out`, stage `waiting-profile-close`, failure category `none`).
  The permit attestation must show a unique initially-absent path, an attempted
  authorization and the permit still present when checked before owned-file deletion.
  Every other GUI field (main menu, D1 click, period, sheet, web input, case edits,
  money counts/masks, export, import, re-export, comparison) must still hold its
  unprogressed default; any unknown progressed field, terminal or later stage,
  `failed`/`root-exited` status, header mismatch, or a retention result other than the
  single `FILES` rejection refuses retry. Supplier/helper shutdown and source/signature/
  isolation attestations are the same as for the startup case.

Observed: run42148832165 (run 1069, case `01GTGT-sale5-half-M10-2026`, release
42148147981) stopped at `waiting-profile-close` after 60s; the other 12 cases of that
cohort passed, and inspected passing web-import runs (1035–1039) finished GUI
automation in 20–36s. The root cause of the unobserved close is not yet known; the retry
does not change any wait, close action or comparison, and the case must still pass in
full on attempt 2.

Unknown errors, a GUI/tax comparison report, changed sources, missing cleanup,
failed callbacks, or a failed second attempt are rejected. The 20-minute batch
ceiling remains. The action token and existing source-status secret are read only
from workflow environment variables; no credential or raw API response is logged.

The controller posts `pending` only after GitHub accepts the rerun. It remembers
submitted run IDs to avoid duplicate reruns during API propagation. An Actions or
status API error aborts the release. The next successful status must still undergo
whole-workflow/attempt/raw-retention reauthentication; failed evidence cannot publish.

Observed examples (both public, before tax): run41349444880 attempt1 hit the old
15-second Framework process-exit budget; attempt2 passed. Run41350681273 attempt1
could not recognize the synthetic post-login profile; attempt2 passed unchanged.
Their parent releases remained failed and were not represented as deployed.
The separate Framework preflight now retains a hard30-second limit plus all exit,
identity, type and result checks; runs41349972027/41349972032 passed on Windows.

Offline tests exercise known/unknown classifications, wrong workflow/builder/input,
cleanup/type/callback failures, attempt2 refusal, eventual consistency, status-post
failure and the unchanged final cohort gate. Fabricated API fixtures do not qualify
an original Windows execution.


Discovery first scans all statuses (including failures behind pending cases), then
waits for every workflow to finish before downloading any logs or artifacts. This
avoids repeatedly fetching already-completed proofs on every 15-second poll when a
later case is still queued, retrying or cleaning up. A failure callback posted before
workflow cleanup finishes waits for terminal job evidence without queuing another
rerun. All full proof checks and final pinned revalidation remain unchanged; no
status or metadata-only result grants qualification.
