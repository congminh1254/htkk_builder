# Original annex01-2 fixed numeric observations

`gtgt-annex12-numeric-inspect` reuses the source-pinned, genuine fourteen-input
zero/two-location setup and then enters five fixed fake values through the normal
original editor. It never assigns computed, locked or hidden cells or calls
business helpers. The three snapshots are parent1/50:50, parent7/33.33:66.67,
and parent99999999999999/33.33:66.67. There is no XML export or import in this mode.

`annex12NumericSnapshots` is a bounded numeric-only string with three semicolon-
separated observations and twelve comma-separated values in each. Zero-based
coordinates, ordered: T43,U43,X43,T44,U44,X44,AO44,T45,U45,X45,T47,X47.
Values are original `Cell.Value`, converted to decimal and canonicalized with at
most 20 fraction digits. This does not preserve underlying Double bits, display
`Text`, XML type16 formatting or exported money rounding. The source flags for
zero input setup remain historical prerequisites, not statements that the final
nonzero cells/main are zero. No new parity or global compatibility flag is set.

Native results below qualify only the listed fixed read-only observations.
Boundary fixtures remain synthetic examples of report syntax, not native outputs.

## Fractional editor input correction

Run40512654143 recorded the first nonzero case but stopped on the first fractional
UI edit before incrementing action2. This is not a tax comparison failure.
Source `GeneralFunctions.FormatCelltypeFromSinfo`06002702 (bodySHA256
`ca09060781b8037f20f9e96eacbed31ad96df75ae2672ed6a888fa099b9c6849`)
selects `DecimalSeparator=","` and `Separator="."` at0111–0122 for
the source percentage default `0,00`; the default containing a dot takes the
opposite separator branch at00C5–00D6. The probe now checks those original read-only CellType properties
before typing33,33/66,67, while invariant expected decimal values stay33.33/66.67.
No original format property is modified. Bounded format/editor-ready/committed/
value-mismatch stages distinguish input failures from native calculated outputs.
Run40513614061 on 3fe223faed0b60dcc3702a1746722fbc4f483b61 subsequently passed
the whole workflow, attempt1, with all five original edits and all three snapshots.

## Display and original type/Double-bit observations

The same twelve fixed numeric coordinates now have three additional bounded
read-only channels. Each uses `|` between twelve cells and `;` between cases:

- `annex12NumericTextSnapshots`: original `Cell.Text`, unchanged, at most64characters
  per cell drawn only from digits, comma, dot, parentheses, minus and ASCIIspace.
  Blank numeric display is preserved. No arbitrary source text is published.
- `annex12NumericTypeSnapshots`: a static enum (`double`, `decimal`, `single`,
  `integer`, `other`), derived with CLR `is` checks; never arbitrary type names.
- `annex12NumericDoubleBits`: exact sixteen-uppercase-hex IEEE754bits when and
  only when original `Cell.Value is Double`; otherwise the cell token is blank.
  No conversion toDouble is used to manufacture bits for other CLR types.

The original decimal-canonical `annex12NumericSnapshots` is retained for existing
analysis; it can lose Double precision. The new channels distinguish raw value,
underlying binary bits and rounded/localized display. They still do not establish
XML type16 serialization parity, manual tax behavior or global compatibility.
All channels default empty outside this mode and the strict reader checks counts,
grammars and type/bit consistency.

## Native evidence and remaining limits

Run [40514369316](https://github.com/congminh1254/htkk_builder/actions/runs/40514369316)
on `0b43db0a07b295af6fd87e2de13a78284e3effae`, attempt 1, passed the whole workflow
with the added display/type/bit channels. All 36 observed original values were Double.
For parent 1 / 50:50, original child Value 0.5/0.5 displayed Text 1/1 while footer Value/Text
remained 1. This must not be replaced with Math.Round(rawValue) or with a sum of
rounded display rows. For parent 7 / fractional percentages, childText was 2/5.

The observation-only mode never clicked XML export. No XML numeric serialization,
general rounding parity, manual input, multigroup or validation qualification is
implied; all global compatibility/roundtrip gates remain false. Full bounded reports
and SHA/provenance are retained privately by the application repo. The old zero
prerequisite flags describe the baseline before the five nonzero edits.

At this code point, 221 Python tests and 150 actual PowerShell boundary checks passed.
The later documentation-only commit does not change the native harness identity
recorded above. Use an immutable code/run SHA when reproducing these observations.
