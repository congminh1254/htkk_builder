# Chẩn đoán private không dùng pipe

API tùy chọn:

```text
LaunchWithOutputFiles(executable, workingDirectory, string[] arguments,
                     noWindow, x86, stdoutPath, stderrPath)
```

`Launch` mặc định vẫn dùng NUL cho cả ba standard handles. API mới chỉ đổi cách
thu stdout/stderr: stdin là NUL, hai output là file riêng, STARTUPINFOEX chỉ
cho kế thừa đúng ba handle đó. Không kế thừa handle môi trường khác, không giữ
pipe để grandchild có thể làm `GetResult()` treo sau root exit. Cơ chế suspended
→ Job assignment → retained identity → resume và cleanup proof giữ nguyên.

Hai đường dẫn phải tuyệt đối, khác nhau và nằm dưới working directory tin cậy.
Không chấp nhận file/dir đã tồn tại, alternate data stream, device name, dấu
chấm/khoảng trắng cuối component hoặc parent có ReparsePoint. File được tạo
bằng native CREATE_NEW, OPEN_REPARSE_POINT, share-none và ACL kế thừa từ thư mục
riêng của runner; không overwrite. Không tự tạo parent directory. Trên lỗi
prelaunch, file private mới tạo một phần có thể còn lại để caller dọn; không
xóa file bất kỳ theo tên sau một lỗi và không xuất nội dung ra log.

Bytes/encoding của child được giữ nguyên; boundary không normalize hoặc parse
diagnostics. Caller chỉ đọc sau khi Dispose/cleanup đã xác minh và phải kiểm
length ≤1 MiB trước khi đọc. Giới hạn này là giới hạn đọc tại caller, không phải
quota ghi đĩa. Compiler chỉ được xuất mã CS#### trong report enum/list đã lọc;
không in source/path/stderr hoặc exception message tùy ý. Category launch mới
chỉ gồm `output-path-invalid` và `output-create-failed` ngoài enum cũ.

Test standalone có sáu preflight cases chạy cả Linux. Trên Windows còn kiểm
capture stdout/stderr tách biệt, credential sentinel không vào environment,
một file handle sentinel cố tình đánh inheritable không được truyền vào child,
file đã tồn tại không bị overwrite và junction output parent bị từ chối trước
child execution. Normal/orphan/timeout/assignment-error tests vẫn được giữ.
Thay đổi capture này chưa có Windows run thật khi viết tài liệu; compile Linux
không thay thế kiểm chứng Win32. Chưa tự tích hợp compiler ở API này.
