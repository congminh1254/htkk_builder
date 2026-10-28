# GitHub Pages trên public builder

Repo nguồn vẫn private tại `htkk-net/htkk_web`. Repo `congminh1254/htkk_builder` chứa workflow tin cậy; GitHub Pages chỉ nhận website tĩnh đã build, giống nội dung phục vụ công khai cho trình duyệt. Không checkout nhánh source vào job Pages, không upload log/source archive, không thực thi code từ artifact trong job có token.

## Luồng phát hành

1. Private dispatch gửi SHA vào public `build.yml`. Release kiểm current main, chạy unit/schema/browser/audit/build, xuất input synthetic và chạy Windows.
2. `publish.py` giữ output trên nhánh private `pages-output`, không gửi dispatch triển khai sang repo private nữa.
3. Public `pages.yml` chỉ tự chạy khi whole release workflow thành công trên main. CI, fork, failed/cancelled release không được deploy.
4. Job Pages dùng token đọc nguồn để checkout commit artifact bất biến. Script tin cậy kiểm metadata/current main, builder run thành công và13ca Windows đúng builder SHA. Chờ native tối đa20phút; failure, artifact thay đổi hoặc source thay đổi đều chặn.
5. Chỉ `output/site` được upload cho Pages; token checkout không lưu, `.git` của checkout không nằm trong artifact. GitHub Pages dùng `GITHUB_TOKEN` của repo public, không cần token Pages riêng.

## Cấu hình một lần

- Repo builder → Settings → Pages: Source **GitHub Actions**.
- Gỡ Custom domain `hotrokekhai.net` khỏi Pages của repo `htkk-net/htkk_web` nếu còn gắn. Sau đó đặt Custom domain này trên builder. Nếu domain đang thuộc một Pages site khác, cần gỡ tại site đó trước.
- Nếu DNS đang có CNAME đích `congminh1254.github.io`, đích đó đã khớp owner builder. Nếu đích hiện tại là `htkk-net.github.io`, đổi về `congminh1254.github.io`. Với apex dùng A/AAAA/ALIAS theo hướng dẫn GitHub Pages; không tạo CNAME tiêu chuẩn ở apex nếu nhà cung cấp DNS không hỗ trợ flattening/ALIAS. Giữ các bản ghi mail/dịch vụ khác.
- Xác nhận DNS check và HTTPS certificate, bật Enforce HTTPS khi GitHub cho phép.
- Environment `github-pages` cho phép deploy từ main builder; giữ restriction này.
- Secret `SOURCE_READ_TOKEN` ở builder tiếp tục cần Contents: read và quyền đọc commit statuses trên source private để kiểm chứng. Những token xuất bản/status hiện có của release giữ quyền tương ứng. Không cần thêm token Pages.

## Retry artifact đã kiểm thử

Trên builder, chạy workflow `Deploy verified HTKK website`, ref main, input `pages_commit` là SHA đầy đủ của `htkk-net/htkk_web:pages-output`. Gate yêu cầu artifact vẫn là bản mới nhất và source vẫn đúng current main; không gán lại provenance cho artifact cũ. Muốn source mới thì chạy release mới.

Chỉ chốt triển khai khi whole Pages workflow success và `https://hotrokekhai.net/build.json` khớp `site/build.json` của artifact. Kiểm thêm landing, Dashboard, asset và liên kết tải mẫu. Không coi việc dispatch hoặc upload artifact thành công là đã deploy.
