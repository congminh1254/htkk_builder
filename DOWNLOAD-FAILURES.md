# Phân loại tải nguồn và retry giới hạn

`Invoke-HtkkPinnedDownload.ps1` đã nối vào `Get-PinnedFile` trong probe.
Không tải gì trong bộ test. Hàm phân loại duyệt tối đa tám exception lồng nhau,
chỉ đọc kiểu exception, enum và HTTP status; không dùng message để đoán lỗi.
Kết quả chỉ có enum, số/bool và tối đa hai attempt. Không URL/path/header/body
hay thông báo exception được đưa vào kết quả.

| Nhóm | Retry |
| --- | --- |
| TLS/certificate (typed authentication/trust/secure-channel failure) | Không |
| HTTP401/403,404 và các status khác ngoài allowlist | Không |
| HTTP408/429/500/502/503/504 | Tối đa một lần |
| DNS TryAgain | Tối đa một lần |
| DNS HostNotFound/NoData/NoRecovery hoặc chỉ biết NameResolutionFailure | Không |
| Typed timeout; socket reset/aborted/network-reset; receive/send/connection-closed | Tối đa một lần |
| ConnectionRefused/Unreachable, lỗi tool không rõ, cancellation không có typed timeout | Không |
| Hash nguồn sai | Không |

IWR nhận timeout120 giây, redirect tối đa8, `MaximumRetryCount 0` để không có
retry ẩn của cmdlet. Chỉ HTTPS không userinfo/fragment được nhận; giữ proxy/CA
và kiểm TLS mặc định. Không ghi đè file đã có. Attempt thất bại xóa file dở
trước khi retry; cleanup không đạt thì dừng. Chỉ trả `verified` sau SHA256 khớp.
Injectable downloader dành cho test xác định; default downloader mới gọi mạng.
Không dùng helper này để retry GUI/oracle hoặc mismatch tài chính.

## Tích hợp vào probe

1. Dot-source helper bên cạnh dependency native-process ở đầu probe.
2. Thêm `$report.sourceDownloads=@()` (mỗi phần tử là result helper, theo thứ tự
hai nguồn ghim hiện có; không thêm URL/path). Dùng wrapper `Get-PinnedFile`
để gọi `Invoke-HtkkPinnedDownload -Url $Url -Destination $Path -ExpectedSha256 $Expected`.
3. Append đúng result vào `sourceDownloads`. Nếu `status` khác `verified`, throw
một enum cố định: `SOURCE_DOWNLOAD_DNS`, `SOURCE_DOWNLOAD_TLS`,
`SOURCE_DOWNLOAD_HTTP`, `SOURCE_DOWNLOAD_TIMEOUT`, `SOURCE_DOWNLOAD_CONNECT`,
`SOURCE_DOWNLOAD_TOOL`; hash dùng `SOURCE_HASH_MISMATCH`. Nếu
`partialFileRemoved=false`, dùng `SOURCE_DOWNLOAD_CLEANUP_NOT_VERIFIED`.
Thêm các enum này vào catch allowlist, không đưa exception.Message ra log.
4. Chỉ đặt `sourceHashesVerified=true` sau hai wrapper đều đạt, giữ nguyên
hash/CAB/MSI/chữ ký về sau. Giữ attempt thực trong `sourceDownloads`; không
rerun tự động cả job khi helper đã dùng hai attempts.
5. Thêm `Test-HtkkPinnedDownload.ps1` vào Windows workflow trước probe; đây mới
là test phân loại/control flow, vẫn cần Windows run thật để xác minh tải nguồn.

Bộ PowerShell thử exception thật có kiểu và downloader giả lập: phục hồi
transient, timeout cả hai attempts, HTTP503 rồi đạt,403/TLS/hash không retry,
xóa file dở, giữ file caller và chống lộ dữ liệu. Python kiểm wiring/helper
contract; không thay thế test hành vi PowerShell.
