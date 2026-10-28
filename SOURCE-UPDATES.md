# Source candidate pipeline (TASK-320)

`source-watch.yml` runs weekly or manually on the trusted main branch, without a
private source checkout. It resolves the fixed private main identity before any
candidate process exists. Fetch steps have only the optional relay credential;
Windows verification has an OS-only child environment. Publication credentials
are injected only after the separate seal step confirms worker/job cleanup.

The observer records the official release row/version/date/link and HTML hash.
The downloader accepts fixed HTTPS GDT/Fshare routes, bounded ephemeral Fshare
token redirects, and server-issued session cookies on the initial origin only.
Opaque signed URLs, cookies, response headers and raw exceptions are not logged
or stored. Direct downloads stream to an owned partial file; relay downloads use
HEAD plus bounded Range requests with a stable strong ETag and exact range/size
checks. No TLS/auth failure gets hidden by switching transports; retry limits and
per-resource deadlines are explicit. Download success never means trust.

Only the pinned 5.8.1 official archive can reach data extraction. Its original
MSI, setup and CAB hashes are checked. No mirror is needed: the official archive
contains all three files. The historical mirror helper requires exact source
and mirror pins and cannot authorize a different mirror/version. A mirror is
compared only when actually supplied; no legacy mirror-match flag is invented.

The Windows worker is launched suspended into a kill-on-close Job before resume.
Its entire lifetime is bounded, including descendant tools. Authenticode and
signtool checks require the publisher and timestamp certificates; explicit
online X509 revocation uses no verification exceptions. The signed MSI is opened
read-only, never installed. A System32 cabinet.dll FDI bridge maps member IDs to
numeric owned paths so trailing-dot MSI IDs are not renamed by Win32. It compares
4,526 sizes and 4,493 legacy signed-MSI MD5 values, then records every SHA-256.
The 33 versioned files without MsiFileHash remain explicit authentication gaps.
No candidate EXE, installer or MSI custom action runs. No adapter is activated.

A private proposal includes metadata, version/reference/archive diffs, the trust
report, payload manifest and raw archives in 4 MiB Git blobs. Reassembly metadata
contains each part and whole-file SHA-256. Before authenticated I/O the publisher
validates exact paths, hashes, bounds, source/run/attempt and cleanup gates. It
checks current main again before publishing/status. Only GET-ref 404 permits
creation; 422/auth errors never become create fallbacks. The fixed private branch
is `official-source-proposals`; main and pages-output are never changed.

Every proposal has ready=false and automaticActivation=false, including a
cryptographically verified baseline. Unknown/new-version archives remain inert
and require new policy pins/review before extraction; qualification belongs to
the subsequent source-diff/adapter tasks.

## Operation

- Normal schedule: direct official HTML, optional relay fallback; unchanged
  observations remain metadata-only. Missing connectivity/auth yields an honest
  unreachable/invalid proposal and error status, not 'unchanged'.
- `verify_current=true`: also download and verify the current pinned baseline.
- Optional `observation_commit`: a fixed private prepared cloud observation,
  explicitly identified by immutable commit, source SHA and canonical observer
  source hash, at most 24 hours old. This supports a cloud relay observation when
  the runner has no relay credential; it does not claim fresh runner connectivity.
- Automatic relay requires the owner to configure AGENT_AUTH_TOKEN in builder
  Actions secrets. The cloud token is never copied into GitHub by these scripts.

Tests: Python source-watch/source-candidate/source-update suites; Windows own
CAB fixture and launch-failure tests; real read-only baseline trust workflow.
Reproducible evidence and current limitations are tracked in private issue #321.
