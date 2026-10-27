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

## Patch UIA đề xuất (chưa áp dụng trong task này)

Thay đúng hai lệnh Add-Type trong generated helper, sau phase assembly-loading:

```powershell
$uiaClient=[Reflection.Assembly]::Load('UIAutomationClient, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35')
$uiaTypes=[Reflection.Assembly]::Load('UIAutomationTypes, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35')
```

Giữ phase, deadline, cleanup và loginReady như cũ. Thêm test độc lập vào workflow
trước probe rồi dispatch main mới; kết quả load độc lập không chứng minh UIA
traversal hoặc đăng nhập đạt. Nếu probe vẫn timeout, phase tiếp theo cung cấp
bằng chứng mới; không coi giả thuyết module autoload là đã chứng minh chỉ vì đã
thay code.
