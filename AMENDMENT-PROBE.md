# Kiểm chứng điều kiện tiên quyết của kê khai bổ sung

Chế độ `gtgt-amendment-inspect` hiện chỉ thực hiện bước đầu: mở tờ khai chính 01/GTGT tháng 10/2026, lần đầu, ngành thông thường, không phụ lục, toàn bộ 27 ô tiền bằng 0 bằng HTKK gốc rồi bấm nút **Ghi** gốc. Chế độ chưa mở lại tờ khai bổ sung, chưa kiểm KHBS và chưa xuất/nhập XML bổ sung.

Báo cáo chỉ đạt giai đoạn `gtgt-original-declaration-saved-inspected` khi đã quan sát đồng thời:

- Hộp thông báo gốc `0002` có nội dung “Đã ghi dữ liệu thành công!”, đúng loại form, tiêu đề và một nút Đóng. Chỉ hộp này được xác nhận.
- Có đúng một tệp XML khai chính mới trong thư mục DataFiles của MST giả lập `9999999997`; trước bấm Ghi chưa có tệp tương ứng. Không tự tạo tệp khai trước đó.
- Tệp nằm trực tiếp trong thư mục giả lập, không reparse point, tên có tiền tố `01_GTGT_TT80_`, nội dung được HTKK tự ghi, root `Sections`, tối đa 256 KiB; SHA-256 không đổi trong các lần quan sát.
- `isDataChanged` của worksheet gốc đã trở về false sau khi hộp thành công đóng; 27 ô tiền trên worksheet và 27 thuộc tính Value theo Path của tệp được ghi đều bằng 0; tám trường HEADER giả lập vẫn đúng.

Chỉ công bố cờ boolean, kích thước và hash; không đưa đường dẫn, tên tệp cụ thể, XML nội bộ hay văn bản ô bất kỳ vào báo cáo. `amendmentLifecycleVerified=false` và `runtimeRoundTrip=false` luôn giữ nguyên, kể cả khi bước Ghi đạt. Các mode cũ có toàn bộ metadata mới mặc định false/0/rỗng.

Đây là điều kiện cần cho bước bổ sung sau này: `CheckPeriodKhbs` (`060004F4`) yêu cầu tệp tờ khai chính tồn tại; thiếu tệp báo `0107`, thiếu lần bổ sung trước báo `0296`. `cmdSave_Click` gốc là `060003A1`, `WinDoWorkSheetSave` là `06000090`; hàm dựng tên nội bộ là `GetFileNameBySheet` `060000A2`. Không gọi trực tiếp các hàm nghiệp vụ/lưu này trong reference host.

Bước tiếp theo cần đóng worksheet sạch, mở lại D1 cùng kỳ bằng menu gốc, chọn bổ sung, kiểm lần 1/ngày lập và các sheet KHBS gốc theo nhánh DIA_BAN. Chỉ sau bằng chứng runtime riêng mới được khẳng định những bước đó đạt.
