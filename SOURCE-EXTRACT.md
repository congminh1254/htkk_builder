# Private HTKK 5.8.1 source extract (W1-D)

`source-extract.yml` is a `workflow_dispatch` job that runs only on this
repository's `main`. It publishes the original HTKK 5.8.1 resources needed for
logic extraction to the fixed PRIVATE branch `htkk-net/htkk_web:htkk-source-5.8.1`.
Nothing from the payload is uploaded as an Actions artifact, cached or printed.

## Inputs

| Input | Values | Meaning |
|---|---|---|
| `scope` | `priority` (default), `full` | `priority`: every pinned resource of the priority forms in `scripts/htkk-source-extract-policy.json`, `InterfaceIni` except `GIA_TINH`, the whole `Project/` directory and every `.dll/.exe/.config` under the install root. `full`: all 4526 MSI files. |
| `transport` | `auto` (default), `direct`, `relay` | Same pinned Fshare archive as `source-candidate-check.py`. `auto` uses the relay only after a retryable direct failure and only when `AGENT_AUTH_TOKEN` exists. |
| `publish` | `true` (default), `false` | `false` runs every verification and builds the commit, but never pushes. |

## Steps and credential boundaries

1. Checkout with `persist-credentials: false`; offline `test_source*.py`, own CAB fixture, MSI query adapter and worker launch-failure tests.
2. `source-extract.py preflight` (only `SOURCE_READ_TOKEN`): target must be the private `htkk-net/htkk_web`.
3. `source-extract.py download` (only optional `AGENT_AUTH_TOKEN`): pinned URL and archive SHA-256 `5d52c065…`.
4. `Test-HtkkSourceCandidateTrust.ps1` (no credentials, unchanged verifier): Authenticode + online revocation for MSI/setup, publisher serial/root pins, MSI/setup/CAB pins (`7c1da251…`, `19394e89…`, `00669905…`), 4526 sizes, 4493 signed-MSI MD5 values and the SHA-256 payload manifest. Worker in a kill-on-close Job, OS-only environment.
5. `Export-HtkkSourcePayload.ps1` (no credentials): starts only after a `baseline-verified` trust result. Bounded Job worker re-checks the archive/MSI/CAB pins, opens the MSI read-only (mode 0) to read `File/Component/Directory/MsiFileHash`, and extracts CAB members through the existing `HtkkSourceCabinet` FDI bridge to numeric names. No installer, `setup.exe`, `msiexec` or custom action runs. Sizes and MD5 are verified again.
6. `source-extract.py stage` (no credentials): both independent extractions must agree byte-for-byte (SHA-256 per MSI file ID). MSI target paths are resolved offline from the tables; every policy pin must appear at the same path with the same SHA-256 and file ID. Unsafe names, path escapes and case collisions fail closed. Writes `payload/`, `manifest.json`, `catalog.json`, `SHA256SUMS`, `msi/layout.json`.
7. `source-extract.py publish` (only `SOURCE_PUBLISH_TOKEN || SOURCE_READ_TOKEN`, Contents write on `htkk_web`): revalidates every hash, checks the target is private, creates one snapshot commit and pushes it to `refs/heads/htkk-source-5.8.1` plus the immutable tag `htkk-source-5.8.1/run-<id>-<attempt>`. A new branch is created without force; an existing one is replaced only with `--force-with-lease` on the exact commit read just before. An identical tree is reported `unchanged` and nothing is pushed. Git receives the token only as an environment-scoped `http.extraheader`, with no system/global config, no credential helper and stdout/stderr discarded.
8. Outcome and cleanup: fixed JSON counts only; local candidate, payload and Git work are deleted after the worker-stop flags are confirmed.

The public log shows status codes and counts, never file names, contents,
headers or URLs. Main, `pages-output` and other branches are never written.

## Policy

`scripts/htkk-source-extract-policy.json` is generated in the private repository by
`scripts/prepare-htkk-source-extract-policy.py` from its pinned menu, scope matrix and
inventory metadata, then copied here verbatim. It lists installer-relative paths,
SHA-256 and MSI file IDs of public installer files only; it contains no private
application source. Regex/prefix selections are filename heuristics.

## Tests

`python3 -m unittest discover -s scripts -p 'test_*.py'` includes
`test_source_extract.py`: policy validation, MSI directory resolution, unsafe
names, collisions, pin mismatch, two-extraction mismatch, dirty export results,
bundle tampering, publish to a local bare repository (create, unchanged, lease
replacement, dry run, public target refusal), the Git environment allowlist,
download transport rules and workflow/exporter text contracts. Windows-only
behaviour (COM MSI reading, FDI extraction, Job cleanup) is only exercised on the
Windows runner.

## Failure diagnostics

`export-result.json` and the single public console line carry only bounded fields:
`code` (`failureCode`, fixed enums `$script:known`/`$script:controllerKnown` or a
worker stage name), `stage` (worker stage), `controller` (controller step),
`error` (innermost .NET exception type from a fixed allowlist, else `other`),
`hresult` (numeric HRESULT) and `workerExit`. The failing step throws
`SOURCE_EXPORT_NOT_VERIFIED:<code>:<stage>` / `SOURCE_TRUST_NOT_VERIFIED:<code>`,
and `source-extract.py outcome` repeats the same enum-shaped fields. Exception
messages, file names and paths are never written. Bootstrap failures (helper
loading, unhandled worker errors) still write a coded result (`HELPER_LOAD`,
`WORKER_UNHANDLED`); a worker that wrote a blocked result is reported by its own
code even when it exits nonzero.
