# Primitive Windows Job

`scripts/HtkkWindowsJobProcess.cs` là boundary riêng của runner. Primitive độc
lập đã qua Windows run40579443937 ở ab4309d; compile trên Linux không thay bằng
chứng Win32. Supplier launcher đang được tích hợp ở thay đổi tiếp theo, xem
`SUPPLIER-JOB-INTEGRATION.md`; compiler/oracle chưa đổi. Không sửa EXE/DLL/config
gốc, không suy test primitive là đã kiểm toàn bộ luồng supplier HTKK.

API `Launch(executable, workingDirectory, arguments, noWindow, x86)` xóa môi
trường kế thừa và chỉ truyền danh sách biến hệ điều hành đang dùng trong runner.
Chỉ kế thừa handle NUL qua STARTUPINFOEX handle-list riêng; không kế thừa handle
môi trường khác. Std input/output/error dùng NUL hợp lệ để Console.WriteLine
không lỗi và output không ra log. Đường dẫn/argument
không xuất vào lỗi; category cố định. Vì không capture stdout/stderr, caller
phải đọc output có cấu trúc từ file riêng như các oracle hiện hành; không thay
thế helper đang cần đọc pipe một cách máy móc.

API tùy chọn `LaunchWithOutputFiles` có hai file diagnostics private riêng và
handle allowlist giới hạn; xem `JOB-PRIVATE-OUTPUT.md`. Không đổi semantics NUL
của `Launch` mặc định và không tự parse hoặc công khai raw compiler output.

Boundary tạo Job không breakaway với `KILL_ON_JOB_CLOSE`, tạo process bằng
`CREATE_SUSPENDED`, gán vào Job rồi mới `ResumeThread`. Gán thất bại thì process
vẫn chưa thực thi, bị terminate và chờ xác minh. Không dùng kiểu Start-Process
rồi mới gán Job vì có race trước lúc gán. Nested Job trên runner Windows phải
được hỗ trợ; lỗi gán không được fallback sang launch ngoài Job.

`WaitForRootExit(ms)` và `RootExitCode` chỉ nói về root, không phải cả tree.
Chúng dùng native process handle giữ từ `CreateProcess`, không tìm lại bằng PID.
`RootProcess` là System.Diagnostics.Process mượn từ owner: handle được giữ và
creation time đối chiếu với native identity trước resume. Caller không Dispose
object mượn này trước owner; Stop/Dispose owner quản lý vòng đời.
`ProcessId` chỉ là tọa độ cho UI diagnostics, không là identity/exit proof. Khi
tích hợp không dùng `Process.GetProcessById` sau resume làm nguồn identity duy
nhất: root có thể thoát nhanh và PID được dùng lại. API identity cần giữ native
handle hoặc xác minh creation time với handle gốc trước khi thao tác process.
`ActiveProcesses` dùng accounting của kernel nên vẫn giữ descendants khi parent
đã thoát/reparent. `Stop(ms)` terminate toàn Job rồi đợi root đã dừng và
`ActiveProcesses == 0`, deadline tối đa 300 giây. Chỉ `CleanupVerified == true`
sau bước này được dùng để mở bước credentials. `false`, exception hoặc query
không xác minh được phải chặn. Dispose terminate/check tối đa 5 giây rồi đóng
handle; fallback finalizer chỉ đóng handle, không phải bằng chứng cleanup để
cho phép dùng token. Owner phải được giữ trong try/finally đến cleanup, không
để GC quyết định thời điểm dừng chương trình.

Test `scripts/Test-HtkkWindowsJobProcess.ps1` biên dịch class production và
kiểm quoting. Khi chạy Windows, test thực sự launch child PowerShell: mã thoát,
argument có quote/space/trailing slash, sentinel credential không kế thừa,
parent thoát trước grandchild đang treo, timeout, lỗi AssignProcessToJobObject
native trước resume và lỗi image không tồn tại. Test dùng private reflection
override handle qua C# shim có `object[]` kiểu xác định để tạo lỗi gán thật;
không ghép reflection argument bằng PowerShell. Shim chỉ trả category/type enum
cố định khi lỗi, không xuất exception message tùy ý hoặc đường dẫn. Preflight
typed invocation chạy trên cả Linux; lỗi Win32 thật vẫn chỉ kiểm trên Windows.
API public luôn dùng Job vừa tạo.

Primitive chưa đảm bảo công việc được tạo qua Windows Installer service hoặc
service khác ở ngoài cây process. Không kill `msiserver` dùng chung và không
suy service đã dừng từ client exit. MSI timeout/lỗi vẫn phải chặn credentials
theo policy riêng. Cần review, chạy test Win32 trên runner thật, rồi mới tích
hợp cho supplier và mọi compiler/oracle/helper; chưa đóng TASK-003.
