import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from gui.components.tooltip import ToolTip

class PosTab(ctk.CTkFrame): # Kế thừa CTkFrame
    def __init__(self, parent, product_service, order_service, promotion_service, exporter, current_user, customer_service=None):
        super().__init__(parent, fg_color="transparent")
        self.product_service = product_service
        self.order_service = order_service
        self.promotion_service = promotion_service 
        self.exporter = exporter
        self.customer_service = customer_service
        
        self.current_applied_voucher = None
        self.current_user_id = current_user['id'] if current_user else 1

        # --- LAYOUT CHÍNH (GRID 2 CỘT) ---
        self.grid_columnconfigure(0, weight=6) # Cột trái (DS Sản phẩm) chiếm 6 phần
        self.grid_columnconfigure(1, weight=4) # Cột phải (Giỏ hàng) chiếm 4 phần
        self.grid_rowconfigure(0, weight=1)

        # 1. KHUNG TRÁI: DANH SÁCH SẢN PHẨM
        self.frame_left = ctk.CTkFrame(self, fg_color=("white", "#1f2937"), corner_radius=10)
        self.frame_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        # Header Tìm kiếm
        search_frame = ctk.CTkFrame(self.frame_left, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(search_frame, text="🔍 Tìm SP:", font=("Arial", 12, "bold")).pack(side="left")
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Nhập tên sản phẩm...", height=35)
        self.entry_search.pack(side="left", fill="x", expand=True, padx=10)
        self.entry_search.bind("<Return>", self.search_product)
        
        btn_search = ctk.CTkButton(search_frame, text="Tìm", width=80, height=35, fg_color="#0984e3", 
                      command=self.search_product)
        btn_search.pack(side="left")
        ToolTip(btn_search, "Tìm kiếm sản phẩm theo tên")

        # Bảng sản phẩm (Table Container)
        table_container = ctk.CTkFrame(self.frame_left, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Treeview Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#0984e3", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=30)
        
        columns = ("id", "name", "price", "stock")
        self.tree_products = ttk.Treeview(table_container, columns=columns, show="headings")
        self.tree_products.heading("id", text="ID")
        self.tree_products.heading("name", text="Tên Sản Phẩm")
        self.tree_products.heading("price", text="Giá Bán")
        self.tree_products.heading("stock", text="Tồn")
        
        self.tree_products.column("id", width=40, anchor="center")
        self.tree_products.column("price", width=120, anchor="e")
        self.tree_products.column("stock", width=60, anchor="center")
        
        self.tree_products.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree_products.yview)
        sb.pack(side="right", fill="y")
        self.tree_products.configure(yscroll=sb.set)
        
        self.tree_products.bind("<Double-1>", self.add_to_cart)

        # 2. KHUNG PHẢI: GIỎ HÀNG (BILL)
        self.frame_right = ctk.CTkFrame(self, fg_color=("gray95", "#2b2b2b"), corner_radius=10)
        self.frame_right.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Header Giỏ hàng
        ctk.CTkLabel(self.frame_right, text="🛒 GIỎ HÀNG", 
                     font=("Segoe UI", 16, "bold")).pack(pady=15)

        # Bảng Giỏ hàng
        cart_frame = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        cart_frame.pack(fill="both", expand=True, padx=15)
        
        cart_cols = ("id", "name", "qty", "total")
        self.tree_cart = ttk.Treeview(cart_frame, columns=cart_cols, show="headings", height=15)
        self.tree_cart.heading("id", text="ID")
        self.tree_cart.heading("name", text="Tên SP")
        self.tree_cart.heading("qty", text="SL")
        self.tree_cart.heading("total", text="Thành tiền")
        
        self.tree_cart.column("id", width=30)
        self.tree_cart.column("qty", width=40, anchor="center")
        self.tree_cart.column("total", width=100, anchor="e")
        
        self.tree_cart.pack(fill="both", expand=True)

        # Nút chức năng giỏ hàng
        btn_box = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        btn_box.pack(fill="x", padx=15, pady=10)
        
        btn_remove = ctk.CTkButton(btn_box, text="❌ Xóa món", width=100, fg_color="#fab1a0", hover_color="#e17055", text_color="black",
                      command=self.remove_item)
        btn_remove.pack(side="left")
        ToolTip(btn_remove, "Xóa sản phẩm đã chọn khỏi giỏ hàng")
        
        btn_clear = ctk.CTkButton(btn_box, text="🗑️ Xóa hết", width=100, fg_color="#ff7675", hover_color="#d63031",
                      command=self.clear_cart)
        btn_clear.pack(side="right")
        ToolTip(btn_clear, "Làm trống toàn bộ giỏ hàng")

        # Footer Tổng tiền & Thanh toán
        footer = ctk.CTkFrame(self.frame_right, fg_color=("white", "#374151"), corner_radius=10)
        footer.pack(fill="x", padx=15, pady=15, side="bottom")
        
        self.lbl_preview_total = ctk.CTkLabel(footer, text="Tạm tính: 0 VNĐ", 
                                              font=("Arial", 16, "bold"), text_color=("#2d3436", "white"))
        self.lbl_preview_total.pack(pady=15, padx=15, anchor="e")
        
        btn_checkout = ctk.CTkButton(footer, text="➡ TIẾN HÀNH THANH TOÁN", height=70, 
                      fg_color="#00b894", hover_color="#00a884",
                      font=("Segoe UI", 14, "bold"), 
                      command=self.open_checkout_dialog)
        btn_checkout.pack(fill="x", padx=5, pady=(0, 10), side="bottom")
        ToolTip(btn_checkout, "Chuyển sang bước thanh toán đơn hàng")

        self.load_products()

    # --- LOGIC QUẢN LÝ (GIỮ NGUYÊN) ---
    def load_products(self, keyword=None):
        for i in self.tree_products.get_children(): self.tree_products.delete(i)
        products = self.product_service.get_all_products()
        for p in products:
            if p[7] > 0: 
                if keyword and keyword.lower() not in p[2].lower(): continue
                price = "{:,.0f}".format(p[6])
                self.tree_products.insert("", "end", values=(p[0], p[2], price, p[7]))

    def search_product(self, event=None):
        self.load_products(self.entry_search.get())

    def add_product_by_id(self, p_id):
        success, msg = self.order_service.add_to_cart(p_id, 1)
        if not success:
            messagebox.showwarning("Cảnh báo", msg)
        self.update_cart_ui()

    def add_to_cart(self, event):
        sel = self.tree_products.selection()
        if not sel: return
        item = self.tree_products.item(sel)
        p_id = item['values'][0]
        self.add_product_by_id(p_id)

    def remove_item(self):
        sel = self.tree_cart.selection()
        if not sel: return
        p_id = self.tree_cart.item(sel)['values'][0]
        self.order_service.remove_from_cart(p_id)
        self.update_cart_ui()

    def clear_cart(self):
        self.order_service.clear_cart()
        self.update_cart_ui()

    def update_cart_ui(self):
        for i in self.tree_cart.get_children(): self.tree_cart.delete(i)
        
        cart = self.order_service.get_cart()
        for c in cart.items.values():
            price_fmt = "{:,.0f}".format(c.total)
            self.tree_cart.insert("", "end", values=(c.product_id, c.name, c.qty, price_fmt))
        
        self.lbl_preview_total.configure(text=f"Tạm tính: {cart.cart_total:,.0f} VNĐ")

    def open_checkout_dialog(self):
        cart = self.order_service.get_cart()
        if not cart.items:
            messagebox.showwarning("Giỏ hàng trống", "Vui lòng chọn sản phẩm trước!")
            return

        self.checkout_win = ctk.CTkToplevel(self)
        self.checkout_win.title("Thanh Toán Đơn Hàng")
        self.checkout_win.geometry("500x680")
        self.checkout_win.grab_set()

        # Header
        header = ctk.CTkFrame(self.checkout_win, fg_color="#00b894", height=60, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="XÁC NHẬN THANH TOÁN", text_color="white", 
                     font=("Segoe UI", 18, "bold")).pack(pady=15)

        content = ctk.CTkFrame(self.checkout_win, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)

        # 1. Thông tin khách
        ctk.CTkLabel(content, text="Số điện thoại khách (tùy chọn):", font=("Arial", 12, "bold")).pack(anchor="w")
        self.entry_checkout_phone = ctk.CTkEntry(content, height=40)
        self.entry_checkout_phone.pack(fill="x", pady=(5, 15))

        # 2. Mã Voucher
        ctk.CTkLabel(content, text="Mã giảm giá (Voucher):", font=("Arial", 12, "bold")).pack(anchor="w")
        
        f_voucher = ctk.CTkFrame(content, fg_color="transparent")
        f_voucher.pack(fill="x", pady=(5, 15))
        
        self.entry_checkout_voucher = ctk.CTkEntry(f_voucher, height=40, placeholder_text="Nhập mã...")
        self.entry_checkout_voucher.pack(side="left", fill="x", expand=True)
        
        btn_apply = ctk.CTkButton(f_voucher, text="Áp dụng", width=80, height=40, fg_color="#6c5ce7", 
                      command=self.apply_voucher_logic)
        btn_apply.pack(side="right", padx=(10, 0))
        ToolTip(btn_apply, "Áp dụng mã giảm giá cho đơn hàng")

        # 3. Tổng kết (Frame riêng biệt nổi bật)
        summary_frame = ctk.CTkFrame(content, fg_color=("gray90", "gray25"), corner_radius=10)
        summary_frame.pack(fill="x", pady=20)
        
        inner_sum = ctk.CTkFrame(summary_frame, fg_color="transparent")
        inner_sum.pack(fill="x", padx=20, pady=20)

        self.lbl_chk_subtotal = ctk.CTkLabel(inner_sum, text=f"Tiền hàng: {cart.cart_total:,.0f} VNĐ", anchor="e")
        self.lbl_chk_subtotal.pack(fill="x")
        
        self.lbl_chk_discount = ctk.CTkLabel(inner_sum, text=f"Giảm giá: -{cart.discount_amount:,.0f} VNĐ", text_color="red", anchor="e")
        self.lbl_chk_discount.pack(fill="x")
        
        ctk.CTkFrame(inner_sum, height=2, fg_color="gray").pack(fill="x", pady=10)
        
        self.lbl_chk_final = ctk.CTkLabel(inner_sum, text=f"{cart.final_total:,.0f} VNĐ", 
                                          text_color=("#2d3436", "white"), font=("Arial", 24, "bold"), anchor="e")
        self.lbl_chk_final.pack(fill="x")

        # 4. Nút Xác Nhận
        btn_confirm = ctk.CTkButton(content, text="💸 XÁC NHẬN & IN HÓA ĐƠN", height=50, 
                      fg_color="#00b894", hover_color="#00a884", font=("Segoe UI", 14, "bold"),
                      command=self.process_final_payment)
        btn_confirm.pack(fill="x", side="bottom")
        ToolTip(btn_confirm, "Hoàn tất thanh toán và in hóa đơn")

    def apply_voucher_logic(self):
        code = self.entry_checkout_voucher.get().strip()
        success, msg = self.order_service.apply_voucher(code)
        
        if success:
            messagebox.showinfo("Thành công", f"Đã áp dụng mã {code}!\nGiảm: {msg:,.0f} đ")
        else:
            messagebox.showerror("Lỗi", msg)
        
        # Cập nhật UI
        cart = self.order_service.get_cart()
        self.lbl_chk_discount.configure(text=f"Giảm giá: -{cart.discount_amount:,.0f} VNĐ")
        self.lbl_chk_final.configure(text=f"{cart.final_total:,.0f} VNĐ")

    def process_final_payment(self):
        phone = self.entry_checkout_phone.get().strip()
        if not phone:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập số điện thoại khách hàng!", parent=self.checkout_win)
            return
            
        customer_id = None
        if self.customer_service:
            customer_id = self.customer_service.get_or_create_customer_by_phone(phone)
            
        cart_snapshot = self.order_service.get_cart().get_items_as_dict_list()
        final_total = self.order_service.get_cart().final_total

        if messagebox.askyesno("Xác nhận", "Hoàn tất giao dịch này?"):
            success, msg = self.order_service.checkout(self.current_user_id, customer_id)
            
            if success:
                try: 
                    order_id = msg.split(": ")[1]
                except (ValueError, IndexError): 
                    order_id = "NEW"
                
                if messagebox.askyesno("In hóa đơn", "Bạn có muốn xuất file PDF không?"):
                    f_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Bill_{order_id}.pdf")
                    if f_path:
                        c_name = f"SĐT: {phone}" if phone else "Khách vãng lai"
                        self.exporter.print_invoice_pdf(order_id, c_name, cart_snapshot, final_total, f_path)
                
                self.checkout_win.destroy()
                self.update_cart_ui()
                self.load_products() 
                messagebox.showinfo("Hoàn tất", "Giao dịch thành công!")
            else:
                messagebox.showerror("Lỗi Thanh Toán", msg)