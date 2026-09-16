# Store Management System (Hệ thống Quản lý Cửa hàng Laptop)

Đây là đồ án hệ thống quản lý cửa hàng laptop được phát triển bằng Python (CustomTkinter) và cơ sở dữ liệu MySQL. 
Hệ thống sử dụng kiến trúc 3 lớp (3-Tier Architecture) giúp phân tách rõ ràng giao diện (GUI), xử lý nghiệp vụ (Service) và truy xuất dữ liệu (DAO).

## 🚀 Tính năng nổi bật
- **Quản lý Kho (Inventory):** Thêm, sửa, xóa laptop, hỗ trợ AI gợi ý sản phẩm cùng mức giá.
- **Bán hàng (POS):** Tạo đơn hàng, áp dụng Voucher, hỗ trợ quét mã vạch (Barcode Scanner).
- **Quản lý Nhân sự (Employees):** Quản lý nhân viên (Admin/Staff), đánh giá hiệu suất nhân viên.
- **Quản lý Khách hàng (CRM):** Phân hạng khách hàng (Đồng, Bạc, Vàng) dựa trên chi tiêu.
- **Tra cứu Bảo hành:** Tra cứu lịch sử mua hàng và thời hạn bảo hành.
- **Báo cáo Thống kê:** Biểu đồ doanh thu trực quan bằng Matplotlib.

## 🛠️ Cài đặt & Chạy dự án (Local Environment)

### 1. Yêu cầu hệ thống
- Python 3.9+
- MySQL Server 8.0+

### 2. Thiết lập Cơ sở dữ liệu (MySQL)
1. Mở MySQL Workbench hoặc phpMyAdmin.
2. Tạo database mới: `CREATE DATABASE store_management;`
3. Import file CSDL: Chạy file `database/sql/CSDL.sql` để tạo cấu trúc 8 bảng và dữ liệu mẫu.

### 3. Cài đặt thư viện Python
Mở Terminal/Command Prompt tại thư mục chứa dự án và chạy:
```bash
pip install -r requirements.txt
```
*(Nếu chưa có `requirements.txt`, hãy cài các gói: `mysql-connector-python`, `customtkinter`, `matplotlib`, `openpyxl`, `python-dotenv`, `fpdf`, `pillow`, `bcrypt`)*

### 4. Cấu hình biến môi trường
Tạo file `.env` ở thư mục gốc (ngang hàng `main.py`) với nội dung:
```env
DB_HOST=localhost
DB_USER=root
DB_PASS=123456
DB_NAME=store_management
```
*(Thay đổi user và password tương ứng với máy của bạn)*

### 5. Chạy ứng dụng
```bash
python main.py
```
**Tài khoản đăng nhập mẫu:**
- Admin: `admin` / `admin123`
- Nhân viên: `staff1` / `staff123`

---

## 🔒 Security Architecture (Kiến trúc Bảo mật)

Vì đây là dự án Desktop Application sử dụng mô hình Client-Server nội bộ, hệ thống được thiết kế với các tiêu chuẩn bảo mật cơ sở sau:

### 1. Tại sao sử dụng `.env` để kết nối MySQL trực tiếp?
Hệ thống hiện tại kết nối trực tiếp đến MySQL và cấu hình được lưu trong file `.env`. 
**Giải trình:** Kiến trúc này được thiết kế dựa trên giả định mô hình mạng **LAN nội bộ (Intranet)** của một cửa hàng, nơi máy khách (Client) và máy chủ CSDL (Database Server) nằm trong cùng một mạng bảo mật vật lý, không expose CSDL ra Internet. 
*Hướng phát triển (Future Work):* Nếu đưa hệ thống lên môi trường Internet (Public Cloud), cấu trúc sẽ được chuyển đổi sang mô hình dùng **RESTful API Gateway** (ví dụ: FastAPI / Node.js) để ẩn thông tin kết nối CSDL khỏi ứng dụng Client.

### 2. Chống lỗi tranh chấp dữ liệu (Concurrency / Pessimistic Locking)
Hệ thống sử dụng kỹ thuật **Pessimistic Locking** (`SELECT ... FOR UPDATE`) trong các giao dịch nhạy cảm (như trừ số lượng tồn kho khi thanh toán). Điều này đảm bảo tính nhất quán (ACID), ngăn chặn lỗi âm kho khi 2 nhân viên cùng bấm thanh toán 1 sản phẩm ở cùng 1 phần nghìn giây.

### 3. Mã hóa mật khẩu (Password Hashing)
Toàn bộ mật khẩu của người dùng được băm (hash) bằng thuật toán **Bcrypt** với salt động trước khi lưu xuống CSDL. Kể cả quản trị viên (DBA) cũng không thể đọc được mật khẩu gốc của nhân viên.

### 4. Chống tấn công SQL Injection
Toàn bộ tầng DAO (Data Access Object) đều sử dụng Parameterized Queries (`%s` trong mysql-connector) để bind dữ liệu. Hệ thống tuyệt đối không dùng phương pháp cộng chuỗi (String Concatenation) khi truy vấn SQL.

### 5. Phân quyền (RBAC - Role Based Access Control)
Hệ thống hỗ trợ 2 vai trò:
- **Admin:** Có toàn quyền (Thêm/Sửa/Xóa dữ liệu, xem báo cáo tổng).
- **Staff:** Chỉ có quyền vận hành (Tạo đơn hàng, tra cứu bảo hành, xem kho hàng). Giao diện của Staff sẽ tự động ẩn các nút thao tác nhạy cảm.

---
*Developed by: [Tên của bạn]*
