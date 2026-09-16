# Sơ Đồ Lớp (Class Diagram) - Kiến trúc 3 lớp đã Refactor

Sơ đồ này thể hiện mối quan hệ giữa các lớp trong chức năng Giỏ hàng và Thanh toán, minh chứng cho sự tách biệt rõ ràng giữa GUI (PosTab), Tầng xử lý nghiệp vụ (OrderService, Cart) và Tầng truy cập dữ liệu (OrderDAO).

Bạn có thể copy mã nguồn bên dưới dán vào trang web **https://mermaid.live/** để xuất ra file ảnh (PNG/JPG) chèn vào báo cáo Word.

```mermaid
classDiagram
    class PosTab {
        -order_service: OrderService
        -exporter: Exporter
        +add_product_by_id(p_id)
        +remove_item()
        +apply_voucher_logic()
        +process_final_payment()
        +update_cart_ui()
    }
    
    class OrderService {
        -dao: OrderDAO
        -cart: Cart
        -product_service: ProductService
        -promotion_service: PromotionService
        +add_to_cart(product_id, qty) bool
        +remove_from_cart(product_id) void
        +apply_voucher(voucher_code) bool
        +checkout(user_id) tuple
    }
    
    class Cart {
        -items: dict
        -voucher_code: String
        -discount_amount: Float
        +add_item()
        +remove_item()
        +cart_total() Float
        +final_total() Float
    }
    
    class CartItem {
        +product_id: int
        +name: String
        +price: Float
        +qty: int
        +max_stock: int
        +total() Float
    }
    
    class OrderDAO {
        -db_manager: DatabaseManager
        +create_order(user_id, cart_items, total, voucher) tuple
    }
    
    class Exporter {
        +print_invoice_pdf(order_id, cart_items, total, filepath) bool
    }

    PosTab --> OrderService : gọi nghiệp vụ
    PosTab --> Exporter : dùng tiện ích xuất file
    OrderService *-- Cart : quản lý trạng thái
    Cart *-- CartItem : chứa nhiều
    OrderService --> OrderDAO : gọi truy cập dữ liệu
```
