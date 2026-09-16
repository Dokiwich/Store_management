# Sơ Đồ Tuần Tự (Sequence Diagram) - Luồng Thanh Toán (Checkout)

Sơ đồ này mô tả chi tiết các bước trao đổi thông điệp (Message passing) từ lúc người dùng nhấn nút thanh toán trên giao diện cho đến khi dữ liệu lưu vào MySQL và in ra hóa đơn PDF.

Bạn có thể copy mã nguồn bên dưới dán vào trang web **https://mermaid.live/** để xuất ra file ảnh (PNG/JPG) chèn vào báo cáo Word.

```mermaid
sequenceDiagram
    actor User as Người dùng (Nhân viên)
    participant GUI as Tầng GUI (PosTab)
    participant OS as Tầng Service (OrderService)
    participant Cart as Domain Model (Cart)
    participant DAO as Tầng DAO (OrderDAO)
    participant DB as CSDL (MySQL)
    participant Exp as Tiện ích (Exporter)

    User->>GUI: Bấm "Tiến hành thanh toán"
    GUI->>User: Hiển thị Popup (Nhập SĐT & Voucher)
    
    Note over User,GUI: Nhập thông tin và xác nhận
    User->>GUI: Bấm "Xác nhận & In hóa đơn"
    
    GUI->>OS: checkout(user_id)
    activate OS
    OS->>Cart: get_items_as_dict_list()
    Cart-->>OS: items_list
    OS->>Cart: final_total
    Cart-->>OS: total_amount
    
    OS->>DAO: create_order(user_id, items_list, total_amount, voucher)
    activate DAO
    DAO->>DB: INSERT INTO orders (...)
    DAO->>DB: INSERT INTO order_details (...)
    DB-->>DAO: Trả về order_id mới
    DAO-->>OS: (True, "order_id: 105")
    deactivate DAO
    
    OS->>Cart: clear() (Xóa giỏ hàng)
    OS-->>GUI: (True, "order_id: 105")
    deactivate OS
    
    GUI->>Exp: print_invoice_pdf(105, items_list, total_amount, file_path)
    activate Exp
    Exp-->>GUI: File PDF được tạo thành công
    deactivate Exp
    
    GUI-->>User: Hiển thị thông báo "Giao dịch thành công!"
```
