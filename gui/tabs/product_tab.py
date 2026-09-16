import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk # Import CustomTkinter

from gui.components.tooltip import ToolTip

class ProductTab(ctk.CTkFrame): # Kế thừa CTkFrame
    def __init__(self, parent, product_service, supplier_service, exporter, current_user):
        super().__init__(parent, fg_color="transparent")
        self.product_service = product_service
        self.supplier_service = supplier_service 
        self.exporter = exporter
        self.current_user = current_user
        
        self.render_ui()

    def render_ui(self):
        # 1. Sidebar (Trái)
        self.frame_sidebar = ctk.CTkFrame(self, width=220, fg_color=("white", "#1f2937"), corner_radius=15)
        self.frame_sidebar.pack(side="left", fill="y", padx=20, pady=20)
        
        ctk.CTkLabel(self.frame_sidebar, text="KHO HÀNG", 
                     font=("Segoe UI", 20, "bold"), text_color=("#0984e3", "white")).pack(pady=20)

        # Các Nút Thao Tác
        if self.current_user['role'] == 'admin':
            self.btn_add = self.create_sidebar_button("➕ Thêm Laptop", "#00b894", "#00a884", self.open_add_dialog)
            self.btn_edit = self.create_sidebar_button("✏️ Cập Nhật", "#fdcb6e", "#e1b12c", self.open_edit_popup)
            self.btn_del = self.create_sidebar_button("🗑️ Xóa Laptop", "#ff7675", "#d63031", self.delete_product)
            ToolTip(self.btn_add, "Thêm sản phẩm mới vào kho")
            ToolTip(self.btn_edit, "Sửa thông tin sản phẩm đã chọn")
            ToolTip(self.btn_del, "Xóa vĩnh viễn sản phẩm")
            
        self.btn_reload = self.create_sidebar_button("🔄 Tải Lại", "#2563eb", "#1d4ed8", self.reload_data, text_color="white")
        self.btn_export = self.create_sidebar_button("📤 Xuất Excel", "#16a34a", "#15803d", self.export_excel, text_color="white")
        
        ToolTip(self.btn_reload, "Tải lại danh sách từ cơ sở dữ liệu")
        ToolTip(self.btn_export, "Xuất danh sách sản phẩm ra file Excel")

        # 2. Khu vực Chính
        self.frame_main = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_main.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # --- THANH TÌM KIẾM ---
        self.frame_search = ctk.CTkFrame(self.frame_main, fg_color=("white", "#1f2937"), corner_radius=10)
        self.frame_search.pack(fill="x", pady=(0, 10))
        
        # Container bên trong để căn lề
        inner_search = ctk.CTkFrame(self.frame_search, fg_color="transparent")
        inner_search.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(inner_search, text="🔍 Tìm kiếm:", font=("Arial", 12)).pack(side="left")
        
        self.entry_search = ctk.CTkEntry(inner_search, width=200, placeholder_text="Nhập tên laptop...")
        self.entry_search.pack(side="left", padx=10)
        self.entry_search.bind("<Return>", lambda event: self.perform_search())

        ctk.CTkLabel(inner_search, text="Danh mục:", font=("Arial", 12)).pack(side="left", padx=(10, 5))
        
        # [NOTE] CTkComboBox dùng command thay vì bind
        self.cmb_filter_cat = ctk.CTkComboBox(inner_search, 
                                              values=["Tất cả", "Gaming", "Văn phòng", "Ultrabook", "Macbook"],
                                              state="readonly", width=150,
                                              command=lambda val: self.perform_search())
        self.cmb_filter_cat.set("Tất cả") # Set giá trị mặc định
        self.cmb_filter_cat.pack(side="left", padx=5)

        ctk.CTkButton(inner_search, text="Lọc", fg_color="#6c5ce7", hover_color="#5f27cd", width=80, 
                      command=self.perform_search).pack(side="left", padx=15)

        # --- BẢNG DỮ LIỆU (Vẫn dùng Treeview vì CTK chưa có Table mạnh) ---
        self.frame_table_container = ctk.CTkFrame(self.frame_main, fg_color="transparent")
        self.frame_table_container.pack(fill="both", expand=True)

        # Style cho Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#5891e6", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))

        columns = ("id", "name", "cat", "brand", "price", "stock")
        display_cols = ("name", "cat", "brand", "price", "stock")

        self.tree = ttk.Treeview(self.frame_table_container, columns=columns, show="headings", displaycolumns=display_cols)
        
        self.tree.heading("name", text="Tên Laptop")
        self.tree.heading("cat", text="Danh Mục")
        self.tree.heading("brand", text="Hãng")
        self.tree.heading("price", text="Giá Bán")
        self.tree.heading("stock", text="Tồn Kho")
        
        self.tree.column("name", width=250)
        self.tree.column("price", width=120, anchor="e") 
        self.tree.column("stock", width=80, anchor="center")

        # Layout Grid cho Table và Scrollbar
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        sb_y = ttk.Scrollbar(self.frame_table_container, orient="vertical", command=self.tree.yview)
        sb_y.grid(row=0, column=1, sticky="ns")
        
        sb_x = ttk.Scrollbar(self.frame_table_container, orient="horizontal", command=self.tree.xview)
        sb_x.grid(row=1, column=0, sticky="ew")

        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        
        self.frame_table_container.grid_rowconfigure(0, weight=1)
        self.frame_table_container.grid_columnconfigure(0, weight=1)
        
        self.tree.bind("<Double-1>", self.open_detail_popup)
        
        self.reload_data()

    def create_sidebar_button(self, text, color, hover_color, command, text_color=None):
        # Helper tạo nút sidebar đồng bộ
        btn_args = {
            "text": text,
            "fg_color": color,
            "hover_color": hover_color,
            "font": ("Segoe UI", 13, "bold"),
            "height": 40,
            "corner_radius": 8,
            "command": command
        }
        if text_color:
            btn_args["text_color"] = text_color
            
        btn = ctk.CTkButton(self.frame_sidebar, **btn_args)
        btn.pack(fill="x", pady=8, padx=10)
        return btn

    def perform_search(self):
        keyword = self.entry_search.get()
        cat = self.cmb_filter_cat.get()
        # [LOGIC GIỮ NGUYÊN]
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        results = self.product_service.search_products(keyword, cat)
        for p in results:
            try:
                price_val = float(p[6])
            except (ValueError, TypeError):
                price_val = 0
            formatted_price = "{:,.0f}".format(price_val)
            self.tree.insert("", tk.END, values=(p[0], p[2], p[3], p[4], formatted_price, p[7]))

    def reload_data(self):
        self.entry_search.delete(0, "end")
        self.cmb_filter_cat.set("Tất cả") # CTK dùng set
        self.perform_search()

    # --- POPUP THÊM MỚI (Dùng CTkScrollableFrame thay vì Canvas cũ) ---
    def open_add_dialog(self):
        self.top = ctk.CTkToplevel(self)
        self.top.title("Thêm Laptop Mới")
        self.top.geometry("600x750")
        self.top.grab_set() # Focus vào cửa sổ này
        
        # Header
        header = ctk.CTkFrame(self.top, fg_color="#605d75", corner_radius=0, height=60)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="NHẬP THÔNG TIN LAPTOP", text_color="white", 
                     font=("Segoe UI", 18, "bold")).pack(pady=15)

        # [NÂNG CẤP] Sử dụng CTkScrollableFrame để cuộn form
        self.form_frame = ctk.CTkScrollableFrame(self.top, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Hàm tạo input nhanh
        def create_input(label_text, parent_frame):
            ctk.CTkLabel(parent_frame, text=label_text, font=("Arial", 12, "bold")).pack(anchor="w", pady=(5, 0))
            entry = ctk.CTkEntry(parent_frame, height=35)
            entry.pack(fill="x", pady=(5, 10))
            return entry

        # 1. Cơ bản
        ctk.CTkLabel(self.form_frame, text="1. THÔNG TIN CƠ BẢN", 
                     text_color=("#2d3436", "#dfe6e9"), font=("Segoe UI", 14, "bold")).pack(fill="x", pady=(0, 10), anchor="w")
        
        self.entry_name = create_input("Tên Laptop:", self.form_frame)

        # Hàng chứa Danh mục & Hãng
        row2 = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        row2.pack(fill="x")
        
        f_cat = ctk.CTkFrame(row2, fg_color="transparent")
        f_cat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(f_cat, text="Danh mục:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.cmb_cat = ctk.CTkComboBox(f_cat, values=["Gaming", "Văn phòng", "Ultrabook", "Workstation", "Macbook"])
        self.cmb_cat.pack(fill="x", pady=5)
        
        f_brand = ctk.CTkFrame(row2, fg_color="transparent")
        f_brand.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(f_brand, text="Hãng:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.cmb_brand = ctk.CTkComboBox(f_brand, values=["", "Khác", "Dell", "Asus", "HP", "Apple", "Lenovo", "Acer", "MSI", "LG"])
        self.cmb_brand.pack(fill="x", pady=5)
        self.cmb_brand.set("") # Mặc định để trống

        # Nhà Cung Cấp
        ctk.CTkLabel(self.form_frame, text="Nhà Cung Cấp:", text_color="#0984e3", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        
        suppliers = self.supplier_service.get_all_suppliers()
        sup_names = [s[1] for s in suppliers] if suppliers else ["Chưa có NCC"]
        self.sup_map = {s[1]: s[0] for s in suppliers} 
        
        self.cb_sup = ctk.CTkComboBox(self.form_frame, values=sup_names)
        self.cb_sup.pack(fill="x", pady=5)

        # 2. Giá & Kho
        ctk.CTkLabel(self.form_frame, text="2. GIÁ & KHO", 
                     text_color=("#2d3436", "#dfe6e9"), font=("Segoe UI", 14, "bold")).pack(fill="x", pady=(20, 10), anchor="w")
        
        row3 = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        row3.pack(fill="x")
        
        f_imp = ctk.CTkFrame(row3, fg_color="transparent")
        f_imp.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_import = create_input("Giá Nhập:", f_imp)

        f_price = ctk.CTkFrame(row3, fg_color="transparent")
        f_price.pack(side="left", fill="x", expand=True)
        self.entry_price = create_input("Giá Bán:", f_price)

        self.entry_stock = create_input("Số lượng Tồn kho:", self.form_frame)

        # 3. Thông số
        ctk.CTkLabel(self.form_frame, text="3. CẤU HÌNH CHI TIẾT", 
                     text_color=("#2d3436", "#dfe6e9"), font=("Segoe UI", 14, "bold")).pack(fill="x", pady=(20, 10), anchor="w")
        
        self.entry_cpu = create_input("CPU:", self.form_frame)
        self.entry_ram = create_input("RAM:", self.form_frame)
        self.entry_screen = create_input("Màn hình:", self.form_frame)
        self.entry_hdd = create_input("Ổ cứng:", self.form_frame)
        self.entry_gpu = create_input("VGA:", self.form_frame)
        self.entry_weight = create_input("Trọng lượng:", self.form_frame)
        self.entry_os = create_input("Hệ điều hành:", self.form_frame)
        self.entry_desc = create_input("Mô tả thêm:", self.form_frame)

        ctk.CTkButton(self.form_frame, text="LƯU SẢN PHẨM", fg_color="#00b894", hover_color="#00a884",
                      font=("Segoe UI", 14, "bold"), height=45,
                      command=self.save_product).pack(pady=30, fill="x")

    def save_product(self):
        # [LOGIC GIỮ NGUYÊN]
        try:
            name = self.entry_name.get()
            category = self.cmb_cat.get()
            brand = self.cmb_brand.get()
            im_price = float(self.entry_import.get() or 0) 
            price = float(self.entry_price.get())
            stock = int(self.entry_stock.get() or 0)
            
            sup_id = self.sup_map.get(self.cb_sup.get(), None)

            cpu = self.entry_cpu.get()
            ram = self.entry_ram.get()
            screen = self.entry_screen.get()
            hdd = self.entry_hdd.get()
            gpu = self.entry_gpu.get()
            weight = self.entry_weight.get()
            os_sys = self.entry_os.get()
            desc = self.entry_desc.get()

            if not name:
                messagebox.showwarning("Lỗi", "Tên không được để trống", parent=self.top)
                return

            success = self.product_service.add_product(name, category, brand, sup_id, im_price, price, stock,
                                                   cpu, ram, screen, hdd, gpu, weight, os_sys, desc)
            if success:
                messagebox.showinfo("Thành công", "Đã thêm sản phẩm", parent=self.top)
                self.reload_data()
                self.top.destroy()
            else:
                messagebox.showerror("Lỗi", "Không thể thêm vào CSDL", parent=self.top)
        except ValueError:
            messagebox.showerror("Lỗi", "Giá và số lượng phải là số hợp lệ", parent=self.top)

    def open_edit_popup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần sửa")
            return
        
        item = self.tree.item(selected)
        p_id = item['values'][0]
        product = self.product_service.get_product_by_id(p_id)
        if not product:
            return
            
        self.open_add_dialog()
        self.top.title("Cập Nhật Laptop")
        
        # Điền dữ liệu cũ
        self.entry_name.insert(0, product[2])
        self.cmb_cat.set(product[3])
        self.cmb_brand.set(product[4])
        
        sup_id = product[1]
        if sup_id:
            for name, sid in self.sup_map.items():
                if sid == sup_id:
                    self.cb_sup.set(name)
                    break
                    
        self.entry_import.insert(0, str(product[5]))
        self.entry_price.insert(0, str(product[6]))
        self.entry_stock.insert(0, str(product[7]))
        
        self.entry_cpu.insert(0, product[8] or "")
        self.entry_ram.insert(0, product[9] or "")
        try:
            self.entry_screen.insert(0, product[10] or "")
            self.entry_hdd.insert(0, product[11] or "")
            self.entry_gpu.insert(0, product[12] or "")
            self.entry_weight.insert(0, product[13] or "")
            self.entry_os.insert(0, product[14] or "")
            self.entry_desc.insert(0, product[15] or "")
        except IndexError:
            pass

        # Ghi đè nút Lưu
        for widget in self.form_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "LƯU SẢN PHẨM":
                widget.configure(text="CẬP NHẬT SẢN PHẨM", command=lambda: self.update_product(p_id))
                break

    def update_product(self, p_id):
        try:
            name = self.entry_name.get()
            category = self.cmb_cat.get()
            brand = self.cmb_brand.get()
            im_price = float(self.entry_import.get() or 0) 
            price = float(self.entry_price.get())
            stock = int(self.entry_stock.get() or 0)
            
            sup_id = self.sup_map.get(self.cb_sup.get(), None)

            cpu = self.entry_cpu.get()
            ram = self.entry_ram.get()
            screen = self.entry_screen.get()
            hdd = self.entry_hdd.get()
            gpu = self.entry_gpu.get()
            weight = self.entry_weight.get()
            os_sys = self.entry_os.get()
            desc = self.entry_desc.get()

            if not name:
                messagebox.showwarning("Lỗi", "Tên không được để trống", parent=self.top)
                return

            success = self.product_service.update_product(p_id, name, category, brand, sup_id, im_price, price, stock,
                                                   cpu, ram, screen, hdd, gpu, weight, os_sys, desc)
            if success:
                messagebox.showinfo("Thành công", "Đã cập nhật sản phẩm", parent=self.top)
                self.reload_data()
                self.top.destroy()
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật vào CSDL", parent=self.top)
        except ValueError:
            messagebox.showerror("Lỗi", "Giá và số lượng phải là số hợp lệ", parent=self.top)

    def delete_product(self):
        # [LOGIC GIỮ NGUYÊN]
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần xóa")
            return
        
        item = self.tree.item(selected)
        p_id = item['values'][0] 
        p_name = item['values'][1]
        
        if messagebox.askyesno("Xác nhận", f"Bạn chắc chắn muốn xóa '{p_name}'?"):
            self.product_service.delete_product(p_id)
            self.reload_data()

    def export_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                 filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            products_data = self.product_service.get_all_products()
            success, msg = self.exporter.export_inventory_to_excel(products_data, file_path)
            if success:
                messagebox.showinfo("Thành công", f"Đã xuất file tại:\n{file_path}")
            else:
                messagebox.showerror("Lỗi", msg)

    # --- POPUP CHI TIẾT ---
    def open_detail_popup(self, event):
        selected = self.tree.selection()
        if not selected: return
        
        item = self.tree.item(selected)
        p_id = item['values'][0]
        product = self.product_service.get_product_by_id(p_id)
        if not product: return

        top = ctk.CTkToplevel(self)
        top.title("Chi Tiết Sản Phẩm")
        top.geometry("450x650")
        top.grab_set()
        
        ctk.CTkLabel(top, text=product[2], font=("Segoe UI", 18, "bold"), wraplength=400).pack(pady=15)
        
        info_frame = ctk.CTkFrame(top, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=20)

        def add_row(label, value, color=None):
            f = ctk.CTkFrame(info_frame, fg_color="transparent", height=30)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=label, font=("Arial", 12, "bold"), width=100, anchor="w").pack(side="left")
            
            val = str(value) if value else "..."
            lbl_val = ctk.CTkLabel(f, text=val, font=("Arial", 12), wraplength=250, anchor="w")
            if color: lbl_val.configure(text_color=color)
            lbl_val.pack(side="left", fill="x", expand=True)
            
            # Kẻ đường mờ
            ctk.CTkFrame(info_frame, height=1, fg_color="gray80").pack(fill="x", pady=2)

        add_row("Danh mục:", product[3])
        add_row("Hãng:", product[4])
        add_row("CPU:", product[8]) 
        add_row("RAM:", product[9]) 
        
        try:
            add_row("Màn hình:", product[10])
            add_row("Ổ cứng:", product[11])
            add_row("VGA:", product[12])
        except IndexError: pass

        add_row("Giá nhập:", "{:,.0f} VNĐ".format(product[5]), color="gray")
        add_row("Giá bán:", "{:,.0f} VNĐ".format(product[6]), color="#e74c3c")
        add_row("Tồn kho:", f"{product[7]} chiếc", color="#27ae60")

        ctk.CTkButton(top, text="Đóng", command=top.destroy, 
                      fg_color="gray", hover_color="gray40", width=100).pack(pady=20)