# Supplier chạy trong Windows Job

Primitive độc lập đã qua test Windows thật ở run40579443937, builder ab4309d:
normal exit/argument/environment, orphan grandchild, timeout và lỗi gán trước
resume. Thay đổi hiện tại tích hợp primitive vào supplier launcher; retained
diagnostic identity và wrapper mới còn cần Windows run mới, không dùng run cũ
để tự nhận tích hợp đã đạt.

`HtkkWindowsJobProcess.Launch` giữ native root handle và lấy
`System.Diagnostics.Process` cùng handle trước `ResumeThread`. Creation time từ
hai handle phải khớp; root phải còn suspended/alive trước resume. `RootProcess`
là object mượn, owner Job giữ đến cleanup; không tìm lại process bằng PID sau
khi supplier bắt đầu chạy. `ProcessId` vẫn chỉ dùng làm tọa độ UI diagnostics.

`Start-HtkkCleanProcess` nay trả Job owner, giữ noWindow=false và x86 environment
semantics cũ. Supplier stdout/stderr đi vào NUL hợp lệ, không có task đọc pipe
không giới hạn hoặc log native output. Bố cục/UI/control, source hash, firewall,
synthetic input, native export/import và raw retention không thay đổi.

Trước launch, `supplierLaunchAttempted=true` và cleanup chưa xác minh. Nếu
launch throw trước khi trả owner thì không suy an toàn từ `$process == null`.
`Stop-HtkkSupplierJob` chỉ xác nhận khi Stop(5000) trả bool true, owner xác minh
cleanup, native root exit được chứng minh và job ActiveProcesses bằng 0. Lỗi
query/wait/dispose, type bất thường hoặc thiếu owner sau launch đều chặn
`supplier_stopped`/`credentials_safe`. Root exit riêng không còn đủ. Kết quả
public chỉ có status và bốn bool, không có PID/handle/path/exception text.

`Test-HtkkSupplierJobBoundary.ps1` chạy chính function production lấy từ AST:
13 tình huống cleanup/type/error/no-launch/owner-missing. Trên Windows còn
compile fixture riêng, gọi launcher thật, giữ diagnostic handle qua root exit,
kiểm environment x86/credential sentinel, rồi terminate orphan descendant qua
wrapper thật. Đây không phải chạy HTKK. Workflow vẫn cần chạy supplier HTKK
nguyên bản riêng để kiểm tương thích launch mới.

Phạm vi này chỉ tích hợp supplier và descendants được kernel Job theo dõi.
Ở snapshot bd54b0c, compiler/oracle/helper khác chưa chuyển sang Job. Các đợt sau đã tích hợp oracle801a7e6, UIAfa87e5f và compiler18b6f1b. Windows Installer service vẫn ngoài phạm vi process tree; giữ policy MSI fail-closed và kiểm native/13ca mới trước khi đóng TASK-003.

Cleanup wrapper đợi Stop tối đa5 giây; Dispose có một lượt fallback tối đa5 giây nếu lần dừng trước chưa xác minh, tổng hữu hạn tối đa10 giây. Không mở credentials nếu fallback/query không đạt.
