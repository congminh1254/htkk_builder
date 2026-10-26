# HTKK public builder

This repository contains only builder workflows, trusted orchestration scripts, and documentation. The application source remains private in `congminh1254/htkk_web`. Never copy its Git history, source tree, fixtures, credentials, diagnostic logs, screenshots, traces, test reports, or dependency caches into this public repository or its artifacts.

The only trigger is `workflow_dispatch` on this repository's `main`. Inputs: full lowercase `commit_sha`, `mode` (`ci` or `release`), optional positive `pr_number`. Release accepts only current source `main`; CI additionally accepts the current head of an open, nonfork PR targeting source `main`. The trusted private dispatcher must use this exact contract. Anyone who can write the private source/main or its internal PRs is trusted to run code on an ephemeral builder runner; do not grant that access to untrusted contributors. Fork builds are rejected.

Build diagnostics stay in runner-local temporary files, are never uploaded, and are removed at job end. Public console messages contain fixed outcome text only. No Actions caches or artifacts are enabled. Secret-bearing checkout, build, publication, and status reporting are separate steps; build subprocesses receive a small environment allowlist. The status callback runs in a separate clean job with only its own token. Dependency/build commands may access the network; private source execution is trusted, not a sandbox against malicious repository maintainers.

Releases copy only static web `out/` (no portable distribution; `downloads/` is rejected) into `site/` on the private generated branch `pages-output`, using a new Git root without source history. `.git`, symlinks and source maps are rejected from static output. Root `.htkk-build.json` records source SHA, build time and builder run provenance. Publication rechecks current main, pushes only `pages-output`, then sends private `repository_dispatch` `htkk-pages-ready` with `pages_commit` and `source_sha`. The private Pages workflow must check out that exact commit, verify provenance/current-main SHA, then deploy `site/`. The generated branch is deliberately replaced for each release; source `main` is never pushed by this builder. All release builds are serialized. Failed dispatch leaves an output branch but does not deploy it; retry only with revalidated current main.

## Configure dedicated credentials

Do not reuse a general personal/session token. Fine-grained tokens must have only the selected repository and permissions listed below; metadata read is implicit. Do not place these credentials in source files or command arguments.

| Location | Secret | Selected repository | Permission |
|---|---|---|---|
| Private source | `BUILDER_DISPATCH_TOKEN` | Public builder only | Actions: write |
| Public builder | `SOURCE_READ_TOKEN` | Private `htkk_web` only | Contents: read, Pull requests: read |
| Public builder | `SOURCE_PUBLISH_TOKEN` | Private `htkk_web` only | Contents: write |
| Public builder | `SOURCE_STATUS_TOKEN` | Private `htkk_web` only | Commit statuses: write |

Store publication credentials in a protected `release` environment restricted to public-builder `main` if requiring release approval is desired; if used, split the release job or add that environment without giving PR CI access to publication secrets. Current workflow uses separate final-step injection and publishes only validated main releases. The initial environment credential could read repositories but returned HTTP403 for Actions secret administration; repository admin visibility alone does not grant secret-management API permission. The user must create these dedicated credentials/secrets in GitHub settings if that restriction persists.

Release builds fetch the pinned Windows runtime into a runner-temporary cache and reverify it during packaging. The downloaded runtime is never executed by this Linux builder. Windows HTKK execution/round-trip validation is not performed by this Linux builder.

## Offline verification

Run `python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 -m py_compile scripts/*.py`. These authorization tests mock API responses; they do not certify Windows HTKK compatibility. Before first dispatch, review the public Git tree to ensure it contains only this builder template, configure the private dispatch/deploy workflows, and configure all four dedicated secrets.

Có thể dùng duy nhất SOURCE_READ_TOKEN cho cả checkout/publish/status theo cấu hình chủ repo: token cần Contents read/write + Commit statuses write chỉ trên htkk_web. Workflow ưu tiên token riêng nếu có, nếu không dùng SOURCE_READ_TOKEN; build subprocess vẫn không nhận token.

Portable downloads have been retired. Release builds remove stale `out/downloads/`, do not fetch or package Node runtimes, and no Windows portable workflow is dispatched. The original HTKK Windows reference probe remains available for compatibility investigation.


Release regression prepares eleven fixed synthetic 01/GTGT cases for the first monthly October2026 declaration, normal activity and no annexes: zero, a 1000000 sale at10%, the positive half-rounding boundary5→1, a 1000000 sale with the original suggested tax manually overridden to7, two5% cases (10→1 and1000000 with tax manually overridden to7), two [21] confirmation cases (from zero and after resetting a1000000 sale), and three remaining [21] branches (No after a1000000 sale, Yes then uncheck, and Yes with credit7). The private application's actual exporter produces each input after CI. Trusted scripts validate the entire fixed privacy/amount allowlist, preserve inputs in eleven private branches and dispatch Windows with immutable artifact commits. Each case uses its own `htkk-native/*` status; financial success is separate from full HTKK compatibility. The Windows harness uses original numeric editors and the original [21] checkbox/confirmation where selected, invokes original export/import controls, compares all70 tax leaves under the documented creation-date/service-identity rules, and preserves unchanged native output XML in a private per-case branch. No XML or private source is uploaded as a public Actions artifact. See [WINDOWS-PROBE.md](WINDOWS-PROBE.md) for exact case scope, source pins and the observed [42] lock timing.

All six native Windows cases passed for source `6866f6f` and builder `1204ea8`. The two 5% cases passed runs [40296479937](https://github.com/congminh1254/htkk_builder/actions/runs/40296479937) (half) and [40296484433](https://github.com/congminh1254/htkk_builder/actions/runs/40296484433) (manual): all 27 monetary checks, the 70-leaf tax comparison, original import/reexport, private raw XML retention and callbacks succeeded. Release and Pages deployment also succeeded. This verifies these six fixed cases; full HTKK compatibility remains unverified.

The two `[21]` cases passed original Windows runs [40299540748](https://github.com/congminh1254/htkk_builder/actions/runs/40299540748) (`noactivity-zero`) and [40299544848](https://github.com/congminh1254/htkk_builder/actions/runs/40299544848) (`noactivity-reset-sale10`), source `a500fe7` and builder `ec03035`. Both verified the original I36 checkbox, exact owned Yes/No confirmation with Yes, 12 locked source cells before export and after import, all27 monetary values and70 XML tax leaves, and unchanged private raw XML retention. No/cancel, unchecking, retained credit and other declarations remain outside these two cases. Final source `5b374e0` passed all eight native workflows with builder `804ec58`; release [40300560433](https://github.com/congminh1254/htkk_builder/actions/runs/40300560433) and Pages40300942468 succeeded. The eight-case privacy/contracts have149 offline Python tests; these do not replace the separately retained native evidence or establish full compatibility.

The three newly configured `[21]` cases are pending original Windows verification. Their parser/transport contracts and exact synthetic vectors pass offline tests, but they do not yet add native compatibility evidence.
