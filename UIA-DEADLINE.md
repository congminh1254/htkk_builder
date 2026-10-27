# Helper UI Automation: môi trường sạch và cleanup

UIA vẫn chạy Windows PowerShell STA, không profile/noninteractive, với helper
UTF-8 BOM đã parse trước và deadline 15 giây. Nay dùng cùng primitive bounded
native-process của MSI: chỉ biến hệ điều hành, drain output vào null stream,
kill/wait/dispose có xác minh khi hết hạn. JSON của helper riêng vẫn được đọc
bằng UTF-8; từ chối tệp trên 32 KiB trước parse.

Kết quả cleanup không xác minh được chặn `credentials_safe` kể cả khi HTKK root
đã dừng. Trạng thái này chỉ có thể chuyển về không an toàn trong một probe;
thành công sau đó không ghi đè lỗi trước. Exception bất ngờ trong boundary cũng
chặn. Không log stderr, đường dẫn hoặc nội dung GUI: lỗi process thoát khác 0
được phân loại `helper-nonzero-exit`, thay vì đoán ParserError từ stderr.
Preflight parser vẫn có category riêng; provider/missing/invalid/timeout vẫn
được phân biệt bằng enum cố định.

`Test-HtkkUiaProcessBoundary.ps1` lấy chính function từ AST production và chạy
11 tình huống với native-runner giả lập: kết quả hợp lệ/provider, malformed,
oversize/missing, timeout, nonzero/tool failure, cleanup failure, tính đơn điệu
và exception. Primitive tiến trình thật có integration test độc lập cho cách ly
môi trường và timeout/termination; không coi mock là bằng chứng UIA Windows.

TASK-003 còn theo dõi OCX/supplier descendants và Installer service, oracle
cleanup, phân loại DNS/TLS/HTTP và retry/attempt hữu hạn. Phải dispatch Windows
main mới sau khi review/push để kiểm chứng thay đổi UIA.
