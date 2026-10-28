# Align original GUI signing input with the fixed synthetic web case

This is reference-runner calibration for issue381/evidence6, not another hand-authored web form. Source-generated engines need a reference oracle using equivalent inputs.

Pinned source binding: `InterfaceTemplates/xml/01_GTGT_TT80_283.xml` SHA25640f5d6f711f7acb69dcc4098e3e3bb0b1849224d1c185902a50b8cae6fc50aae maps `K_66`, Controltype14, to `TKhaiThue/ngayKy`. The pinned XLS8ad9ec9f0f3462da75ce4e873e4bb60003947e9edd5d738a5055e37d6c73b310 labels J66 “Ngày ký:” and merges K66:O66; source zero-based cell is65/10. Original `WinSpreadProcess.DefaultCellFomat`, token0x060001b9/bodySHA2631ff4f900dc0350d01b6ca00c82a9a83fc97da8c867d57aacc19bc68ff32ed, supports date/text editor formatting; DateTimeCellType uses `dd/MM/yyyy`.

Only `gtgt-web-import-inspect` edits this source cell before the first export. The helper opens its original public cell editor, uses foreground-owned keyboard input and commits through original editing APIs. It observes the committed cell as2026-10-25 and rechecks before proceeding. It never assigns Cell.Value or business/model fields, patches sources, authors XML or edits totals. Existing case money input counters remain unchanged.

All four native service leaves, including provider checksum, must match initial/reexport. The existing GUI exact XML comparison must succeed before staging. Live staging-v3 explicitly binds the fixed-web-synthetic-date policy, attempt and both original hashes. Publisher v3 independently checks exact signing dates, every initial/reexport leaf and attribute before authenticated I/O. Legacy v1/v2 reading remains separate; a current live run cannot downgrade its date policy. Both raw files remain private and byte-exact; no signing date or service normalization is applied.

This does not enable filing/fullcompatibility, replace independent XSD verification/review, or authenticate a run from booleans alone. Windows runs, immutable artifacts and independent checks must be attached to issue381 separately. The prior0/13 mismatching v2 records remain valid historical observations and are not rewritten.
