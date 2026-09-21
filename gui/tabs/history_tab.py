from tkinter import ttk
import customtkinter as ctk
from gui.components.tooltip import ToolTip

class HistoryTab(ctk.CTkFrame): # Kế thừa CTkFrame
    def __init__(self, parent, history_service, current_user):
        super().__init__(parent, fg_color="transparent")
        self.history_service = history_service
        self.current_user = current_user
        
        # --- HEADER ---
        # Tiêu đề lớn
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 5))
        
        title_text = "ĐƠN HÀNG CỦA TÔI" if self.current_user['role'] == 'customer' else "LỊCH SỬ HOẠT ĐỘNG"
        ctk.CTkLabel(header, text=title_text, 
                     text_color=("#0288d1", "white"),
                     font=("Montserrat", 22, "bold")).pack()

        # --- TABVIEW (Thay thế Notebook cũ) ---
        self.tab_view = ctk.CTkTabview(self, fg_color="#f5f5f5")
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=10)

        # Tạo tab con
        self.tab_view.add("Lịch Sử Mua Hàng" if self.current_user['role'] == 'customer' else "Lịch Sử Bán Hàng")
        if self.current_user['role'] != 'customer':
            self.tab_view.add("Lịch Sử Nhập Hàng")

        # Cấu hình Style cho bảng (Treeview)
        self.setup_treeview_style()

        # --- TAB 1: LỊCH SỬ BÁN HÀNG ---
        self.setup_sales_table()

        # --- TAB 2: LỊCH SỬ NHẬP HÀNG ---
        if self.current_user['role'] != 'customer':
            self.setup_imports_table()
        
        # Nút làm mới chung (Đặt dưới cùng)
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", pady=10)
        
        btn_refresh = ctk.CTkButton(footer, text="Làm mới dữ liệu", 
                      fg_color="#0984e3", hover_color="#00cec9",
                      font=("Arial", 12, "bold"), height=40,
                      command=self.load_data)
        btn_refresh.pack()
        ToolTip(btn_refresh, "Tải lại lịch sử bán hàng và nhập hàng")

        self.load_data()

    def setup_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Màu header bảng
        style.configure("Treeview.Heading", background="#2d3436", foreground="white", font=("Segoe UI", 10, "bold"))
        # Màu dòng dữ liệu
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        # Màu khi chọn dòng
        style.map("Treeview", background=[('selected', '#0984e3')])

    def setup_sales_table(self):
        # Lấy frame cha là nội dung của Tab "Bán Hàng"
        tab_name = "Lịch Sử Mua Hàng" if self.current_user['role'] == 'customer' else "Lịch Sử Bán Hàng"
        parent_tab = self.tab_view.tab(tab_name)
        
        # Frame chứa bảng
        table_frame = ctk.CTkFrame(parent_tab, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "staff", "cust", "total", "date")
        self.tree_sales = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree_sales.heading("id", text="Mã Đơn")
        self.tree_sales.heading("staff", text="Nhân Viên")
        self.tree_sales.heading("cust", text="Khách Hàng")
        self.tree_sales.heading("total", text="Tổng Tiền")
        self.tree_sales.heading("date", text="Ngày Bán")
        
        self.tree_sales.column("id", width=60, anchor="center")
        self.tree_sales.column("total", width=120, anchor="e")
        self.tree_sales.column("date", width=150, anchor="center")
        
        # Scrollbar
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_sales.yview)
        self.tree_sales.configure(yscroll=sb.set)
        
        self.tree_sales.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def setup_imports_table(self):
        # Lấy frame cha là nội dung của Tab "Nhập Hàng"
        parent_tab = self.tab_view.tab("Lịch Sử Nhập Hàng")

        table_frame = ctk.CTkFrame(parent_tab, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "name", "qty", "price", "total", "date")
        self.tree_imports = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree_imports.heading("id", text="ID")
        self.tree_imports.heading("name", text="Sản Phẩm")
        self.tree_imports.heading("qty", text="SL Nhập")
        self.tree_imports.heading("price", text="Giá Nhập")
        self.tree_imports.heading("total", text="Thành Tiền")
        self.tree_imports.heading("date", text="Ngày Nhập")
        
        self.tree_imports.column("id", width=50, anchor="center")
        self.tree_imports.column("qty", width=60, anchor="center")
        self.tree_imports.column("price", width=120, anchor="e")
        self.tree_imports.column("total", width=120, anchor="e")
        self.tree_imports.column("date", width=150, anchor="center")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_imports.yview)
        self.tree_imports.configure(yscroll=sb.set)
        
        self.tree_imports.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # --- LOGIC LOAD DỮ LIỆU (GIỮ NGUYÊN) ---
    def load_data(self):
        # 1. Load Sales
        for i in self.tree_sales.get_children(): self.tree_sales.delete(i)
        
        # Nếu là customer thì truyền user_id vào
        uid = self.current_user['id'] if self.current_user['role'] == 'customer' else None
        sales = self.history_service.get_sales_history(user_id=uid)
        for row in sales:
            # Format tiền và ngày
            try:
                total_val = float(row[3] or 0)
            except (ValueError, TypeError):
                total_val = 0
            total = "{:,.0f}".format(total_val)
            try:
                date = row[4].strftime("%d/%m/%Y %H:%M")
            except (AttributeError, TypeError):
                date = str(row[4]) if row[4] else "N/A"
            cust_name = row[2] if row[2] else "Khách lẻ"
            self.tree_sales.insert("", "end", values=(row[0], row[1], cust_name, total, date))

        # 2. Load Imports (nếu không phải customer)
        if self.current_user['role'] != 'customer':
            for i in self.tree_imports.get_children(): self.tree_imports.delete(i)
            imports = self.history_service.get_import_history()
            for row in imports:
                try:
                    price_val = float(row[3] or 0)
                    total_val = float(row[4] or 0)
                except (ValueError, TypeError):
                    price_val = total_val = 0
                price = "{:,.0f}".format(price_val)
                total_cost = "{:,.0f}".format(total_val)
                try:
                    date = row[5].strftime("%d/%m/%Y %H:%M")
                except (AttributeError, TypeError):
                    date = str(row[5]) if row[5] else "N/A"
                self.tree_imports.insert("", "end", values=(row[0], row[1], row[2], price, total_cost, date))