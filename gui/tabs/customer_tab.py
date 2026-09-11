from tkinter import ttk, messagebox
import customtkinter as ctk # Import CustomTkinter
from gui.components.tooltip import ToolTip

class CustomerTab(ctk.CTkFrame): # Kế thừa CTkFrame
    def __init__(self, parent, customer_service, current_user):
        super().__init__(parent, fg_color="transparent")
        self.customer_service = customer_service
        self.current_user = current_user
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(header, text="👥 QUẢN LÝ KHÁCH HÀNG", 
                     text_color=("#111827", "white"),
                     font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=20)

        # Container chính (Chia 2 cột)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        main_container.grid_columnconfigure(0, weight=0) # Cột form cố định
        main_container.grid_columnconfigure(1, weight=1) # Cột bảng giãn nở
        main_container.grid_rowconfigure(0, weight=1)

        # --- 1. CỘT TRÁI: FORM NHẬP LIỆU ---
        frame_input = ctk.CTkFrame(main_container, width=300, corner_radius=15, fg_color=("white", "#1f2937"))
        frame_input.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        frame_input.grid_propagate(False)

        ctk.CTkLabel(frame_input, text="Thêm Khách Hàng", text_color="#2563eb", 
                     font=("Segoe UI", 16, "bold")).pack(pady=(20, 20))

        # Hàm tạo input nhanh
        def create_input(label, parent):
            ctk.CTkLabel(parent, text=label, font=("Segoe UI", 12, "bold")).pack(fill="x", padx=20, pady=(5, 0))
            entry = ctk.CTkEntry(parent, height=35)
            entry.pack(fill="x", padx=20, pady=(5, 10))
            return entry

        self.entry_name = create_input("Họ tên:", frame_input)
        self.entry_phone = create_input("Số điện thoại:", frame_input)
        self.entry_email = create_input("Email:", frame_input)
        
        # Nút Thêm
        btn_add = ctk.CTkButton(frame_input, text="➕ Lưu Khách Hàng", height=45,
                      fg_color="#00b894", hover_color="#00a884", font=("Segoe UI", 13, "bold"),
                      command=self.add_customer)
        btn_add.pack(fill="x", padx=20, pady=30)
        ToolTip(btn_add, "Lưu thông tin khách hàng mới vào hệ thống")
        
        # (Optional) Nút Làm mới form
        btn_clear = ctk.CTkButton(frame_input, text="🔄 Làm mới Form", height=40,
                      fg_color="gray", hover_color="gray40",
                      command=self.clear_form)
        btn_clear.pack(fill="x", padx=20)
        ToolTip(btn_clear, "Xóa các trường nhập liệu trên form")

        # --- 2. CỘT PHẢI: BẢNG DANH SÁCH ---
        frame_list = ctk.CTkFrame(main_container, fg_color="transparent")
        frame_list.grid(row=0, column=1, sticky="nsew")

        # Style cho Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#00b894", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        
        cols = ("id", "name", "phone", "email", "points")
        self.tree = ttk.Treeview(frame_list, columns=cols, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Họ Tên")
        self.tree.heading("phone", text="SĐT")
        self.tree.heading("email", text="Email")
        self.tree.heading("points", text="Điểm Tích Lũy")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("phone", width=120, anchor="center")
        self.tree.column("email", width=200)
        self.tree.column("points", width=100, anchor="center")
        
        # Thanh cuộn
        sb = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.load_data()

    # --- LOGIC GIỮ NGUYÊN ---
    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        data = self.customer_service.get_all_customers()
        for row in data:
            # row: (id, full_name, phone, email, address, loyalty_points)
            filtered_row = (row[0], row[1], row[2], row[3], row[5])
            self.tree.insert("", "end", values=filtered_row)

    def add_customer(self):
        name = self.entry_name.get()
        phone = self.entry_phone.get()
        email = self.entry_email.get()
        
        if not name or not phone:
            messagebox.showwarning("Thiếu thông tin", "Tên và SĐT là bắt buộc")
            return
            
        success, msg = self.customer_service.add_customer(name, phone, email, "")
        if success:
            messagebox.showinfo("Thành công", msg)
            self.load_data()
            self.clear_form()
        else:
            messagebox.showerror("Lỗi", msg)

    def clear_form(self):
        self.entry_name.delete(0, "end")
        self.entry_phone.delete(0, "end")
        self.entry_email.delete(0, "end")