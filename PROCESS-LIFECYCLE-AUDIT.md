# Kiểm toán vòng đời tiến trình cho TASK-003

Kiểm tra ngày 27/10/2026. Đây là kiểm tra chỉ đọc mã runner và các bảng trong
MSI đã ghim; không cài đặt hoặc chạy HTKK/MSI, không thu thập dữ liệu người dùng.
Các nhận xét dưới đây không chứng minh tương thích nghiệp vụ hoặc hoàn tất #4.

## Nguồn và cách tái hiện kiểm tra MSI

Bản được đọc tại môi trường kiểm tra:

```text
/workspace/reference/htkk/installer/HTKK_5.8.1_DLL_signed/HTKK.msi
SHA256: 7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080
```

Đường dẫn là vị trí của bản đã có trong workspace, không phải yêu cầu về đường
dẫn máy mới. Phải kiểm đúng hash trước khi dùng kết luận này cho một bản khác.
Hash khớp không thay thế kiểm chứng Authenticode của quy trình intake.

Các công cụ `msiinfo`/thư viện đã có tại
`/workspace/reference/tools/root`; lệnh dưới chỉ đọc cơ sở dữ liệu MSI. Môi trường
tiến trình được dựng từ danh sách cho phép, không kế thừa biến xác thực:

```python
import hashlib
import os
from pathlib import Path
import subprocess

root = Path('/workspace/reference/tools/root')
msi = Path('/workspace/reference/htkk/installer/HTKK_5.8.1_DLL_signed/HTKK.msi')
assert hashlib.sha256(msi.read_bytes()).hexdigest() == (
    '7c1da251ee2acd126a2363e4457502b8ad6fc0792d78dc0a92b153701dc29080'
)
env = {key: value for key, value in os.environ.items()
       if key in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')}
env['LD_LIBRARY_PATH'] = str(root / 'usr/lib/x86_64-linux-gnu')
tool = str(root / 'usr/bin/msiinfo')

def read(*args):
    return subprocess.run([tool, *args], env=env, text=True,
                          capture_output=True, check=True).stdout

tables = read('tables', str(msi)).splitlines()
for table in ('CustomAction', 'ServiceInstall', 'ServiceControl',
              'MsiServiceConfig', 'MsiServiceConfigFailureActions', 'SelfReg',
              'InstallExecuteSequence', 'InstallUISequence', 'ControlEvent'):
    print('TABLE', table)
    print(read('export', str(msi), table) if table in tables else 'ABSENT')
```

Tương ứng, các thao tác đọc chính là `msiinfo tables HTKK.msi` và
`msiinfo export HTKK.msi <tên bảng>`. Không gọi `msiexec`, không sửa các bảng hoặc
trích xuất rồi thực thi custom action.

## Kết quả các bảng MSI

Không có bảng `ServiceInstall`, `ServiceControl`, `MsiServiceConfig`,
`MsiServiceConfigFailureActions` hoặc `SelfReg` trong danh sách bảng. Execute
sequence vẫn có các standard action như `InstallServices`, `StartServices`,
`SelfRegModules`; sự hiện diện của standard action không tự tạo bản ghi service
hoặc self-registration khi bảng tương ứng không có.

`CustomAction` có chín dòng:

| Action | Type | Vị trí/điều kiện liên quan đã đọc |
| --- | --- | --- |
| `ISPreventDowngrade` | 19 | Execute/UI sequence 450, `ISFOUNDNEWERPRODUCTVERSION`; action báo lỗi |
| `ISRunSetupTypeAddLocalEvent` | 1 | Execute sequence 1050, `Not Installed And Not ISRUNSETUPTYPEADDLOCALEVENT`; DLL `ISExpHlp.dll`, entry `RunSetupTypeAddLocalEvent` |
| `ISSetAllUsers` | 257 | Execute/UI sequence 10, `Not Installed`; DLL `SetAllUsers.dll`, entry `SetAllUsers` |
| `SetARPINSTALLLOCATION` | 51 | Execute sequence 1100; đặt property `ARPINSTALLLOCATION` từ `[INSTALLDIR]` |
| `SetAllUsersProfileNT` | 51 | Execute/UI sequence 970, `VersionNT = 400`; đặt property |
| `setAllUsersProfile2K` | 51 | Execute/UI sequence 980, `VersionNT >= 500`; đặt property |
| `setUserProfileNT` | 51 | Execute/UI sequence 960, `VersionNT`; đặt property |
| `ShowMsiLog` | 226 | Không có trong Execute/UI sequence; được gọi từ finish-dialog `ControlEvent` |
| `ISPrint` | 1 | `LicenseAgreement/ISPrintButton` gọi qua `ControlEvent`, điều kiện `1`; DLL `SetAllUsers.dll`, entry `PrintScrollableText` |

Type 1 là DLL custom action; type 257 là `0x101`, gồm DLL và cờ
`FirstSequence`, không có cờ async `0x80`. Type 51 đặt property. Chỉ
`ShowMsiLog` có cờ async: 226 = `0xE2`, gồm executable có directory source
(`SystemFolder`), async và continue. Target là
`[SystemFolder]notepad.exe "[MsiLogFileLocation]"`.

Ba event gọi `ShowMsiLog` là:

| Dialog/control | Điều kiện | Ordering |
| --- | --- | --- |
| `SetupCompleteError/Finish` | `MsiLogFileLocation And (ISSHOWMSILOG="1")` | 3 |
| `SetupCompleteSuccess/OK` | `MsiLogFileLocation And (ISSHOWMSILOG="1") And NOT ISENABLEDWUSFINISHDIALOG` | 6 |
| `SetupInterrupted/Finish` | `MsiLogFileLocation And (ISSHOWMSILOG="1")` | 3 |

Runner gọi `/qn`, không hiển thị các finish dialog này; action async được khai
báo trên không được lên lịch bởi đường execute hiện tại. Không suy rằng toàn
bộ MSI không có action async chỉ vì run dùng `/qn`.

Các bảng không mô tả mọi hành vi bên trong DLL custom action. Kiểm tra này
không chứng minh DLL không khởi chạy thêm công việc, gọi COM hoặc service.
Mã thoát MSI 0 chứng minh client báo transaction kết thúc thành công; nó không
chứng minh Windows Installer service đã kết thúc tiến trình. Service dùng chung
có thể tiếp tục tồn tại hợp lệ: không kill service hoặc các `msiexec.exe` khác
theo tên để làm báo cáo có vẻ sạch.

## Kết luận về cài đặt bị ngắt

Kill MSI client khi hết hạn không chứng minh service đã dừng transaction hoặc
rollback. Vì vậy phải chặn bước nạp credentials sau timeout, lỗi tool hoặc kết
thúc chưa xác minh, dù handle client đã báo thoát. `fd6aa15` đã hạ cờ an toàn
trước khi gọi installer helper, chỉ khôi phục sau mã 0, trạng thái `exited`,
không timeout và client đã dừng. Đây là điều kiện hoàn tất installer được kiểm
soát, không phải bằng chứng mọi supplier descendant đã dừng.

## Khoảng trống cleanup còn lại

Ở mã được kiểm tra, cleanup supplier dùng `Kill(true)` nếu root còn sống rồi
kiểm `root.HasExited`. Nếu root đã thoát trước, hậu duệ còn sống có thể bị bỏ
qua. Handle giữ lại cho một số `regsvr32` chỉ được dispose cuối probe; dispose
không terminate hoặc xác minh tiến trình đã kết thúc.

`Get-DescendantProcessIds` có giới hạn snapshot 4.096 tiến trình và 96 vòng
duyệt. Snapshot/polling hoặc một tập handle của các tiến trình đã quan sát có
thể hỗ trợ chẩn đoán, nhưng không chứng minh đầy đủ mọi hậu duệ: có thể bỏ lỡ
parent sống ngắn, bỏ lỡ child giữa hai lần quan sát, hoặc mất quan hệ sau root
thoát. Không gọi các giới hạn này là bằng chứng cleanup đầy đủ.

Compiler/oracle có deadline root 30 giây và môi trường sạch. Tuy nhiên nhiều
nhánh timeout/finally chỉ `Kill(true)` rồi `Dispose()` mà không chờ và xác minh
đã dừng. Cờ tổng trước khi nạp credentials chưa chứa bằng chứng cleanup của
tất cả helper đó. Việc chờ kết quả đọc stdout/stderr không giới hạn sau khi
root thoát cũng có thể quá deadline nếu một child giữ pipe; cần kiểm soát cả
tiến trình và thời hạn drain, không chỉ `WaitForExit` root.

## Boundary Windows được khuyến nghị

Để chứng minh toàn bộ cây tiến trình do runner trực tiếp khởi chạy đã dừng,
dùng Windows Job Object không cho breakaway, có `KILL_ON_JOB_CLOSE`:

1. Tạo job và tạo tiến trình **suspended**, cùng môi trường chỉ chứa biến hệ điều
   hành và output riêng. Assign tiến trình vào job trước khi chạy instruction
   đầu tiên, rồi mới resume. `Process.Start()` rồi mới assign có race, không
   đáp ứng chứng minh này.
2. Giữ job handle và process identity đến cleanup. Hậu duệ thừa kế membership,
   kể cả khi root thoát hoặc quan hệ parent/PID không còn truy được qua snapshot.
3. Terminate job trong cleanup; query `JobObjectBasicAccountingInformation`
   đến khi `ActiveProcesses == 0` hoặc hết deadline hữu hạn. Chỉ số 0 được xác
   minh mới cho phép cờ cleanup tương ứng thành true. Query/assignment/cleanup
   thất bại phải chặn credentials; nếu assign thất bại, không resume root.
4. Runner Windows có thể đã nằm trong job riêng. Kiểm chứng nested-job support
   thực tế, không bật breakaway để lách assignment lỗi. Dùng primitive cho cả
   supplier/OCX và các compiler/oracle helpers hoặc một native-phase supervisor
   phù hợp; không chỉ bảo vệ HTKK rồi bỏ các helper khác ngoài cờ tổng.

Job Object quản lý tiến trình thành viên, không là sandbox toàn hệ điều hành
và không bao phủ mọi hoạt động được chuyển qua service có sẵn. Không dùng kết
quả job để suy Windows Installer service dừng. Môi trường con sạch cũng chỉ
chứng minh không kế thừa biến credentials; không tự chứng minh cách ly bảo mật
với mọi tiến trình khác chạy cùng tài khoản runner.

Kiểm thử cần chạy Windows thật: parent sinh child rồi thoát sớm; child sinh
grandchild treo; timeout; mất khả năng assign/query; cleanup lỗi; normal exit;
cờ an toàn đơn điệu không được trở lại true sau lỗi. Phải giữ deadline và
không thực thi supplier trước assignment. Test root-only hoặc assert chuỗi
source không thay các kiểm chứng vòng đời này. Sau thay harness cần dispatch
workflow mới và đọc toàn job, không rerun để gọi mã harness cũ là bản sửa mới.
