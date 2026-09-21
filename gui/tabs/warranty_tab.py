from tkinter import ttk, messagebox
import customtkinter as ctk # Import CustomTkinter
from datetime import datetime, timedelta
from gui.components.tooltip import ToolTip

class WarrantyTab(ctk.CTkFrame): # Kế thừa CTkFrame
    def __init__(self, parent, warranty_service):
        super().__init__(parent, fg_color="transparent") # Nền trong suốt
        self.warranty_service = warranty_service
        
        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(header, text="TRA CỨU BẢO HÀNH", 
                     text_color=("#2563eb", "white"),
                     font=("Segoe UI", 24, "bold")).pack(side="left", padx=20)

        # --- Search Area ---
        # Khung tìm kiếm bo tròn, nổi bật
        frame_search = ctk.CTkFrame(self, fg_color=("white", "#1f2937"), corner_radius=15)
        frame_search.pack(fill="x", padx=20, pady=10)
        
        # Container bên trong để căn chỉnh
        inner_search = ctk.CTkFrame(frame_search, fg_color="transparent")
        inner_search.pack(padx=20, pady=20)

        ctk.CTkLabel(inner_search, text="Nhập SĐT khách hoặc Mã đơn hàng:", 
                     font=("Segoe UI", 12)).pack(side="left", padx=(0, 10))
        
        self.entry_search = ctk.CTkEntry(inner_search, width=300, 
                                         placeholder_text="Ví dụ: 0987654321 hoặc HD001...",
                                         font=("Segoe UI", 13))
        self.entry_search.pack(side="left", padx=10)
        self.entry_search.bind("<Return>", lambda e: self.do_search())
        
        btn_search = ctk.CTkButton(inner_search, text="Tra Cứu", 
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      width=120, height=35,
                      font=("Segoe UI", 13, "bold"),
                      command=self.do_search)
        btn_search.pack(side="left", padx=10)
        ToolTip(btn_search, "Tìm kiếm thông tin bảo hành")

        # --- Table Result Container ---
        # Tạo Frame chứa bảng để dễ quản lý layout
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Table Result (Vẫn dùng ttk.Treeview vì CTK chưa có widget bảng mạnh) ---
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        
        self.tree = ttk.Treeview(table_frame, columns=("order", "cust", "phone", "prod", "date", "status"), show="headings", height=20)
        
        # Cấu hình tiêu đề
        self.tree.heading("order", text="Mã Đơn")
        self.tree.heading("cust", text="Khách Hàng")
        self.tree.heading("phone", text="SĐT")
        self.tree.heading("prod", text="Sản Phẩm")
        self.tree.heading("date", text="Ngày Mua")
        self.tree.heading("status", text="Trạng Thái")
        
        # Cấu hình cột
        self.tree.column("order", width=80, minwidth=80, anchor="center")
        self.tree.column("cust", width=180, minwidth=150)
        self.tree.column("phone", width=120, minwidth=100)
        self.tree.column("prod", width=250, minwidth=200)
        self.tree.column("date", width=120, minwidth=100, anchor="center")
        self.tree.column("status", width=200, minwidth=150, anchor="center") # Tăng width cho status
        
        # Scrollbar (Dùng ttk Scrollbar chuẩn để tương thích với Treeview)
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # --- LOGIC GIỮ NGUYÊN ---
    def do_search(self):
        kw = self.entry_search.get()
        if not kw:
            messagebox.showwarning("Lỗi", "Vui lòng nhập thông tin tìm kiếm")
            return
            
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        rows = self.warranty_service.search_warranty(kw)
        
        if not rows:
            messagebox.showinfo("Thông báo", "Không tìm thấy dữ liệu phù hợp")
            return

        for row in rows:
            # row: (order_id, name, phone, product, price, created_at, warranty_time)
            try:
                purchase_date = row[5]
                # Đọc warranty_time từ CSDL (mặc định 12 tháng)
                w_raw = row[6] if len(row) > 6 else 12
                months = 12
                if w_raw:
                    try:
                        nums = [int(s) for s in str(w_raw).split() if s.isdigit()]
                        months = nums[0] if nums else int(w_raw)
                    except:
                        months = 12

                expiry_date = purchase_date + timedelta(days=months * 30)
                today = datetime.now()
                
                # Logic hiển thị trạng thái
                if today < expiry_date:
                    days_left = (expiry_date - today).days
                    status = f"✅ Còn hạn ({days_left} ngày)"
                else:
                    status = "❌ Hết hạn"
                
                date_str = purchase_date.strftime("%d/%m/%Y")
            except (AttributeError, TypeError):
                status = "❓ Lỗi dữ liệu ngày"
                date_str = str(row[5]) if row[5] else "N/A"
            
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], date_str, status))