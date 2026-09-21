from tkinter import ttk, messagebox
import customtkinter as ctk # Import CustomTkinter
from gui.components.tooltip import ToolTip

class EmployeeTab(ctk.CTkFrame): # Kế thừa CTkFrame
    def __init__(self, parent, user_service, current_user=None):
        super().__init__(parent, fg_color="transparent")
        self.user_service = user_service
        self.current_user = current_user

        # 1. Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 5))
        
        ctk.CTkLabel(header, text="QUẢN LÝ NHÂN VIÊN", 
                     text_color=("#111827", "white"), 
                     font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=20)

        # 2. Container chính (Chia 2 cột: Form & List)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Cấu hình grid: Cột 0 (Form) cố định, Cột 1 (Bảng) giãn nở
        main_container.grid_columnconfigure(0, weight=0) # Sidebar không giãn
        main_container.grid_columnconfigure(1, weight=1) # Bảng giãn hết cỡ
        main_container.grid_rowconfigure(0, weight=1)

        # --- CỘT TRÁI: FORM THÊM MỚI ---
        # Frame chứa form
        frame_form = ctk.CTkFrame(main_container, width=300, corner_radius=15, fg_color=("white", "#1f2937"))
        frame_form.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        frame_form.grid_propagate(False) # Cố định kích thước width=300

        # Nội dung Form
        ctk.CTkLabel(frame_form, text="Thêm Nhân Viên", text_color="#2563eb", 
                     font=("Segoe UI", 16, "bold")).pack(pady=(20, 20))

        # Hàm tạo input nhanh
        def create_input(label, parent):
            ctk.CTkLabel(parent, text=label, font=("Segoe UI", 12, "bold")).pack(fill="x", padx=20, pady=(5, 0))
            entry = ctk.CTkEntry(parent, height=35)
            entry.pack(fill="x", padx=20, pady=(5, 10))
            return entry

        self.entry_user = create_input("Tên đăng nhập:", frame_form)
        self.entry_pass = create_input("Mật khẩu:", frame_form)
        self.entry_pass.configure(show="*") # Ẩn mật khẩu
        self.entry_name = create_input("Họ và Tên:", frame_form)
        
        # Combobox Chức vụ
        ctk.CTkLabel(frame_form, text="Chức vụ:", font=("Segoe UI", 12, "bold")).pack(fill="x", padx=20, pady=(5, 0))
        self.cb_role = ctk.CTkComboBox(frame_form, values=["staff", "admin", "customer"], height=35)
        self.cb_role.pack(fill="x", padx=20, pady=(5, 20))
        self.cb_role.set("staff") # Giá trị mặc định

        # Các nút bấm
        btn_add = ctk.CTkButton(frame_form, text="Thêm Nhân Viên", height=45,
                      fg_color="#2563eb", hover_color="#1d4ed8", font=("Segoe UI", 13, "bold"),
                      command=self.add_employee)
        btn_add.pack(fill="x", padx=20, pady=(10, 10))
        ToolTip(btn_add, "Tạo tài khoản nhân viên mới")

        btn_delete = ctk.CTkButton(frame_form, text="Xóa Đã Chọn", height=45,
                      fg_color="#ef4444", hover_color="#b91c1c", font=("Segoe UI", 13, "bold"),
                      command=self.delete_employee)
        btn_delete.pack(fill="x", padx=20)
        ToolTip(btn_delete, "Khóa tài khoản nhân viên đang được chọn")

        # --- CỘT PHẢI: DANH SÁCH (Treeview) ---
        frame_list = ctk.CTkFrame(main_container, fg_color="transparent")
        frame_list.grid(row=0, column=1, sticky="nsew")

        # Style cho bảng đẹp hơn
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#2563eb", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.map("Treeview", background=[('selected', '#1d4ed8')])

        cols = ("id", "user", "name", "role", "active")
        self.tree = ttk.Treeview(frame_list, columns=cols, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("user", text="Tài khoản")
        self.tree.heading("name", text="Họ Tên")
        self.tree.heading("role", text="Chức vụ")
        self.tree.heading("active", text="Trạng thái")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("active", width=100, anchor="center")
        self.tree.column("role", width=100, anchor="center")
        self.tree.column("user", width=150)
        self.tree.column("name", width=200)

        # --- THANH CUỘN ---
        # Scrollbar dọc
        v_scroll = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        # Scrollbar ngang
        h_scroll = ttk.Scrollbar(frame_list, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Layout bằng pack trong frame bên phải
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        
        self.load_data()

    # --- LOGIC GIỮ NGUYÊN ---
    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        users = self.user_service.get_all_users()
        for u in users:
            # u: id, username, full_name, role, is_active
            status = "Hoạt động" if u[4] == 1 else "Đã khóa"
            self.tree.insert("", "end", values=(u[0], u[1], u[2], u[3], status))

    def add_employee(self):
        u = self.entry_user.get()
        p = self.entry_pass.get()
        n = self.entry_name.get()
        r = self.cb_role.get()

        if not u or not p or not n:
            messagebox.showwarning("Thiếu tin", "Vui lòng nhập đủ thông tin!")
            return

        success, msg = self.user_service.add_user(u, p, n, r)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.entry_user.delete(0, "end")
            self.entry_pass.delete(0, "end")
            self.entry_name.delete(0, "end")
            self.load_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def delete_employee(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel)
        u_id = item['values'][0]
        u_name = item['values'][1]
        
        if self.current_user and str(u_id) == str(self.current_user.get('id')):
            messagebox.showwarning("Cảnh báo", "Không thể tự khóa tài khoản của chính mình!")
            return

        if messagebox.askyesno("Xác nhận", f"Bạn muốn khóa tài khoản {u_name}?"):
            if self.user_service.delete_user(u_id):
                self.load_data()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa!")