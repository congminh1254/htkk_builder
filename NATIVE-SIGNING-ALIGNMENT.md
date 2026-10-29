# Native signing alignment — TASK-005 / source issue381

Original D1 maps K_66 (zero-based65/10) to signing date, control14. The pinned XLS
uses text format `@`, unlocked, merged K66:O66. That template format alone does
not describe the runtime editor: original fpSpBindDataCell maps control14 to
InsertDateCell, which creates MaskCellType with mask `00/00/0000` and prompt `.`.
Canary40916290675 rejected the earlier General/text/date guard before editing.
Runtime success for the corrected mask still needs a fresh main-only pilot.

The revised helper requires this exact source-backed mask on the original pinned
D1 sheet and enters eight digits (`25102026`) through its editor. It refuses locked
cells. It scrolls the active original cell into view via vendor ShowActiveCell,
starts the original editor, types the fixed synthetic date through keyboard input
and commits via the vendor lifecycle. No Cell.Value/CellType/Locked or model setter
is used. The final date edit occurs after the case's original money/checkbox flow,
before original export. Failed editor attempts are not silently retried.

Four bounded typed fields report edited/ready/locked and cell kind(0unknown,
1General-text,2text,3date,4source-date-mask). Live staging-v3 requires ready/edited, unlocked,
exact kind4 and full original initial/reexport equality. It compares all four native
service fields including provider checksum exactly. Retention remains private and
byte-exact, with schema/qualification assertions kept separate. Historical v1/v2
reading remains explicit; it cannot satisfy the strict live aligned policy.

Source checksum evidence is held in the private application's pinned contract:
WinDoWorkExportXML generates the provider value from the whole declaration after
removing TTinDVu. GenerateKey uses the original deterministic encryption/string
serialization/hash pipeline. A signing-date difference therefore changes that
checksum; no checksum/date normalization is permitted. The private independent
checker has matched26historical raw native outputs. This is not a new signature
scheme or a substitute for authenticated runner provenance.

Local regression tests are not native proof. Run a main Windows pilot and then
all13fixed cases, inspect whole workflows and raw immutable outputs, independently
validate39XSD documents and full comparisons, and keep the parent TASK open if
mandatory branch coverage or independent review is missing. Archived failed
experiments40781676341/40782248741 remain failed evidence, not successful runs.

Canary40914285102 stopped before supplier launch at the safe-result fixture:
its handwritten baseline did not include the four new typed fields. The baseline
now initializes from generated defaults and then applies the explicit positive
fixture overrides; the production reader still rejects every missing runtime key.
Date diagnostics are active only for web-import mode. Portable PowerShell now runs
the actual safe-reader and tax-comparison fixtures from Python CI, including a
well-formed-but-wrong provider checksum negative case. All376local tests execute
with PowerShell available, without skips. This preflight fix is not native proof;
the next canary uses a new main SHA rather than rerunning the old implementation.
