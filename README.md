# RobotFace - khuôn mặt robot cho OLED SSD1306

Blockly extension tạo khuôn mặt robot trên OLED SSD1306 128x64 bằng thư viện
`robotface.py`.

## Cách dùng các khối

1. Trong phần **Khởi tạo**, đặt khối **khởi tạo khuôn mặt robot trên OLED**.
   Khối này tạo cả `oled` và `face`, sử dụng `pin19.pin` (SCL), `pin20.pin`
   (SDA), địa chỉ `0x3C` và tốc độ cập nhật mặc định 25 FPS.
2. Trong các khối **sự kiện**, đặt biểu cảm, hoạt ảnh, hướng nhìn hoặc hiệu ứng
   cần thực hiện khi sự kiện xảy ra.
3. Trong **lặp lại mãi**, đặt khối **cập nhật khuôn mặt** để hoạt ảnh nền và
   chuyển biểu cảm tiếp tục chạy. Khối này cũng nghỉ 1 ms sau mỗi lần cập nhật
   để tránh vòng lặp chạy liên tục không cần thiết.

## Các khối

- **Biểu cảm**: chọn một trong `neutral`, `happy`, `laugh`, `excited`, `love`,
  `wink`, `surprised`, `talk`, `sad`, `cry`, `angry`, `suspicious`, `sleepy`,
  `sleep`, `dizzy`, `error`; thời gian chuyển mặc định 300 ms.
- **Phát hoạt ảnh**: chọn chạy một lần hoặc lặp nền đến khi dùng khối dừng.
  Khi lặp, khuôn mặt trở về biểu cảm nền và nghỉ 2 giây giữa các lượt. Chế độ
  lặp không chờ và được cập nhật trong vòng lặp mãi. Danh sách gồm
  `blink`, `double_blink`, `wink`, `laugh`, `surprise`,
  `shake`, `nod`, `bounce`, `look_around`, `heartbeat`, `dizzy`, `fall_asleep`,
  `wake_up`.
- **Dừng hoạt ảnh đang phát**: dừng hoạt ảnh nền; hoạt ảnh chuyển trạng thái
  như `fall_asleep` vẫn kết thúc ở trạng thái đích tương ứng.
- **Hiệu ứng lặp**: là lớp chuyển động chồng lên biểu cảm hiện tại, không tự
  chọn biểu cảm. Chọn biểu cảm phù hợp để hiệu ứng dễ thấy hơn: `love` với
  `heartbeat`, `talk` với hiệu ứng `talk`, `laugh` với hiệu ứng `laugh`, và
  `cry` với `sob`. `idle` tự chớp mắt và liếc nhìn. Cần có khối cập nhật trong
  vòng lặp mãi.
  Có thể bật ở một sự kiện và tắt ở một sự kiện khác. Các hiệu ứng này độc lập
  với chế độ hoạt ảnh lặp của khối **Phát hoạt ảnh**.
- **Nói trong ... giây**: hoạt ảnh miệng tự bật, chờ đủ thời gian rồi tự tắt.
- **Nhìn về hướng**: điều khiển hướng nhìn độc lập với biểu cảm.
- **Chờ ... ms**: chờ trong khi vẫn cập nhật khuôn mặt và chạy hiệu ứng nền.
- **Cập nhật khuôn mặt**: đặt trong vòng lặp mãi, không đặt riêng một lần.

## Yêu cầu phần cứng

OLED phải là SSD1306 I2C 128x64. Chân SCL/SDA mặc định theo cấu hình ví dụ của
bo mạch và hiện được cố định trong khối khởi tạo.
`robotface.py` cần MicroPython có hỗ trợ `framebuf.ellipse()` và
`framebuf.poly()` (MicroPython 1.19 trở lên).
