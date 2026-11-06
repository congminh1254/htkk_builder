# Ca ứng viên web→HTKK cho 01/CNKD TT50 (menu U5)

> Cập nhật: ca `01CNKD-TT50-revenue-two-groups-Q3-2026` đã được đăng ký (releaseGate false) với driver chung
> `declaration-web-import-inspect` — xem `DECLARATION-NATIVE-CASES.md`. Ca annex 01-3 vẫn chỉ là thiết kế.

Nhánh `work/forms-hkd`. Đây **không** phải bằng chứng native và không được đăng ký trong
`scripts/htkk-native-cases.json`: release, Pages, cohort và scoped evidence không đổi
(vẫn 13 ca gate D1 + các ca ứng viên đã có). Mọi cờ tương thích vẫn false.

## Hai ca tổng hợp (NNT giả lập 9999999997)

| Ca | Kỳ | Nội dung | Kỳ vọng chính |
|---|---|---|---|
| `01CNKD-TT50-revenue-two-groups-Q3-2026` | Q3/2026, ô (1) | 1 trụ sở (00001, xã 10129087), nhóm 01: 300 tr; nhóm 02: 150 tr, [12] 10 tr | [14] 3.000.000/7.000.000; [17] 1.500.000/3.000.000; [20] 10.000.000/4.500.000; mục D 2 dòng, hạn nộp 30/10/2026; [47] 14.500.000 |
| `01CNKD-TT50-profit-two-locations-annex13-M10-2026` | M10/2026, ô (2) | trụ sở 00001 (nhóm 02 140 tr; nhóm 06 123.456.789, [16] 23.456.789) + chi nhánh 00002 (nhóm 01 100 tr); PL 01-3 bán ra mục I nhóm 02 140 tr | [14] 5.600.000/2.469.136/1.000.000; [17] 2.800.000/1.000.000/500.000; [20] 9.069.136/4.300.000; mục D 3 dòng (TNCN chi nhánh dồn về trụ sở), hạn 20/11/2026; [47] 13.369.136; PL giảm 1.400.000 |

Input là XML do exporter thật của htkk_web sinh ra (`tests/fixtures/htkk-hkd-cases/*.xml`,
SHA-256 ghi trong báo cáo nhánh `work/forms-hkd` của htkk_web). XML không được đưa vào repo
public này. `scripts/htkk_hkd_web_cases.py` tính lại kỳ vọng bằng Decimal, độc lập với engine
TypeScript, và `validate_case_xml` kiểm namespace, định danh (1266/2.9.8/C/0), kỳ, NNT giả lập
và mọi lá tiền. Đã đối chiếu thủ công: cả hai XML web đều qua validator này.

## Driver Windows cần viết (chưa có)

Mode đề xuất `cnkd-web-import-inspect`, tái dùng hồ sơ NNT giả lập và khung CLR2/x86:

1. Đóng hồ sơ NNT như D1; mở menu bằng `RaiseOriginalMenuClick` với ID `U5` (nhóm `101_37`).
2. Hộp kỳ `frmHTKKPeriod`: KieuKy 21 hiện `chkTkhaiThang`, `chkTKQuy`, `chkTKLanPS`. Ca A chọn
   quý 3/2026; ca B chọn tháng 10/2026 và tích phụ lục "PL 142/2024/QH15-174/2024/QH15-204/2025/QH15".
3. Nhập XML web bằng nút gốc `Nhập từ XML` (`FinishImportXML` gốc), rồi để HTKK tự tính lại.
4. Kết xuất bằng nút gốc; XSD .NET đã pin `01_CNKD_HKD_TT50_298.xsd`; `validate_case_xml` trên
   bản xuất lại; so toàn cây với input, ngoại trừ ngày lập và 4 trường định danh dịch vụ.
5. Ghi riêng các điểm web chưa chắc chắn để xác nhận: cách HTKK ghi ô rỗng kiểu TIN/ngày
   (web dùng `xsi:nil`), dòng mặc định của mục A.III/B/C, giá trị `ct41_ma`/`ct43_maDBHC`/
   `ct44_maCQThu`/`ct45_maCQThue` mục D (IL TongHopBangD chỉ ghi U/Z/AH), làm tròn binary64.

Không patch EXE/DLL, không gán Cell.Value, không tự viết XML native.

## Dispatch

Chưa thể dispatch: workflow `probe-htkk-windows.yml` chưa có mode trên. Sau khi driver được
viết và review, PM dispatch thủ công (không phải release):

```
gh workflow run probe-htkk-windows.yml --ref work/forms-hkd \
  -f install_and_probe=true -f synthetic_login=true -f acknowledge_registration=true \
  -f runtime_host=clr2-x86-reference -f gui_automation=cnkd-web-import-inspect \
  -f web_case_id=<ca> -f web_source_sha=<commit htkk_web> -f web_artifact_commit=<commit input>
```

Kiểm offline: `python3 -m unittest discover -s scripts -p 'test_*.py'`.
