# Kiểm chứng điều kiện tiên quyết của kê khai bổ sung

Chế độ `gtgt-amendment-inspect` hiện chỉ thực hiện bước đầu: mở tờ khai chính 01/GTGT tháng 10/2026, lần đầu, ngành thông thường, không phụ lục, toàn bộ 27 ô tiền bằng 0 bằng HTKK gốc rồi bấm nút **Ghi** gốc. Chế độ chưa mở lại tờ khai bổ sung, chưa kiểm KHBS và chưa xuất/nhập XML bổ sung.

Báo cáo chỉ đạt giai đoạn `gtgt-original-declaration-saved-inspected` khi đã quan sát đồng thời:

- Hộp thông báo gốc `0002` có nội dung “Đã ghi dữ liệu thành công!”, đúng loại form, tiêu đề và một nút Đóng. Chỉ hộp này được xác nhận.
- Có đúng một tệp XML khai chính mới trong thư mục DataFiles của MST giả lập `9999999997`; trước bấm Ghi chưa có tệp tương ứng. Không tự tạo tệp khai trước đó.
- Tệp nằm trực tiếp trong thư mục giả lập, không reparse point, tên chính xác của ca nguồn `01_GTGT_TT80_CQTQL10129_00_102026_283.xml`, nội dung được HTKK tự ghi, root `Sections`, tối đa 256 KiB; SHA-256 không đổi trong các lần quan sát.
- `isDataChanged` của worksheet gốc đã trở về false sau khi hộp thành công đóng; 27 ô tiền trên worksheet và 27 thuộc tính Value theo Path của tệp được ghi đều bằng 0; tám trường HEADER giả lập vẫn đúng.

Chỉ công bố cờ boolean, kích thước và hash; không đưa đường dẫn, tên tệp cụ thể, XML nội bộ hay văn bản ô bất kỳ vào báo cáo. `amendmentLifecycleVerified=false` và `runtimeRoundTrip=false` luôn giữ nguyên, kể cả khi bước Ghi đạt. Các mode cũ có toàn bộ metadata mới mặc định false/0/rỗng.

Đây là điều kiện cần cho bước bổ sung sau này: `CheckPeriodKhbs` (`060004F4`) yêu cầu tệp tờ khai chính tồn tại; thiếu tệp báo `0107`, thiếu lần bổ sung trước báo `0296`. `cmdSave_Click` gốc là `060003A1`, `WinDoWorkSheetSave` là `06000090`; hàm dựng tên nội bộ là `GetFileNameBySheet` `060000A2`. Không gọi trực tiếp các hàm nghiệp vụ/lưu này trong reference host.

Bước tiếp theo cần đóng worksheet sạch, mở lại D1 cùng kỳ bằng menu gốc, chọn bổ sung, kiểm lần 1/ngày lập và các sheet KHBS gốc theo nhánh DIA_BAN. Chỉ sau bằng chứng runtime riêng mới được khẳng định những bước đó đạt.

Run40419346023 dừng trước nút Ghi vì guard nhầm số sheet được nạp với số phụ lục được chọn. Workbook nguồn luôn nạp11 sheet, kể cả khi chọn0 phụ lục. Guard đã sửa thành đúng11 sheet và vẫn đồng thời bắt buộc `periodNoAnnexMatched=true`, `annexSelected=0`; chưa coi bước Ghi đã đạt cho đến lượt Windows mới.

Phân tích tên tệp: `Menu.xml` D1 có `NopTheoTinhCQT=3`. `GetNameNopTheoTinhCQT` (`060000A3`, body SHA256 `d31d979dbbbe838db307ae1ba73c6a1ece35023b1a50a7f4a8ac00d1bc60dd72`) sinh `CQTQL`+mã CQT quản lý. `GetFileNameBySheet` (`060000A2`, body SHA256 `622698495a9b6c8f41c9ddcf33e61dd2ef498743f238184ca883c674686f8044`), nhánh tháng D1 `0950–09D5`, ghép DataFile/CQT/tiểu mục/tháng+năm/phiên bản bỏ dấu chấm. Ca cố định dùng CQT10129/giá trị nội bộ ngành00/M10-2026/XML2.8.3 nên chỉ chấp nhận tên nêu trên; không dùng regex số chung. Run40419703029 đã gọi Ghi nhưng chưa xác nhận thành công; không suy bằng chứng lưu thành công từ source hay guard mới.

Các checkpoint chẩn đoán cố định phải cùng nằm trong allowlist của reader PowerShell; chỉ thêm chuỗi C# không đủ. Một kiểm thử contract kiểm toàn bộ stage literal của partial file để không che báo cáo lỗi sau điểm gọi Ghi. Run40420291134 chưa cho phép kết luận Ghi không hoạt động vì các stage mới chưa được reader chấp nhận.

Run40421387435 đã khớp hộp thành công gốc nhưng dừng ở `gtgt-amendment-prior-file-missing`. Giả định trước đó gán1701 vào tên tệp là sai: `GetPeriodInfo` (`060004E2`, body SHA256 `7e93833849afb80c512c144575d80b1c80e57c98a55a98bb16a162e48fb64983`) ánh xạ `KieuKy=19` sang nhánh1050–1383, tại1356–137C lấy `cboNganhKD.SelectedValue` vào `TieuMucHachToanVal`. Tên field này dễ nhầm, nhưng ca ngành thông thường có giá trị nội bộ00; mã tiểu mục XML1701 là field khác. Probe nay đọc và bắt buộc `TieuMucHachToanVal=00`, `maCQTQuanLy=10129`, `VersionXML=2.8.3` trước Ghi và chỉ nhận đúng tên00. Không suy rằng đã hoàn tất Ghi/đối chiếu tệp cho đến lượt Windows mới.

## Mở bổ sung lần 1 — checkpoint riêng chưa chạy Windows

Run `40421871768` (builder `819b516a`) đã hoàn tất bước Ghi gốc: đúng hộp0002, dirty=false, tệp nội bộ11.576 byte/SHA256 `c5ca2e9693ce8e047d5ee04d1b9af890b02f4003a46d5961a9719390e3286d40`, 27 ô Value và27 ô worksheet bằng0. Đây là bằng chứng của điều kiện tiên quyết, không phải kê khai bổ sung hoàn chỉnh.

Mode mới `gtgt-amendment-open-inspect` dùng lại đúng bước Ghi trên, sau đó bấm **Đóng** gốc chỉ khi trạng thái sạch và mở lại D1 bằng menu gốc, giữ tháng10/2026/ngành00/CQT10129. Chọn radio **Bổ sung** bằng control gốc; không gán số lần hoặc ngày lập, chỉ kiểm giá trị mặc định `txtLan=1` và ngày hiện tại của Windows. Sau nút Đồng ý, kiểm model gốc B/SoLan1/cùng kỳ/ngành/CQT, năm tài nguyên KHBS ghim hash và hai SheetInfo/tabs `01-KHBS`/`01-1-KHBS` được nguồn kích hoạt. Chỉ ghi boolean và kích thước bảng có giới hạn; không ghi đường dẫn, nội dung bảng hoặc XML bổ sung. Mainsheet phải giữ27 ô tiền0/định danh giả; tệp gốc và HEADER phải giữ hash/giá trị đã quan sát.

Các cờ `gtgtPeriodModelMatched`/`periodFirstDeclarationMatched` hiện có vẫn mô tả checkpoint C0 đã lưu; cờ `amendmentOpenPeriodMatched` riêng mô tả model B1 mới. Không dùng cờ C0 để khẳng định B1. Các field mở bổ sung mặc địnhfalse/0 trong mọi mode cũ. Reader nhận đúng bộ key/type/bounds, chặn metadata B1 xuất hiện ở mode khác và chặn `amendmentLifecycleVerified=true`.

Checkpoint này chỉ quan sát mở màn hình/tabs; chưa kiểm KHBS phân bổ/chênh lệch, Tổng hợp KHBS, validation lưu B1, in, export/import XML hoặc số tiền phát sinh. `amendmentLifecycleVerified=false` và `runtimeRoundTrip=false` tiếp tục giữ nguyên. Chỉ sau Windows runtime mới được ghi nhận checkpoint mở B1 đạt.

## Boundary checks before B1

Run40484715557 stopped in the offline PowerShell reader test before HTKK ran. A merge introduced a leading array element in string validation and omitted B1 flags from boolean typing. Both are corrected and individually covered. B1 alone allows up to six original menu clicks (two traversals); existing modes retain the three-click bound. The real PowerShell boundary suite is also run locally on Linux before dispatch; it is not native HTKK evidence.

B1 runtime40487969037 observed11 loaded sheets and reached the main-sheet lookup. Source WinSpreadProcess.fpSpDisplayTemplate060001A1, bodySHA48616a3afb63b1152d9a5b8b6194403a7dec05fdc3bee91f60863eae147160b5: when LoaiToKhai=B and KieuKHBS is nonempty (D1=3),0163–01AC renames sheet0 to `Tờ khai điều chỉnh`. The B1 inspector now requires that exact original caption instead of C0's name.

B1 runtime40488821238 proved B/SoLan1/date, allfive sourcepins and original01-KHBS146×65. Metadata ID`01-1-KHBS` differs from its menu/display caption`01-1/KHBS`. GetHTKKSheetInfo060000F0 copiesID andSheetNameseparately; fpSpBindDataTemplate06000194 copiesSheetInfo.SheetName to the actualvendor sheet. B1 nowkeepsmetadataID andliteraldisplaycaptiondistinct ratherthan requiring them identical.
