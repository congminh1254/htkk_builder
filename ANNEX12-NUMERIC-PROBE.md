# Original annex01-2 numeric observation (not yet native-qualified)

`gtgt-annex12-numeric-inspect` reuses the source-pinned, genuine fourteen-input
zero/two-location setup and then enters five fixed fake values through the normal
original editor. It never assigns computed, locked or hidden cells or calls
business helpers. The three snapshots are parent1/50:50, parent7/33.33:66.67,
and parent99999999999999/33.33:66.67. There is no XML export or import in this mode.

`annex12NumericSnapshots` is a bounded numeric-only string with three semicolon-
separated observations and twelve comma-separated values in each. Zero-based
coordinates, ordered: T43,U43,X43,T44,U44,X44,AO44,T45,U45,X45,T47,X47.
Values are original `Cell.Value`, converted to decimal and canonicalized with at
most20fraction digits. This does not preserve underlying Double bits, display
`Text`, XML type16 formatting or exported money rounding. The source flags for
zero input setup remain historical prerequisites, not statements that the final
nonzero cells/main are zero. No new parity or global compatibility flag is set.

Native execution and full-run success are still required. Boundary fixtures are
synthetic examples of report syntax, not claimed original numeric outputs.
