# Harness HTKK gốc: hợp đồng và ranh giới

Harness là mã kiểm thử riêng chạy CLR 2/x86 trong AppDomain dùng cấu hình
HTKK gốc. Không sửa EXE/DLL/config, không tự viết XML mang danh kết quả gốc,
không gọi business helper để ép tổng, không sửa khóa/visibility/dirty flag.
Các bằng chứng chỉ có giá trị cho phiên bản, SHA, kỳ và ca đã chạy.

## Điểm vào

- `scripts/htkk-native-automation-registry.json`: mode/stage, định tuyến và
  trường kết quả typed, default, giới hạn, phạm vi mode. Không chứa biểu thức
  thực thi hoặc công thức nghiệp vụ tùy ý.
- `scripts/generate-native-automation-registry.py`: kiểm registry và sinh
  wire maps/enums CLR2, reader và compile contract PowerShell. Chạy sau khi
  đổi registry; `--check` phải đạt trước khi push.
- `scripts/HtkkNativeCompileInputs.ps1`: danh sách compiler được sinh và thực
  sự dùng bởi `New-HtkkX86ReferenceHost.ps1`. Mọi mode, kể cả `none`, cần đầy
  đủ partial closure để biên dịch; biên dịch không cho phép tự động hóa.
- `scripts/HtkkNativeUiHarness.cs`: cell editor, quan sát/control ownership,
  đóng profile sạch, tìm common dialog. Tên menu, period, tọa độ, dữ liệu và
  quy tắc nghiệp vụ thuộc adapter; shared harness không tự nhận một ô là
  được phép chỉnh sửa.
- `scripts/HtkkGuiReferenceAutomation.cs`: điều phối UI thread, profile gốc,
  permit, timer và facade; `HtkkGtgt*.cs` giữ hành vi D1 đặc thù.
- `scripts/Get-HtkkSafeGuiReferenceResult.ps1`: strict reader của kết quả.
  Default không được dùng để bổ sung trường thiếu trong output thật.

## Thêm hành vi

1. Đọc issue và source pin hiện hành; phân biệt nguồn tĩnh, fixture và bằng
   chứng native. Không dùng việc kiểm XSD để suy ra đúng công thức/thuế.
2. Thêm mode/stage/field vào registry, policy thành công vào mã được review,
   giữ unknown/default đóng. Stage phải dùng enum, kể cả nhánh ternary.
3. Thêm partial vào compile closure và sinh lại. Cập nhật mọi entrypoint,
   terminal matcher, artifact/context policy qua generator và kiểm đồng bộ.
4. Adapter chọn đúng control nguồn và dữ liệu giả lập cố định; shared harness
   chỉ thực hiện hành động UI và quan sát. Không gọi business method thay UI.
5. Kiểm unit/negative boundary; chạy Windows từ main SHA mới. Không rerun job
   cũ để kiểm mã mới. Cần toàn workflow đạt, không chỉ một flag GUI.
6. Giữ raw XML nguyên byte trong repo private, SHA nguồn/builder/run/attempt,
   source pin và hash. Đối chiếu độc lập cả cấu trúc/giá trị lẫn XSD. Mỗi ca mới
   có context/artifact riêng, không thay thế các ca hồi quy cũ.

## Process và quyền xuất bản

Compiler, oracle, UIA helper và supplier phải nằm trong Job có thời hạn;
cleanup gate chỉ mở sau khi process dừng và Job rỗng. Không nới env allowlist,
không xuất raw stdout/window title/path/XML vào public log. Token đọc/xuất bản
chỉ nạp trong bước tin cậy riêng sau ranh giới an toàn tương ứng. Một lần
helper thành công không được xóa trạng thái cleanup không an toàn trước đó.

## Kiểm thử

```sh
python scripts/generate-native-automation-registry.py --check
python -m unittest discover -s scripts -p 'test_*.py'
```

PowerShell boundary fixtures chạy trên runner không cần dữ liệu HTKK thật;
chúng không thay thế native proof. Bằng chứng đóng TASK-004 phải ghi rõ SHA,
run/attempt, private retention và giới hạn; xem issue #5 trong repo private.
