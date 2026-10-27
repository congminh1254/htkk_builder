# Compiler: deadline, job cleanup và mã lỗi có giới hạn

`Invoke-HtkkBoundedCompiler.ps1` giữ kết quả diagnostic của compiler bằng API
`LaunchWithOutputFiles`, thay vì pipe `ReadToEndAsync().GetResult()` không có
deadline drain. Các đường compile trong ba oracle và
`New-HtkkX86ReferenceHost.ps1` giữ nguyên executable/CWD, thứ tự và nội dung
arguments, source pins và checks sau compile. Helper không đổi mã CLR hoặc code
HTKK được kiểm chứng.

API native tạo hai tệp mới trong thư mục riêng, chỉ kế thừa handles đã cho phép,
assign job trước resume. Output là byte do chương trình tự chọn, không bị sửa
encoding. Root được chờ tối đa 30 giây; Dispose thực hiện một deadline cleanup
5 giây, xác minh root dừng và job `ActiveProcesses == 0`, rồi đóng handles.
Helper chỉ đọc diagnostic khi kết thúc bình thường và cleanup đã được xác minh.
Timeout giữ `compile-timeout`, không nhận output dở dang là diagnostic hoàn chỉnh.

Mỗi file được đọc tối đa 1 MiB, kiểm kích thước trước cấp buffer, không dùng
unbounded `GetContent -Raw` hoặc chờ pipe. Từ chối file quá lớn, thiếu/không đọc
được hoặc reparse point; không trả danh sách mã một phần nếu một file sai. UTF-16
BOM được nhận diện; mặc định UTF-8 replacement vẫn giữ token ASCII `CS####` từ
legacy code page. Chỉ trả tối đa mười token uppercase đúng bốn chữ số, sort và
unique như trước. Không trả nội dung lỗi, tên/path source hoặc path output.

Hai file raw được xóa sau đọc khi job đã sạch. Không đọc/xóa file khi cleanup
chưa xác minh; caller sở hữu working directory riêng. Giới hạn đọc không phải
disk quota trong lúc compiler chạy; không nhận rằng output file không thể vượt
1 MiB trước khi bị kiểm tra. Thời gian đọc file cục bộ và overhead launch không
phải lời hứa hard real-time 35 giây toàn hàm.

`compilerJobCleanupVerified` được ghi trong kết quả chuẩn bị/oracle. Cờ tổng
`htkkHelperJobsStopped` của helper giống oracle result-file: lỗi cleanup/launch
không biết chuyển sang false, success về sau không ghi đè. Probe phải tiếp tục
đưa tổng này vào điều kiện credentials. Việc compiler kết thúc khác 0 hoặc
diagnostic bị từ chối vẫn là thất bại compile/tool, không trở thành bằng chứng
nghiệp vụ đạt.

`Test-HtkkBoundedCompiler.ps1` kiểm policy production với file thật: dedupe/sort/
max10, signed exit, UTF-16 BOM, token boundary, đúng 1 MiB và vượt 1 MiB, thiếu
file, timeout/exception, không đọc trước cleanup và tính đơn điệu của cờ an toàn.
Phần Windows dùng compiler Framework hệ thống compile source cố ý sai để kiểm
`CS1525` qua API output thật, chặn raw/path trong result và xóa diagnostic riêng;
thêm fixture timeout/cách ly sentinel. Linux chỉ chạy policy, ghi rõ Win32 chưa
chạy. Cần dispatch Windows mới để chứng minh giữ behavior CLR2/native workflow.

Boundary chỉ chứng minh tiến trình thành viên job; không thay kiểm chứng MSI
service, DLL rules, source signature hoặc nghiệp vụ. Những giới hạn trong
`PROCESS-LIFECYCLE-AUDIT.md` vẫn áp dụng.
