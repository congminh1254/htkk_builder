# Original 01-2/GTGT fixed input inspection

`gtgt-annex12-input-inspect` is a separate, bounded successor to the unchanged
`gtgt-annex12-row-inspect` scenario. It requires the pinned original workbook and
business instance, the real original annex selection, and one real F5 insertion
producing 67 rows, group ID 1, and two child rows.

The reference host then edits exactly 16 original UI cells: synthetic factory
name and MST `9999999997-001`, and each child's original location type, synthetic
name, Hà Nội / Sơn Tây, original tax-authority selectors, and percentage 50.
Type labels come from the original DC_01 catalogue. Dropdowns use the vendor's
public editor selection API; text and percentages use guarded keyboard input.
Only source-editable cells are touched. Hidden codes, plant tax, formulas,
calculated values and internal business objects are never written.

The result contains only bounded booleans and an action count. Success separately
requires original hidden location codes 01/02, province 101, ward 10129087, tax
head 10100 / local 10129, both percentages 50, original group sum 100, and eight
original monetary cells still zero. All owner, process, foreground, source pin,
modal, shape and row-insertion guards remain active.

This mode does not save or export a declaration. It proves neither a valid
annex XML nor schema / import compatibility. `runtimeRoundTrip` remains false.
Its first Windows execution is still required; Python and PowerShell fixture
checks validate the harness boundary rather than HTKK business behaviour.
