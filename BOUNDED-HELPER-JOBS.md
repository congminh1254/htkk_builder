# Job boundary cho các oracle dùng result file

`Invoke-HtkkBoundedJobProcess.ps1` dùng boundary Windows đã có: tạo suspended,
assign job trước resume, môi trường chỉ có biến hệ điều hành, stdout/stderr vào
NUL. Đây là helper cho tool có kết quả trong tệp riêng, không phải thay thế
chung cho compiler hoặc chương trình cần đọc stdout.

Root được chờ tối đa 30 giây. Sau đó helper gọi `Dispose()` một lần; boundary
thực hiện `Stop(5000)`, xác minh root đã dừng và `ActiveProcesses == 0`, rồi
đóng handles. Không gọi Stop trước Dispose để tránh hai deadline cleanup cộng
dồn. Exit code được chuyển lại Int32 có dấu như `Diagnostics.Process.ExitCode`.
Root thoát thành công không thay thế bằng chứng job đã sạch.

Các oracle thực thi trong `Test-HtkkTaxIdOracle.ps1`,
`Test-HtkkProfileAliasOracle.ps1` và `Test-HtkkCommonHeaderOracle.ps1` dùng helper
này, giữ nguyên executable, working directory, argument order, source pins và
kiểm nội dung result file. Chỉ đọc JSON hoặc copy XML sau khi helper xác minh
cleanup; giữ enum `oracle-timeout`/`host-or-tool-failure` hiện có. stdout/stderr
oracle trước đây chỉ được drain riêng, không dùng làm kết quả nghiệp vụ.

Kết quả có cờ `oracleJobCleanupVerified`. Biến tổng script
`htkkHelperJobsStopped` chuyển sang false trước mỗi lần launch và chỉ được giữ
true nếu cả các lần trước và lần hiện tại đều xác minh sạch. Exception không
phân loại/cleanup failure không được ghi đè bởi một helper thành công sau đó.
Probe đã nối biến tổng này vào `credentials_safe` và báo `NATIVE_HELPER_PROCESS_NOT_STOPPED` nếu chưa xác minh sạch. Helper không chứng minh các tiến trình ngoài job đã dừng.

## Kiểm chứng

`Test-HtkkBoundedJobProcess.ps1` gọi wrapper production với tám tình huống policy,
gồm signed exit, timeout, wait failure, missing tool, cleanup failure, exception
không biết và trạng thái không an toàn không bị success sau đó xóa đi.

Phần Windows riêng thực thi fixture thật: root sinh child treo rồi thoát trước;
wrapper phải dừng orphan đó, root timeout phải bị dừng, sentinel credentials
không được kế thừa, missing image được từ chối có cleanup. Phần này không chạy
trên Linux; output local ghi rõ Win32 integration chưa chạy. Không chạy HTKK
hoặc dùng dữ liệu người dùng trong các test fixture.

## Phần còn lại của TASK-003

Đợt bổ sung compiler dùng `Invoke-HtkkBoundedCompiler.ps1` và API native
output-file riêng cho cả ba oracle lẫn `New-HtkkX86ReferenceHost.ps1`. Việc giữ
mã `CS####`, bounded read sau cleanup và giới hạn đọc/encoding được mô tả tại
`BOUNDED-COMPILER-DIAGNOSTICS.md`; không thay compiler bằng NUL. Cần Windows
workflow mới để xác minh tích hợp, không coi test policy trên Linux là bằng
chứng native oracle/runtime behavior được giữ nguyên.

Job không chứng minh Windows Installer service đã dừng hoặc bao phủ mọi công
việc được chuyển sang service có sẵn. Giữ điều kiện fail-closed của installer;
không kill service dùng chung hoặc nới điều kiện để có callback thành công.
