# Chờ focus của hộp thoại XML nguyên bản

Run 40565276626 dừng ở `gtgt-export-filename-keyboard-editing`, chưa xác nhận
nhập đường dẫn thành công: hộp thoại, editor và nút lưu đã khớp. Stage cũ gộp
kiểm focus, chọn và gõ nên chưa xác định chính xác thao tác thất bại.
Đây chưa phải lỗi so sánh XML hay số thuế; không đánh dấu ca đó đạt.

Controller nay đợi tối đa 40 lần quan sát hợp lệ (timer 100 ms), yêu cầu hai lần
liên tiếp cùng hộp thoại/editor đang giữ focus. Mỗi lần vẫn kiểm lại process,
owner, tiêu đề, combo chứa editor, nút gốc và đường dẫn/hash đầu vào hoặc thư mục
đầu ra mới. Editor/hộp thoại đổi làm ca thất bại. Không nhập khi chưa sẵn sàng.

Một khi bắt đầu thao tác bàn phím, policy khóa việc thử nhập lại; lỗi sau chọn
hoặc gõ dừng ca. Chỉ reset sau khi gửi thành công thao tác nút gốc để phục vụ
hộp thoại nhập/xuất kế tiếp. Không sửa EXE/DLL/config hoặc số liệu thuế.

`Test-HtkkFileDialogFocusPolicy.ps1` biên dịch chính class policy production và
kiểm chuyển trạng thái, mất focus, đổi handle, giới hạn chờ và chống nhập lại.
Suite boundary gọi test này trước khi đọc các báo cáo giả lập. Python chỉ kiểm
hợp đồng tích hợp; bằng chứng GUI thực phải đến từ dispatch Windows mới.
