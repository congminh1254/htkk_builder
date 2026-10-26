# Fixed original annex export foundation

The candidate contract is now used by the separate original-export probe in
ANNEX12-EXPORT-PROBE.md. The 14-input scenario passed native Windows run
40420603838; first export execution is still pending. The thirteen web/native
cases and their publishers remain unchanged.

`htkk_annex12_fixed_export.validate_candidate` accepts only the source-predicted
synthetic C0/M10/2026 case `01GTGT-annex12-zero-two-locations-M10-2026`:

- one 01-2/GTGT annex and one factory (`ID_1`), synthetic parent name and MST;
- exactly two children (`ID_44`, `ID_45`), STT 1.1/1.2 and types 01/02;
- source-locked child name/MST fields blank, exact Hà Nội/Sơn Tây and CQT codes;
- each percentage 50, original group percentage 100, every annex amount zero;
- original fake base profile, industry 00/1701, current native dates, 27 zeros.

The pinned output template has six factory leaves, fifteen leaves per child,
and two footer leaves. Thus this case adds 38 leaves to the known 74 base
leaves: 112 total, 108 tax leaves after the four service-identity leaves.
IDs are source predictions, not runtime evidence. Any actual native difference
must stop retention until explained and represented as a separately reviewed
fixed contract; the validator must never accept arbitrary row IDs or strings.

The base no-annex validator remains unchanged. A private in-memory deep copy is
projected to an empty PLuc solely for its existing privacy validation. The raw
body is never rewritten, returned as replacement XML, staged or published by
this module. All annex nodes, order, attributes, values, IDs and 38 leaves are
checked separately first. UTF-8, namespaces, declaration, size, depth and node
count are bounded. Parser tests are synthetic and cannot establish native or
XSD compatibility. All returned proof/compatibility flags remain false.

## Export implementation boundaries

1. Add a separate fixed `gtgt-annex12-export-inspect` mode rather than extending
   the thirteen web input cases. Preserve the input-only and row-only modes.
2. Require all input observations, pins, one source F5 and two source children.
   Re-observe the pinned main sheet (index 0, 72×24, identity and signer), all
   27 zero monetary cells and unchecked ct21 after the annex inputs.
   Call the existing read-only `InspectCaseMoney(main)` explicitly: the current
   annex branch returns before this function and the common exporter requires
   `gtgtCaseMoneyMatched`. Never assign that flag as a shortcut.
3. Reuse the original Kết xuất command, original selector and original common
   file-dialog keyboard mechanism. `exportStarted` already prevents the outer
   observer from re-entering edits while the native export watcher runs. Use a
   dedicated fresh directory/file, owner/PID/modal guards, pinned XSD path and
   ComputeHash DLL. Require actual original 0280 success and unchanged bytes.
   Export alone does not prove import/reexport or web parity.
4. Run actual independent XSD validation before retention, using only the pinned
   local schema (no external resolution). Keep
   `originalExporterValidatedSchema` distinct from independent XSD verification.
   In the app's later immutable fixture tests, repeat with the actual WASM XSD
   validator used by browser exports, against the raw original file.
5. Only after supplier shutdown and source re-hash may staging copy the exact
   original bytes into a dedicated RUNNER_TEMP directory. Check the original
   and staged size/hash, every parent path against reparse points, an empty new
   destination, and exact two-file scope. Staging provenance binds builder SHA,
   run/attempt, fixed case, pinned inputs/source, zero/two-row observations,
   original export success, independent schema result, byte count and SHA-256.
6. Add a separate annex publisher with a new fixed private orphan branch and
   exact native staging contract. It must re-run `validate_candidate` and the
   byte/provenance checks before any API write, verify the destination repo is
   private, and load credentials only in the post-supplier step guarded by both
   `supplier_stopped` and `credentials_safe`. No raw XML in public Actions logs,
   artifacts, screenshots or summaries. Reuse bounded error codes only.
7. Preserve raw XML and manifest unchanged in private immutable evidence, then
   pin them in app fixtures with provenance. Compare real IDs/omission and all
   108 tax leaves before implementing a web serializer or import/reexport test.

The existing `publish-htkk-web-native-output.py` explicitly requires one of the
thirteen case IDs, 74 leaves and 70 compared tax leaves; those checks must remain
unchanged. The legacy zero-export publisher also deliberately rejects a
nonempty PLuc. Neither publisher is an annex retention path.
