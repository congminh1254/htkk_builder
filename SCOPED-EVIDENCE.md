# Scoped evidence assessment

`evidence.yml` runs on builder main after verified Pages deployment or by manual
dispatch with exact native producer source and builder SHAs. It collects only the
thirteen existing fixed synthetic native cases. Historical auditing is supported:
assessment code is pinned separately to the current private source main.

The trusted public collector authenticates run/attempt, complete jobs/steps, GUI
and cleanup/oracle reports, publication commit, original raw hashes, producer and
input lineage. It rechecks the existing fixed synthetic privacy allowlist before
writing a local private bundle. It never executes supplier binaries or private
producer code. API errors and raw response bodies are not printed; signed log
storage redirects do not receive the GitHub Authorization header.

The private main assessor runs without credential variables, with diagnostics
captured locally. Its process group is stopped before the publication step loads
credentials. The publisher verifies the destination is the fixed private source
repository and retains only 133 allowlisted files on
`gtgt-scoped-evidence-candidates`. No public artifact upload is used. A parentless
Git commit provides an immutable audit snapshot; the branch may later advance.

An assessment workflow can succeed while qualification remains **BLOCKED**. The
stored candidate has no reviewer and never grants native/filing qualification.
Independent review and all required case branches remain mandatory at the source
repository's official gate. Current known native initial/reexport signing/service
identity differences are retained honestly, not normalized away.

Secrets use the existing SOURCE_READ_TOKEN and optional SOURCE_PUBLISH_TOKEN
fallback; GitHub's job token needs actions:read for authenticated public run logs.
Do not move credentials into source files, input fields, logs or public artifacts.
The workflow removes source and private diagnostics in its final always step.

Checks: `python -m unittest discover -s scripts -p 'test_*.py'`. The new suite tests
wrong run/attempt/workflow, raw Git blob integrity, cleanup/oracles, preservation
of existing local work, partial failure cleanup, request resolution, private-only
publication and the separation of credentials from assessor execution. Mocked
records are contract tests, not production evidence.
