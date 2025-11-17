<div align="center" markdown="1">
   <sup>Special thanks to:</sup>
   <br>
   <br>
   <a href="http://go.warp.dev/cursor-pro">
      <img alt="Warp sponsorship" width="400" src="https://github.com/user-attachments/assets/ab8dd143-b0fd-4904-bdc5-dd7ecac94eae">
   </a>

### [Warp, built for coding with multiple agents.](http://go.warp.dev/cursor-pro)
[Available for MacOS, Linux, & Windows](http://go.warp.dev/cursor-pro)<br>

</div>

---

# ➤ Cursor Pro VIP

<div align="center">
<p align="center">
  <img src="./images/logo.png" alt="Cursor Pro Logo" width="200" style="border-radius: 6px;"/>
</p>

<p align="center">

[![Release](https://img.shields.io/endpoint?url=https://api.pinstudios.net/api/badges/release/qtu11/cursor-pro)](https://github.com/qtu11/cursor-pro/releases/latest)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC_BY--NC--ND_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
[![Stars](https://img.shields.io/endpoint?url=https://api.pinstudios.net/api/badges/stars/qtu11/cursor-pro)](https://github.com/qtus11/cursor-pro/stargazers)
[![Downloads](https://img.shields.io/endpoint?url=https://api.pinstudios.net/api/badges/downloads/qtu11/cursor-pro/total)](https://github.com/qtu11/cursor-pro/releases/latest)
<a href="https://buymeacoffee.com/qtusdev" target="_blank"><img alt="Buy Me a Coffee" src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support%20Me-FFDA33"></a>
 [<img src="https://devin.ai/assets/deepwiki-badge.png" alt="Ask DeepWiki.com" height="20"/>](https://deepwiki.com/qtu11/cursor-pro)

</p>


<a href="https://trendshift.io/repositories/13425" target="_blank"><img src="https://trendshift.io/api/badge/repositories/13425" alt="qtusdev%2Fcursor-pro | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
<br>

<h4>Hỗ trợ phiên bản 0.49.x mới nhất | Support Latest 0.49.x Version</h4>

Công cụ này dành cho mục đích giáo dục, hiện tại repo không vi phạm bất kỳ luật nào. Vui lòng hỗ trợ dự án gốc.
Công cụ này sẽ không tạo bất kỳ tài khoản email giả và truy cập OAuth.

Hỗ trợ Windows, macOS và Linux.

Để có hiệu suất tối ưu, hãy chạy với quyền quản trị viên và luôn cập nhật phiên bản mới nhất.

This tool is for educational purposes, currently the repo does not violate any laws. Please support the original project.
This tool will not generate any fake email accounts and OAuth access.

Supports Windows, macOS and Linux.

For optimal performance, run with privileges and always stay up to date.



![QTusdev](https://files.catbox.moe/padl51.png)


</div>

## 🔄 Nhật ký thay đổi | Change Log

[Xem nhật ký thay đổi | Watch Change Log](CHANGELOG.md)

## ✨ Tính năng | Features

* Hỗ trợ hệ thống Windows, macOS và Linux<br>Support Windows, macOS and Linux systems<br>

* Đặt lại cấu hình Cursor<br>Reset Cursor's configuration<br>

* Hỗ trợ đa ngôn ngữ (Tiếng Anh, Tiếng Việt, 简体中文, 繁體中文)<br>Multi-language support (English, Vietnamese, 简体中文, 繁體中文)<br>

## 💻 Hỗ trợ hệ thống | System Support

| Hệ điều hành | Kiến trúc      | Hỗ trợ |
|--------------|----------------|--------|
| Windows      | x64, x86       | ✅      |
| macOS        | Intel, Apple Silicon | ✅ |
| Linux        | x64, x86, ARM64 | ✅     |

## 👀 Cách sử dụng | How to use

<details open>
<summary><b>⭐ Chạy script tự động | Auto Run Script</b></summary>

### **Linux/macOS**

```bash
curl -fsSL https://raw.githubusercontent.com/qtu11/cursor-pro/main/scripts/install.sh -o install.sh && chmod +x install.sh && ./install.sh
```

### **Archlinux**

Cài đặt qua [AUR](https://aur.archlinux.org/packages/cursor-pro-git)

```bash
yay -S cursor-pro-git
```

### **Windows**

```powershell
irm https://raw.githubusercontent.com/qtu11/cursor-pro/main/scripts/install.ps1 | iex
```

</details>

Nếu bạn muốn dừng script, vui lòng nhấn Ctrl+C<br>If you want to stop the script, please press Ctrl+C

## ❗ Lưu ý | Note

📝 Cấu hình | Config
`Đường dẫn Windows / macOS / Linux | Win / Macos / Linux Path [Documents/.cursor-pro/config.ini]`
<details>
<summary><b>⭐ Cấu hình | Config</b></summary>

```
[Chrome]
# Đường dẫn Google Chrome mặc định | Default Google Chrome Path
chromepath = C:\Program Files\Google/Chrome/Application/chrome.exe

[Turnstile]
# Thời gian chờ xử lý Turnstile | Handle Turnstile Wait Time
handle_turnstile_time = 2
# Thời gian chờ ngẫu nhiên xử lý Turnstile (phải là 1-3 hoặc 1,3) | Handle Turnstile Wait Random Time (must merge 1-3 or 1,3)
handle_turnstile_random_time = 1-3

[OSPaths]
# Đường dẫn lưu trữ | Storage Path
storage_path = /Users/username/Library/Application Support/Cursor/User/globalStorage/storage.json
# Đường dẫn SQLite | SQLite Path
sqlite_path = /Users/username/Library/Application Support/Cursor/User/globalStorage/state.vscdb
# Đường dẫn Machine ID | Machine ID Path
machine_id_path = /Users/username/Library/Application Support/Cursor/machineId
# Đối với người dùng Linux: ~/.config/cursor/machineid

[Timing]
# Thời gian ngẫu nhiên tối thiểu | Min Random Time
min_random_time = 0.1
# Thời gian ngẫu nhiên tối đa | Max Random Time
max_random_time = 0.8
# Thời gian chờ tải trang | Page Load Wait
page_load_wait = 0.1-0.8
# Thời gian chờ nhập | Input Wait
input_wait = 0.3-0.8
# Thời gian chờ gửi | Submit Wait
submit_wait = 0.5-1.5
# Nhập mã xác thực | Verification Code Input
verification_code_input = 0.1-0.3
# Thời gian chờ xác thực thành công | Verification Success Wait
verification_success_wait = 2-3
# Thời gian chờ thử lại xác thực | Verification Retry Wait
verification_retry_wait = 2-3
# Thời gian chờ kiểm tra email ban đầu | Email Check Initial Wait
email_check_initial_wait = 4-6
# Thời gian chờ làm mới email | Email Refresh Wait
email_refresh_wait = 2-4
# Thời gian chờ tải trang cài đặt | Settings Page Load Wait
settings_page_load_wait = 1-2
# Thời gian thử lại khi thất bại | Failed Retry Time
failed_retry_time = 0.5-1
# Khoảng thời gian thử lại | Retry Interval
retry_interval = 8-12
# Thời gian chờ tối đa | Max Timeout
max_timeout = 160

[Utils]
# Kiểm tra cập nhật | Check Update
check_update = True
# Hiển thị thông tin tài khoản | Show Account Info
show_account_info = True

[TempMailPlus]
# Bật TempMailPlus | Enable TempMailPlus (bất kỳ email nào được chuyển tiếp đến TempMailPlus đều hỗ trợ lấy mã xác thực, ví dụ cloudflare email Catch-all)
enabled = false
# Email TempMailPlus | TempMailPlus Email
email = xxxxx@mailto.plus
# Mã pin TempMailPlus | TempMailPlus pin
epin = 

[WindowsPaths]
storage_path = C:\Users\qtusdev\AppData\Roaming\Cursor\User\globalStorage\storage.json
sqlite_path = C:\Users\qtusdev\AppData\Roaming\Cursor\User\globalStorage\state.vscdb
machine_id_path = C:\Users\qtusdev\AppData\Roaming\Cursor\machineId
cursor_path = C:\Users\qtusdev\AppData\Local\Programs\Cursor\resources\app
updater_path = C:\Users\qtusdev\AppData\Local\cursor-updater
update_yml_path = C:\Users\qtusdev\AppData\Local\Programs\Cursor\resources\app-update.yml
product_json_path = C:\Users\qtusdev\AppData\Local\Programs\Cursor\resources\app\product.json

[Browser]
default_browser = opera
chrome_path = C:\Program Files\Google\Chrome\Application\chrome.exe
edge_path = C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
firefox_path = C:\Program Files\Mozilla Firefox\firefox.exe
brave_path = C:\Program Files\BraveSoftware/Brave-Browser/Application/brave.exe
chrome_driver_path = D:\VisualCode\cursor-pro-new\drivers\chromedriver.exe
edge_driver_path = D:\VisualCode\cursor-pro-new\drivers\msedgedriver.exe
firefox_driver_path = D:\VisualCode\cursor-pro-new\drivers\geckodriver.exe
brave_driver_path = D:\VisualCode\cursor-pro-new\drivers\chromedriver.exe
opera_path = C:\Users\qtusdev\AppData\Local\Programs\Opera\opera.exe
opera_driver_path = D:\VisualCode\cursor-pro-new\drivers\chromedriver.exe

[OAuth]
show_selection_alert = False
timeout = 120
max_attempts = 3
```

</details>

* Sử dụng quyền quản trị viên để chạy script <br>Use administrator privileges to run the script

* Xác nhận rằng Cursor đã được đóng trước khi chạy script <br>Confirm that Cursor is closed before running the script<br>

* Công cụ này chỉ dành cho mục đích học tập và nghiên cứu <br>This tool is only for learning and research purposes<br>

* Vui lòng tuân thủ các điều khoản sử dụng phần mềm liên quan khi sử dụng công cụ này <br>Please comply with the relevant software usage terms when using this tool

## 🚨 Vấn đề thường gặp | Common Issues

| Nếu bạn gặp vấn đề về quyền, vui lòng đảm bảo: | Script này được chạy với quyền quản trị viên |
|:----------------------------------------------:|:--------------------------------------------:|
| If you encounter permission issues, please ensure: | This script is run with administrator privileges |
| Lỗi 'User is not authorized' | Điều này có nghĩa là tài khoản của bạn đã bị cấm vì sử dụng email tạm thời (dùng một lần). Đảm bảo sử dụng dịch vụ email không tạm thời |
| Error 'User is not authorized' | This means your account was banned for using temporary (disposal) mail. Ensure using a non-temporary mail service |

## 🤩 Đóng góp | Contribution

Chào mừng gửi Issue và Pull Request!


<a href="https://github.com/qtu11/cursor-pro/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=qtu11/cursor-pro&preview=true&max=&columns=" />
</a>
<br /><br />

## 📩 Tuyên bố miễn trừ trách nhiệm | Disclaimer

Công cụ này chỉ dành cho mục đích học tập và nghiên cứu, mọi hậu quả phát sinh từ việc sử dụng công cụ này do người dùng tự chịu trách nhiệm. <br>

This tool is only for learning and research purposes, and any consequences arising from the use of this tool are borne
by the user.

## 💰 Mua cho tôi một ly cà phê | Buy Me a Coffee

<div align="center">
  <table>
    <tr>
      <td>
        <img src="./images/provi-qrcode.jpg" alt="buy_me_a_coffee" width="280"/><br>
      </td>
      <td>
        <img src="./images/paypal.jpg" alt="buy_me_a_coffee" width="280"/><br>
      </td>
    </tr>
  </table>
</div>

## ⭐ Lịch sử sao | Star History

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=qtu11/cursor-pro&type=Date)](https://star-history.com/#qtu11/cursor-pro&Date)

</div>

## 📝 Giấy phép | License

Dự án này được cấp phép theo [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
Please refer to the [LICENSE](LICENSE.md) file for details.
