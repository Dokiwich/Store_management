# TỪ ĐIỂN DỮ LIỆU (DATA DICTIONARY) CHUẨN HỌC THUẬT

Dưới đây là chi tiết Từ điển dữ liệu với đầy đủ các cột bắt buộc: **Tên Trường, Kiểu Dữ Liệu, Loại Khóa, Ràng Buộc, và Mô Tả**. Bạn có thể copy trực tiếp các bảng này dán vào phần 3.3 của file báo cáo Word (Word tự động nhận diện bảng từ Markdown).

### 1. Bảng `users` (Tài khoản người dùng)
Lưu trữ thông tin đăng nhập và phân quyền của nhân viên, quản trị viên.

| Tên Trường | Kiểu Dữ Liệu | Khóa | Ràng Buộc | Mô Tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | PK | AUTO_INCREMENT | Mã định danh tài khoản |
| `username` | VARCHAR(50) | | NOT NULL, UNIQUE | Tên đăng nhập (duy nhất) |
| `password` | VARCHAR(255)| | NOT NULL | Mật khẩu (đã được hash bcrypt) |
| `full_name`| VARCHAR(100)| | DEFAULT NULL | Họ và tên người dùng |
| `role` | ENUM | | DEFAULT 'customer' | Quyền: 'admin', 'staff', 'customer'|
| `is_active`| TINYINT | | DEFAULT 1 | Trạng thái (1: hoạt động, 0: khóa) |

### 2. Bảng `customers` (Khách hàng)
Quản lý thông tin khách hàng mua máy và tích điểm.

| Tên Trường | Kiểu Dữ Liệu | Khóa | Ràng Buộc | Mô Tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | PK | AUTO_INCREMENT | Mã định danh khách hàng |
| `full_name` | VARCHAR(100)| | NOT NULL | Họ tên khách hàng |
| `phone` | VARCHAR(20) | | NOT NULL, UNIQUE | Số điện thoại (duy nhất) |
| `email` | VARCHAR(100)| | DEFAULT NULL | Địa chỉ Email |
| `address` | TEXT | | DEFAULT NULL | Địa chỉ liên hệ |
| `loyalty_points`| INT | | DEFAULT 0 | Điểm tích lũy thành viên |
| `created_at` | TIMESTAMP | | DEFAULT CURRENT_TIMESTAMP | Thời gian tạo tài khoản |

### 3. Bảng `products` (Sản phẩm)
Quản lý thông tin, giá bán và cấu hình của Laptop.

| Tên Trường | Kiểu Dữ Liệu | Khóa | Ràng Buộc | Mô Tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | PK | AUTO_INCREMENT | Mã định danh sản phẩm |
| `supplier_id` | INT | FK | DEFAULT NULL | ID Nhà cung cấp (Tham chiếu `suppliers`) |
| `name` | VARCHAR(200)| | NOT NULL | Tên Laptop |
| `category` | VARCHAR(50) | | DEFAULT NULL | Danh mục (Gaming, Văn phòng, Ultrabook...) |
| `brand` | VARCHAR(50) | | DEFAULT NULL | Hãng sản xuất (Dell, Asus, Apple...) |
| `import_price`| DECIMAL(15,2)|| NOT NULL | Giá nhập vào |
| `price` | DECIMAL(15,2)|| NOT NULL | Giá bán lẻ |
| `stock_quantity`| INT | | DEFAULT 0 | Số lượng tồn kho |
| `spec_cpu` | VARCHAR(100)| | DEFAULT NULL | Thông số CPU |
| `spec_ram` | VARCHAR(50) | | DEFAULT NULL | Thông số RAM |
| `spec_screen` | VARCHAR(100)| | DEFAULT NULL | Thông số Màn hình |
| `spec_hard_drive`| VARCHAR(100)| | DEFAULT NULL | Thông số Ổ cứng (SSD/HDD) |
| `spec_gpu` | VARCHAR(150)| | DEFAULT NULL | Thông số Card đồ họa (VGA) |
| `spec_weight` | VARCHAR(50) | | DEFAULT NULL | Trọng lượng máy |
| `spec_os` | VARCHAR(50) | | DEFAULT NULL | Hệ điều hành cài sẵn |
| `description` | TEXT | | DEFAULT NULL | Bài viết mô tả chi tiết sản phẩm |
| `is_active` | TINYINT | | DEFAULT 1 | Trạng thái kinh doanh |

### 4. Bảng `orders` (Đơn hàng / Hóa đơn)
Lưu thông tin hóa đơn khi khách hàng thanh toán tại POS.

| Tên Trường | Kiểu Dữ Liệu | Khóa | Ràng Buộc | Mô Tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | PK | AUTO_INCREMENT | Mã định danh hóa đơn |
| `user_id` | INT | FK | DEFAULT NULL | ID Nhân viên bán hàng (Tham chiếu `users`) |
| `customer_id` | INT | FK | DEFAULT NULL | ID Khách hàng (Tham chiếu `customers`) |
| `voucher_code`| VARCHAR(50) | | DEFAULT NULL | Mã giảm giá đã sử dụng |
| `total_amount`| DECIMAL(15,2)|| NOT NULL | Tổng tiền phải thanh toán (sau giảm giá) |
| `created_at` | TIMESTAMP | | DEFAULT CURRENT_TIMESTAMP | Thời gian lập hóa đơn |
| `status` | VARCHAR(20) | | DEFAULT 'Completed' | Trạng thái (Completed, Cancelled...) |

### 5. Bảng `order_details` (Chi tiết Đơn hàng)
Lưu danh sách các sản phẩm (và số lượng) nằm trong 1 hóa đơn.

| Tên Trường | Kiểu Dữ Liệu | Khóa | Ràng Buộc | Mô Tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | PK | AUTO_INCREMENT | Mã chi tiết |
| `order_id` | INT | FK | NOT NULL (ON DELETE CASCADE) | Thuộc hóa đơn nào (Tham chiếu `orders`) |
| `product_id` | INT | FK | NOT NULL | Sản phẩm nào (Tham chiếu `products`) |
| `quantity` | INT | | NOT NULL | Số lượng mua |
| `price_at_sale`| DECIMAL(15,2)|| NOT NULL | Đơn giá sản phẩm tại thời điểm bán |

### 6. Bảng `promotions` (Mã giảm giá)
Quản lý các chương trình khuyến mãi, voucher.

| Tên Trường | Kiểu Dữ Liệu | Khóa | Ràng Buộc | Mô Tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | PK | AUTO_INCREMENT | Mã khuyến mãi |
| `code` | VARCHAR(20) | | NOT NULL, UNIQUE | Chuỗi mã code (VD: SALE500K) |
| `discount_value`| DECIMAL(15,2)|| NOT NULL | Giá trị giảm |
| `discount_type` | ENUM | | DEFAULT 'amount' | Loại giảm ('amount' = trừ tiền, 'percent' = %)|
| `min_order_value`| DECIMAL(15,2)|| DEFAULT 0.00 | Giá trị đơn hàng tối thiểu để áp dụng |
| `end_date` | DATE | | DEFAULT NULL | Hạn chót sử dụng |
| `is_active` | TINYINT | | DEFAULT 1 | Trạng thái khả dụng |

### 7. Bảng `suppliers` (Nhà cung cấp)
Quản lý danh sách các nhà phân phối máy tính.

| Tên Trường | Kiểu Dữ Liệu | Khóa | Ràng Buộc | Mô Tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | PK | AUTO_INCREMENT | Mã định danh nhà cung cấp |
| `name` | VARCHAR(100)| | NOT NULL | Tên công ty / Nhà cung cấp |
| `phone` | VARCHAR(20) | | DEFAULT NULL | Số điện thoại liên hệ |
| `email` | VARCHAR(100)| | DEFAULT NULL | Email liên hệ |
| `address` | TEXT | | DEFAULT NULL | Địa chỉ công ty |
| `is_active` | TINYINT(1) | | DEFAULT 1 | Trạng thái hợp tác |

### 8. Bảng `import_logs` (Lịch sử nhập kho)
Ghi nhận mỗi lần kho nhập thêm hàng hóa.

| Tên Trường | Kiểu Dữ Liệu | Khóa | Ràng Buộc | Mô Tả |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INT | PK | AUTO_INCREMENT | Mã phiếu nhập |
| `product_id` | INT | FK | DEFAULT NULL | Sản phẩm được nhập (Tham chiếu `products`)|
| `product_name` | VARCHAR(200)| | DEFAULT NULL | Lưu log tên SP phòng khi SP bị xóa |
| `quantity` | INT | | NOT NULL | Số lượng nhập |
| `import_price` | DECIMAL(15,2)|| NOT NULL | Đơn giá nhập tại thời điểm đó |
| `total_cost` | DECIMAL(15,2)|| NOT NULL | Tổng tiền nhập (quantity * import_price) |
| `created_at` | TIMESTAMP | | DEFAULT CURRENT_TIMESTAMP | Ngày giờ nhập kho |
