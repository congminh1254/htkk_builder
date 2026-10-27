# UIA dừng ở assembly-loading trong môi trường WinPS sạch

Báo cáo Windows run40579271429 ghi `uiaHelperPhase=assembly-loading`, trước
RootElement/traversal. Hai nguồn đều tải/hash đạt attempt1, MSI0 và đã dừng.
Không tăng deadline hay retry thêm để che lỗi. Phase hiện tại bao phủ cả hai
lệnh Add-Type, chưa xác định chính xác lệnh/nhánh module nào đang chặn.

`Test-HtkkFrameworkUiaAssemblyLoad.ps1` bổ sung kiểm tra Windows độc lập: cùng
primitive bounded-native-process, cùng WinPS STA, môi trường OS-only, cwd tạm,
CreateNoWindow và deadline15 giây. Child dùng trực tiếp CLR
`Reflection.Assembly.Load` bằng full strong name, không dùng Add-Type/import
module. Kiểm full identity và type `AutomationElement` / `ControlType` thuộc
đúng hai assembly; không truy cập UIA RootElement hoặc HTKK. Child kết quả chỉ
gồm schema/status và sáu booleans. Parent kiểm deadline/exit/cleanup/schema.
Linux chỉ parse/skip rõ ràng, không được ghi là Windows test đạt.

Dùng hai identity framework:

```
UIAutomationClient, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35
UIAutomationTypes, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35
```

Không có bản GAC/reference assembly của Windows trong filesystem cloud hiện tại
để kiểm metadata local; strong name trên là identity .NET Framework4/WPF kỳ vọng.
Bài Windows thật phải xác minh full identity/type và dừng nếu không đúng, không
fallback sang assembly từ thư mục/tải khác.

## Patch UIA đã áp dụng vào generated helper

Đã thay đúng hai lệnh Add-Type trong generated helper, sau phase assembly-loading:

```powershell
$uiaClient=[Reflection.Assembly]::Load('UIAutomationClient, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35')
$uiaTypes=[Reflection.Assembly]::Load('UIAutomationTypes, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35')
```

Giữ phase, deadline, cleanup và loginReady như cũ. Thêm test độc lập vào workflow
trước probe rồi dispatch main mới; kết quả load độc lập không chứng minh UIA
traversal hoặc đăng nhập đạt. Nếu probe vẫn timeout, phase tiếp theo cung cấp
bằng chứng mới; không coi giả thuyết module autoload là đã chứng minh chỉ vì đã
thay code.

Kiểm chứng Windows độc lập: run40580662096, builder eadc33f, toàn workflow đạt. Bằng chứng này xác nhận load/type/STA/cleanup, chưa xác nhận traversal, đăng nhập hoặc roundtrip của helper đã sửa.

## Kiểm thêm cmdlet còn lại của generated UIA helper

Windows run40580662096 tại eadc33f đã đạt bài load assembly/type/STA độc lập.
Đó chưa phải bằng chứng cho các cmdlet còn lại trong helper. Phiên bản test mới
chạy tiếp trong **cùng WinPS child sạch**: `Sort-Object` trên số3,1,2,
`ConvertTo-Json -Depth 4` và `Set-Content -Encoding UTF8` trên fixture hoàn toàn
giả lập cố định. Bổ sung ba flags `sortObjectMatched`,
`jsonSerializationMatched`, `setContentMatched`, giữ sáu flags cũ; parent còn
parse file fixture riêng, kiểm đúng format/ba keys/boolean và ba số1,2,3.
Deadline chung vẫn15 giây. Chưa thêm Import-Module hay đổi probe từ phần việc
này; cần Windows run mới để chứng minh cmdlet hoạt động dưới môi trường sạch.
