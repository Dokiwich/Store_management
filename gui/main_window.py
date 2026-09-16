import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk  # Giao diện hiện đại
from gui.components.tooltip import ToolTip
from gui.components.onboarding import GuidedTour

# Import các Tab (GIỮ NGUYÊN)
from gui.tabs.home_tab import HomeTab
from gui.tabs.pos_tab import PosTab
from gui.tabs.product_tab import ProductTab
from gui.tabs.dashboard_tab import DashboardTab
from gui.tabs.customer_tab import CustomerTab
from gui.tabs.history_tab import HistoryTab
from gui.tabs.warranty_tab import WarrantyTab
from gui.tabs.employee_tab import EmployeeTab

# Cấu hình giao diện mặc định
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self, current_user, on_logout, service_container):
        super().__init__()
        
        # --- LOGIC GIỮ NGUYÊN ---
        self.on_logout_callback = on_logout
        self.current_user = current_user
        self.role = current_user['role']

        self.title(f"LAPTOP MANAGER - Xin chào: {current_user['full_name']} ({self.role})")
        
        # Tăng kích thước cửa sổ mặc định và đặt minsize
        self.geometry("1280x768")
        self.minsize(1024, 700)
        
        # Phóng to màn hình (hỗ trợ Windows/Mac)
        def set_zoom():
            try:
                self.state("zoomed")
            except Exception:
                self.attributes("-fullscreen", True)
        self.after(100, set_zoom)
        
        self.is_dark_mode = False

        # Giải nén các logic từ container
        self.db_manager = service_container.db_manager
        self.product_service = service_container.product_service
        self.order_service = service_container.order_service
        self.report_service = service_container.report_service
        self.customer_service = service_container.customer_service
        self.warranty_service = service_container.warranty_service
        self.exporter = service_container.exporter
        self.history_service = service_container.history_service
        self.user_service = service_container.user_service
        self.promotion_service = service_container.promotion_service
        self.supplier_service = service_container.supplier_service

        self.menu_buttons = []
        self.current_btn = None
        self.cached_tabs = {}  # Cache các tab để không phải tạo lại liên tục

        # --- CẤU HÌNH STYLE CHO TREEVIEW (Bên trong các Tab con vẫn dùng Treeview cũ) ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_treeview_style() # Tách ra hàm riêng để tái sử dụng

        # --- LAYOUT CHÍNH (GRID) ---
        # Cột 0: Sidebar (cố định), Cột 1: Nội dung (co giãn)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR (Cột trái)
        # Nền xanh nhạt
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#e3f2fd")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Cố định chiều rộng sidebar

        # 2. CONTENT AREA (Cột phải)
        # Nền xám nhạt để làm nổi nội dung trắng
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#f5f5f5")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        
        # Tạo một khung chứa nội dung "nổi" lên với góc bo tròn
        self.content_area = ctk.CTkFrame(self.main_container, corner_radius=20, fg_color="#ffffff")
        self.content_area.pack(fill="both", expand=True, padx=20, pady=20)

        # --- XÂY DỰNG SIDEBAR ---
        
        # A. Logo Section
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(fill="x", pady=(30, 20))

        self.lbl_logo_icon = ctk.CTkLabel(self.logo_frame, text="⚡", font=("Segoe UI", 36), text_color="#0288d1")
        self.lbl_logo_icon.pack()

        self.lbl_logo_text = ctk.CTkLabel(self.logo_frame, text="LAPTOP STORE", font=("Montserrat", 18, "bold"), text_color="#0288d1")
        self.lbl_logo_text.pack(pady=5)

        role_display = {"admin": "Quản Trị Viên", "staff": "Nhân Viên", "customer": "Khách Hàng"}.get(self.role, "User")
        self.lbl_logo_sub = ctk.CTkLabel(self.logo_frame, text=role_display, font=("Consolas", 12), text_color="#555555")
        self.lbl_logo_sub.pack()

        # B. Menu Section (Scrollable nếu màn hình nhỏ, hoặc Frame thường)
        self.menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.menu_frame.pack(fill="both", expand=True, padx=10)

        # === [PHÂN QUYỀN MENU - LOGIC GIỮ NGUYÊN] ===
        self.btn_home = self.create_nav_btn("🏠  Trang Chủ", self.show_home_tab)
        
        if self.role == 'customer':
            self.btn_my_orders = self.create_nav_btn("📦  Đơn Hàng Của Tôi", self.show_history_tab)
            
        self.btn_warr = self.create_nav_btn("🔍  Tra Cứu BH", self.show_warranty_tab)

        if self.role in ['admin', 'staff']:
            self.create_separator()
            self.btn_pos = self.create_nav_btn("🛒  Bán Hàng", self.show_pos_tab)
            self.btn_prod = self.create_nav_btn("📦  Kho Hàng", self.show_product_tab)
            self.btn_cust = self.create_nav_btn("👥  Khách Hàng", self.show_customer_tab)
            self.btn_hist = self.create_nav_btn("📜  Lịch Sử", self.show_history_tab)

        if self.role == 'admin':
            self.create_separator()
            self.btn_dash = self.create_nav_btn("📊  Thống Kê", self.show_dashboard_tab)
            self.btn_emp = self.create_nav_btn("👤  Nhân Viên", self.show_employee_tab)

        # C. Bottom Section (Logout & Theme)
        self.bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        # Switch Theme
        self.switch_var = ctk.StringVar(value="off")
        self.theme_switch = ctk.CTkSwitch(self.bottom_frame, text="Dark Mode", command=self.toggle_theme,
                                          variable=self.switch_var, onvalue="on", offvalue="off")
        self.theme_switch.pack(pady=10)

        # Nút Logout
        self.btn_logout = ctk.CTkButton(self.bottom_frame, text="🚪 Đăng Xuất", 
                                        fg_color="#ef4444", hover_color="#dc2626",
                                        height=40, corner_radius=10, 
                                        font=("Segoe UI", 12, "bold"),
                                        command=self.perform_logout)
        self.btn_logout.pack(fill="x")

        # Mặc định mở trang chủ
        self.select_btn(self.btn_home)
        self.show_home_tab()

        # === TOOLTIPS ===
        ToolTip(self.btn_home, "Xem sản phẩm nổi bật, khuyến mãi")
        ToolTip(self.btn_warr, "Tra cứu thông tin bảo hành theo SĐT")
        ToolTip(self.btn_logout, "Đăng xuất khỏi hệ thống")
        ToolTip(self.theme_switch, "Chuyển đổi giao diện Sáng/Tối")

        if self.role in ['admin', 'staff']:
            ToolTip(self.btn_pos, "Tạo đơn hàng mới, bán hàng")
            ToolTip(self.btn_prod, "Quản lý kho hàng, thêm/sửa/xóa sản phẩm")
            ToolTip(self.btn_cust, "Quản lý thông tin khách hàng")
            ToolTip(self.btn_hist, "Xem lịch sử bán hàng và nhập hàng")

        if self.role == 'admin':
            ToolTip(self.btn_dash, "Xem thống kê doanh thu, sản phẩm bán chạy")
            ToolTip(self.btn_emp, "Quản lý tài khoản nhân viên")

        if self.role == 'customer':
            ToolTip(self.btn_my_orders, "Xem đơn hàng đã đặt")

        # === ONBOARDING TOUR ===
        if GuidedTour.should_show_tour():
            tour = GuidedTour(self)
            tour.add_step(None, "Chào mừng đến Laptop Store! 🎉",
                          "Hướng dẫn này sẽ giúp bạn làm quen với các tính năng chính.")
            tour.add_step(self.sidebar, "📌 Menu Điều Hướng",
                          "Đây là thanh menu bên trái. Nhấn vào từng mục để chuyển trang.")
            tour.add_step(self.btn_home, "🏠 Trang Chủ",
                          "Xem sản phẩm nổi bật, tìm kiếm và lọc laptop theo nhu cầu.")
            if self.role in ['admin', 'staff']:
                tour.add_step(self.btn_pos, "🛒 Bán Hàng (POS)",
                              "Tạo đơn hàng mới. Tìm sản phẩm, thêm vào giỏ, thanh toán và in hóa đơn PDF.")
                tour.add_step(self.btn_prod, "📦 Kho Hàng",
                              "Thêm, sửa, xóa sản phẩm. Xuất danh sách ra Excel.")
            if self.role == 'admin':
                tour.add_step(self.btn_dash, "📊 Thống Kê",
                              "Biểu đồ doanh thu theo tháng/năm, sản phẩm bán chạy, tồn kho thấp.")
            tour.add_step(self.content_area, "📄 Vùng Nội Dung",
                          "Nội dung chính hiển thị ở đây. Mỗi trang có bảng dữ liệu, bộ lọc riêng.")
            tour.add_step(self.theme_switch, "🌙 Dark Mode",
                          "Bật/tắt chế độ tối cho mắt thoải mái hơn.")
            tour.start()

    # --- CÁC HÀM HỖ TRỢ GIAO DIỆN (ĐÃ UPDATE VISUAL) ---
    
    def create_nav_btn(self, text, command):
        # Sử dụng CTkButton thay vì Label để có hiệu ứng hover và bo góc đẹp
        btn = ctk.CTkButton(self.menu_frame, text=text, 
                            fg_color="transparent", # Nền trong suốt
                            text_color="#333333",
                            hover_color="#b3e5fc",
                            anchor="w", # Canh trái chữ
                            height=45,
                            corner_radius=8, # Bo góc nhẹ
                            font=("Segoe UI", 13, "bold"),
                            command=lambda: [self.select_btn(btn), command()])
        
        # Cần lưu lại tham chiếu btn object để xử lý đổi màu sau này nếu muốn
        # Nhưng ở đây CTkButton tự xử lý visual, ta chỉ cần logic select
        btn.pack(fill="x", pady=2)
        self.menu_buttons.append(btn)
        return btn

    def create_separator(self):
        sep = ctk.CTkFrame(self.menu_frame, height=2, fg_color=("gray90", "gray30"))
        sep.pack(fill="x", pady=10, padx=5)

    def select_btn(self, btn):
        # Reset tất cả về trong suốt
        for b in self.menu_buttons:
            b.configure(fg_color="transparent", text_color="#333333")
        
        self.current_btn = btn
        # Highlight nút đang chọn (Màu xanh đậm)
        btn.configure(fg_color="#0288d1", text_color="white")

    def clear_content(self):
        # Ẩn tất cả các tab thay vì destroy()
        for widget in self.content_area.winfo_children():
            widget.pack_forget()

    def perform_logout(self):
        if messagebox.askyesno("Đăng Xuất", "Bạn có chắc muốn đăng xuất?"):
            self.destroy() 
            self.on_logout_callback()

    # --- THEME (LOGIC MỚI CHO CTK) ---
    def configure_treeview_style(self):
        # Cấu hình Treeview (vẫn dùng ttk) để khớp với giao diện
        bg = "#1f2937" if self.is_dark_mode else "white"
        fg = "white" if self.is_dark_mode else "black"
        h_bg = "#111827" if self.is_dark_mode else "#f9fafb"
        h_fg = "white" if self.is_dark_mode else "#374151"
        
        self.style.configure("Treeview", background=bg, foreground=fg, fieldbackground=bg, rowheight=30, borderwidth=0)
        self.style.configure("Treeview.Heading", background=h_bg, foreground=h_fg, font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[('selected', '#3b82f6')])

    def toggle_theme(self):
        if self.switch_var.get() == "on":
            self.is_dark_mode = True
            ctk.set_appearance_mode("Dark")
        else:
            self.is_dark_mode = False
            ctk.set_appearance_mode("Light")
        
        # Cập nhật lại Treeview style vì Treeview là widget cũ của tk
        self.configure_treeview_style()

    # --- CÁC HÀM SHOW TAB (LOGIC GIỮ NGUYÊN 100%) ---
    # Lưu ý: Các Tab con (HomeTab, PosTab...) được viết bằng tk.Frame
    # Chúng vẫn hoạt động tốt khi đặt bên trong ctk.CTkFrame (self.content_area)

    def show_home_tab(self):
        self.clear_content()
        if "home" not in self.cached_tabs:
            self.cached_tabs["home"] = HomeTab(self.content_area, self.product_service, self.order_service, self.promotion_service, self.current_user, on_buy_click=self.switch_to_pos)
        else:
            self.cached_tabs["home"].apply_filters()
        self.cached_tabs["home"].pack(fill="both", expand=True)

    def switch_to_pos(self, p_id=None):
        if self.role == 'customer':
            messagebox.showinfo("Thông báo", "Quý khách vui lòng liên hệ nhân viên tại quầy để mua hàng!")
            return
        
        # Cần tìm nút POS trong list để highlight visual
        # Logic tìm nút tương ứng
        for btn in self.menu_buttons:
            if "Bán Hàng" in btn.cget("text"):
                self.select_btn(btn)
                break
                
        self.show_pos_tab(product_id_to_add=p_id)

    def show_pos_tab(self, product_id_to_add=None):
        self.clear_content()
        if "pos" not in self.cached_tabs:
            pos = PosTab(self.content_area, self.product_service, self.order_service, self.promotion_service, self.exporter, self.current_user, self.customer_service)
            self.cached_tabs["pos"] = pos
        else:
            pos = self.cached_tabs["pos"]
            pos.load_products()
            
        pos.current_user_id = self.current_user['id']
        pos.pack(fill="both", expand=True)
        if product_id_to_add: 
            pos.add_product_by_id(product_id_to_add)

    def show_product_tab(self):
        self.clear_content()
        if "product" not in self.cached_tabs:
            self.cached_tabs["product"] = ProductTab(self.content_area, self.product_service, self.supplier_service, self.exporter, self.current_user)
        else:
            self.cached_tabs["product"].reload_data()
        self.cached_tabs["product"].pack(fill="both", expand=True)

    def show_dashboard_tab(self):
        self.clear_content()
        if "dashboard" not in self.cached_tabs:
            self.cached_tabs["dashboard"] = DashboardTab(self.content_area, self.report_service)
        else:
            self.cached_tabs["dashboard"].update_chart()
        self.cached_tabs["dashboard"].pack(fill="both", expand=True)

    def show_customer_tab(self):
        self.clear_content()
        if "customer" not in self.cached_tabs:
            self.cached_tabs["customer"] = CustomerTab(self.content_area, self.customer_service, self.current_user)
        else:
            self.cached_tabs["customer"].load_data()
        self.cached_tabs["customer"].pack(fill="both", expand=True)

    def show_history_tab(self):
        self.clear_content()
        if "history" not in self.cached_tabs:
            self.cached_tabs["history"] = HistoryTab(self.content_area, self.history_service, self.current_user)
        else:
            self.cached_tabs["history"].load_data()
        self.cached_tabs["history"].pack(fill="both", expand=True)

    def show_warranty_tab(self):
        self.clear_content()
        if "warranty" not in self.cached_tabs:
            self.cached_tabs["warranty"] = WarrantyTab(self.content_area, self.warranty_service)
        self.cached_tabs["warranty"].pack(fill="both", expand=True)

    def show_employee_tab(self):
        self.clear_content()
        if "employee" not in self.cached_tabs:
            self.cached_tabs["employee"] = EmployeeTab(self.content_area, self.user_service)
        else:
            self.cached_tabs["employee"].load_data()
        self.cached_tabs["employee"].pack(fill="both", expand=True)