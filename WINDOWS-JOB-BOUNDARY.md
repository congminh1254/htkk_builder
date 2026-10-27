# Primitive Windows Job chưa tích hợp

`scripts/HtkkWindowsJobProcess.cs` là boundary riêng của runner, chưa thay cách
launch HTKK/compiler/oracle trong pipeline. Không sửa EXE/DLL/config gốc. Chưa
có bằng chứng Win32 integration thật cho primitive này; compile trên Linux
không chứng minh Windows Job hoạt động.

API `Launch(executable, workingDirectory, arguments, noWindow, x86)` xóa môi
trường kế thừa và chỉ truyền danh sách biến hệ điều hành đang dùng trong runner.
Chỉ kế thừa handle NUL qua STARTUPINFOEX handle-list riêng; không kế thừa handle
môi trường khác. Std input/output/error dùng NUL hợp lệ để Console.WriteLine
không lỗi và output không ra log. Đường dẫn/argument
không xuất vào lỗi; category cố định. Vì không capture stdout/stderr, caller
phải đọc output có cấu trúc từ file riêng như các oracle hiện hành; không thay
thế helper đang cần đọc pipe một cách máy móc.

Boundary tạo Job không breakaway với `KILL_ON_JOB_CLOSE`, tạo process bằng
`CREATE_SUSPENDED`, gán vào Job rồi mới `ResumeThread`. Gán thất bại thì process
vẫn chưa thực thi, bị terminate và chờ xác minh. Không dùng kiểu Start-Process
rồi mới gán Job vì có race trước lúc gán. Nested Job trên runner Windows phải
được hỗ trợ; lỗi gán không được fallback sang launch ngoài Job.

`WaitForRootExit(ms)` và `RootExitCode` chỉ nói về root, không phải cả tree.
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
override handle để tạo lỗi gán thật; API public luôn dùng Job vừa tạo.

Primitive chưa đảm bảo công việc được tạo qua Windows Installer service hoặc
service khác ở ngoài cây process. Không kill `msiserver` dùng chung và không
suy service đã dừng từ client exit. MSI timeout/lỗi vẫn phải chặn credentials
theo policy riêng. Cần review, chạy test Win32 trên runner thật, rồi mới tích
hợp cho supplier và mọi compiler/oracle/helper; chưa đóng TASK-003.
