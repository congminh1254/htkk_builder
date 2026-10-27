# Deadline của MSI và môi trường tiến trình

`probe-htkk-windows.ps1` chỉ chạy MSI sau khi hash, Authenticode, publisher và
CAB tương ứng đã được kiểm như trước. Giữ nguyên `/i`, `/qn`, `/norestart`,
`ISCHECKFORPRODUCTUPDATES=0`, log riêng và xử lý mã 0/3010; truyền đường dẫn qua
`ArgumentList` thay vì tự ghép dấu nháy.

MSI nay có deadline 180 giây. Helper `Invoke-HtkkBoundedNativeProcess.ps1` xóa
môi trường kế thừa, chỉ thêm danh sách biến hệ điều hành giống launch HTKK.
stdout/stderr được drain vào null stream, không log hay giữ chuỗi tùy ý. Hết
hạn thì kill process tree và chờ tối đa 5 giây; chỉ xác nhận process đã dừng khi
handle giữ lại báo `HasExited`. Không xác minh được thì chặn
`credentials_safe`; workflow không nạp token publish/callback sau đó.

Integration test chạy tiến trình con thật, kiểm mã thoát khác 0, sentinel không
được kế thừa, timeout, PID con đã dừng và lỗi thiếu tool. Không chạy MSI trong
bài test local. Windows workflow cũng chạy bài này trước khi tải nguồn.

Đây là một phần TASK-003, chưa hoàn tất issue: cần phân loại DNS/TLS/HTTP và
attempt/retry transient, xử lý deadline/cleanup UIA và OCX, chứng minh tất cả
supplier descendants/oracle helpers dừng (không chỉ root), và kiểm chứng Windows
mới cho thay đổi MSI. MSI có thể sử dụng Windows Installer service; trạng thái
root đã dừng không tự chứng minh mọi service/descendant đã dừng.
