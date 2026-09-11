import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk 
from gui.components.tooltip import ToolTip

class HomeTab(ctk.CTkFrame):
    def __init__(self, parent, product_service, order_service, promotion_service, current_user, on_buy_click):
        super().__init__(parent, fg_color="transparent")
        self.product_service = product_service
        self.order_service = order_service
        self.promotion_service = promotion_service
        self.current_user = current_user
        self.on_buy_click = on_buy_click
        
        self.cart = [] 
        self.current_voucher = None 
        self.banner_timer = None
        
        # Biến phân trang
        self.all_products = []
        self.current_page = 1
        self.items_per_page = 10 
        
        # --- GIAO DIỆN CHÍNH ---
        self.render_header_area()
        self.render_banner()       # Sẽ thành Auto-Carousel
        self.render_categories()   # THÊM MỚI: Tab danh mục cuộn ngang
        self.render_filter_bar()

        ctk.CTkLabel(self, text="KẾT QUẢ TÌM KIẾM", 
                     text_color=("#2d3436", "white"),
                     font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=30, pady=(10, 5))

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.pagination_frame.pack(fill="x", pady=(0, 20))

        self.apply_filters()

    # --- [CẬP NHẬT] KHU VỰC HEADER: THÊM NÚT CSKH ---
    def render_header_area(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=30, pady=10)
        
        # 1. Nút Giỏ hàng (Bên phải cùng)
        self.btn_cart = ctk.CTkButton(header, text="🛒 Giỏ hàng (0)", 
                                      fg_color="#d63031", hover_color="#c0392b",
                                      font=("Segoe UI", 13, "bold"), 
                                      height=35, corner_radius=15,
                                      command=self.open_cart_popup)
        self.btn_cart.pack(side="right")

        # 2. [MỚI] Nút Chăm sóc khách hàng (Bên cạnh giỏ hàng)
        btn_support = ctk.CTkButton(header, text="🎧 CSKH", 
                                    fg_color="#0984e3", hover_color="#00cec9",
                                    font=("Segoe UI", 13, "bold"),
                                    height=35, corner_radius=15, width=100,
                                    command=self.open_customer_care)
        btn_support.pack(side="right", padx=10)

    # --- [MỚI] CÁC HÀM XỬ LÝ CHĂM SÓC KHÁCH HÀNG ---
    def open_customer_care(self):
        # Tạo cửa sổ Popup CSKH
        top = ctk.CTkToplevel(self)
        top.title("Trung Tâm Chăm Sóc Khách Hàng")
        top.geometry("600x400")
        top.grab_set() # Focus vào cửa sổ này
        
        # Header Popup
        ctk.CTkLabel(top, text="👋 CHÚNG TÔI CÓ THỂ GIÚP GÌ CHO BẠN?", 
                     font=("Segoe UI", 18, "bold"), text_color="#0984e3").pack(pady=20)

        # Container chứa 3 nút dịch vụ
        grid_frame = ctk.CTkFrame(top, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tạo 3 cột đều nhau
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)

        # === 1. DỊCH VỤ VỆ SINH ===
        btn_clean = self.create_service_card(grid_frame, "🧹\nDịch vụ Vệ Sinh", 
                                             "Làm sạch laptop,\ntra keo tản nhiệt", 
                                             "#00b894", 0, 
                                             lambda: self.show_branch_msg("Vệ Sinh Laptop"))

        # === 2. DỊCH VỤ PHẦN MỀM ===
        btn_soft = self.create_service_card(grid_frame, "💿\nDịch vụ Phần Mềm", 
                                            "Cài Office, Windows,\nDiệt Virus", 
                                            "#6c5ce7", 1, 
                                            self.show_software_popup)

        # === 3. ĐỔI TRẢ ===
        btn_return = self.create_service_card(grid_frame, "🔄\nĐổi Trả / Bảo Hành", 
                                              "Đổi mới trong 30 ngày\nnếu lỗi NSX", 
                                              "#e17055", 2, 
                                              lambda: self.show_branch_msg("Đổi Trả & Bảo Hành"))
        
        # Footer
        ctk.CTkLabel(top, text="Hotline hỗ trợ: 1900 1000 (8:00 - 22:00)", text_color="gray").pack(side="bottom", pady=20)

    def create_service_card(self, parent, title, subtext, color, col_idx, command):
        # Hàm hỗ trợ tạo thẻ dịch vụ đẹp
        card = ctk.CTkButton(parent, text=f"{title}\n\n{subtext}", 
                             font=("Segoe UI", 14, "bold"),
                             fg_color=color, hover_color=color, # Giữ nguyên màu hoặc làm tối đi tí
                             corner_radius=15,
                             width=160, height=200,
                             command=command)
        card.grid(row=0, column=col_idx, padx=10, sticky="nsew")
        return card

    def show_branch_msg(self, service_name):
        # Popup thông báo ra chi nhánh
        messagebox.showinfo(f"{service_name}", 
                            f"Đối với dịch vụ {service_name}, quý khách vui lòng mang máy đến chi nhánh gần nhất để được kỹ thuật viên hỗ trợ trực tiếp.\n\nXin cảm ơn!")

    def show_software_popup(self):
        # Popup riêng cho Phần mềm
        soft_win = ctk.CTkToplevel(self)
        soft_win.title("Dịch Vụ Phần Mềm")
        soft_win.geometry("400x300")
        soft_win.grab_set()
        
        ctk.CTkLabel(soft_win, text="GÓI DỊCH VỤ PHẦN MỀM", font=("Segoe UI", 16, "bold")).pack(pady=20)
        
        # Frame chứa danh sách
        content = ctk.CTkFrame(soft_win, fg_color=("white", "#2b2b2b"), corner_radius=10)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Mục 1
        row1 = ctk.CTkFrame(content, fg_color="transparent")
        row1.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(row1, text="🟦 Microsoft Office 365/2021", font=("Arial", 12, "bold")).pack(anchor="w")
        ctk.CTkLabel(row1, text="   (Word, Excel, PowerPoint...)", font=("Arial", 11)).pack(anchor="w")
        
        # Mục 2
        row2 = ctk.CTkFrame(content, fg_color="transparent")
        row2.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(row2, text="🪟 Windows 10/11 Bản Quyền", font=("Arial", 12, "bold")).pack(anchor="w")
        ctk.CTkLabel(row2, text="   (Home, Pro, Edu...)", font=("Arial", 11)).pack(anchor="w")
        
        # Nút liên hệ Admin
        ctk.CTkButton(soft_win, text="📞 Liên hệ Admin để kích hoạt", 
                      fg_color="#0984e3", font=("Segoe UI", 12, "bold"),
                      command=lambda: messagebox.showinfo("Liên hệ", "Vui lòng liên hệ Admin qua Zalo/SĐT: 099.999.9999 để được cài đặt từ xa (UltraView/TeamView).")).pack(pady=10)

    def render_banner(self):
        # Banner dùng Frame màu tím
        self.banner = ctk.CTkFrame(self, fg_color="#6c5ce7", corner_radius=10, height=120)
        self.banner.pack(fill="x", padx=20, pady=(0, 20))
        self.banner.pack_propagate(False) 
        
        self.lbl_banner_title = ctk.CTkLabel(self.banner, text="SĂN SALE ĐÓN TẾT!", text_color="white", 
                                             font=("Montserrat", 24, "bold"))
        self.lbl_banner_title.place(x=30, y=20)
        
        self.lbl_banner_promo = ctk.CTkLabel(self.banner, text="🔥 Ưu đãi cực sốc", 
                                             text_color="#ffeaa7", font=("Segoe UI", 14, "bold"))
        self.lbl_banner_promo.place(x=30, y=65)
        
        # Thiết lập danh sách các banner để auto-rotate
        self.banner_slides = [
            {"bg": "#6c5ce7", "title": "SĂN SALE ĐÓN TẾT!", "promo": "🔥 Giảm đến 50% các dòng Laptop Gaming"},
            {"bg": "#0984e3", "title": "BACK TO SCHOOL", "promo": "🎓 Trợ giá HSSV - Tặng balo & chuột không dây"},
            {"bg": "#d63031", "title": "FLASH SALE CUỐI TUẦN", "promo": "⚡ Mua 1 tặng 1 phụ kiện cao cấp"}
        ]
        self.current_slide = 0
        
        # Thêm 2 nút điều hướng thủ công cho banner
        ctk.CTkButton(self.banner, text="<", width=30, fg_color="transparent", hover_color="#2d3436",
                      command=self.prev_slide).place(relx=0.01, rely=0.4)
        ctk.CTkButton(self.banner, text=">", width=30, fg_color="transparent", hover_color="#2d3436",
                      command=self.next_slide).place(relx=0.96, rely=0.4)

        # Chạy auto carousel
        self.rotate_banner()

    def update_banner_ui(self):
        slide = self.banner_slides[self.current_slide]
        self.banner.configure(fg_color=slide["bg"])
        self.lbl_banner_title.configure(text=slide["title"])
        self.lbl_banner_promo.configure(text=slide["promo"])

    def next_slide(self):
        self.current_slide = (self.current_slide + 1) % len(self.banner_slides)
        self.update_banner_ui()

    def prev_slide(self):
        self.current_slide = (self.current_slide - 1) % len(self.banner_slides)
        self.update_banner_ui()

    def rotate_banner(self):
        if self.winfo_ismapped():
            self.next_slide()
        # Chuyển slide mỗi 4 giây
        self.banner_timer = self.after(4000, self.rotate_banner)

    def destroy(self):
        if getattr(self, 'banner_timer', None):
            self.after_cancel(self.banner_timer)
        super().destroy()

    # --- TÍNH NĂNG MỚI: DANH MỤC CUỘN NGANG ---
    def render_categories(self):
        cat_wrapper = ctk.CTkFrame(self, fg_color="transparent", height=100)
        cat_wrapper.pack(fill="x", padx=20, pady=(0, 20))
        
        # Nút cuộn trái
        btn_left = ctk.CTkButton(cat_wrapper, text="<", width=30, height=80, fg_color="#f5f5f5", 
                                 text_color="black", hover_color="#dfe6e9", font=("Arial", 16, "bold"),
                                 command=lambda: self.scroll_categories(-1))
        btn_left.pack(side="left", padx=(0, 5))
        
        # Khung cuộn ngang (ScrollableFrame với orientation="horizontal")
        # CustomTkinter hỗ trợ orientation="horizontal"
        self.cat_scroll = ctk.CTkScrollableFrame(cat_wrapper, orientation="horizontal", height=100, 
                                                 fg_color="transparent")
        self.cat_scroll.pack(side="left", fill="x", expand=True)
        
        # Nút cuộn phải
        btn_right = ctk.CTkButton(cat_wrapper, text=">", width=30, height=80, fg_color="#f5f5f5", 
                                  text_color="black", hover_color="#dfe6e9", font=("Arial", 16, "bold"),
                                  command=lambda: self.scroll_categories(1))
        btn_right.pack(side="right", padx=(5, 0))

        categories = self.product_service.get_all_categories()
        
        # Nút Tất cả
        self.create_category_icon("Tất cả", "🌐")
        
        icons = ["💻", "🎮", "💼", "🖥️", "🍎", "⚡"]
        for i, cat in enumerate(categories):
            icon = icons[i % len(icons)]
            self.create_category_icon(cat, icon)

    def scroll_categories(self, direction):
        # Truy cập vào canvas bên trong CTkScrollableFrame để cuộn ngang
        try:
            self.cat_scroll._parent_canvas.xview_scroll(direction, "units")
        except Exception:
            pass # Bỏ qua nếu lỗi thuộc tính

    def create_category_icon(self, name, icon):
        # Tạo một nút vuông trông giống icon Shopee
        btn = ctk.CTkButton(self.cat_scroll, text=f"{icon}\n{name}", 
                            width=100, height=80, fg_color="white", text_color="black",
                            hover_color="#e3f2fd", border_width=1, border_color="#dfe6e9",
                            corner_radius=10, font=("Segoe UI", 13, "bold"),
                            command=lambda n=name: self.filter_by_category(n))
        btn.pack(side="left", padx=10, pady=5)

    def filter_by_category(self, cat_name):
        # Tự động cập nhật combobox và gọi hàm lọc
        if cat_name == "Tất cả":
            self.cb_cat.set("Danh mục: Tất cả")
        else:
            self.cb_cat.set(f"Danh mục: {cat_name}")
        self.apply_filters()

    def render_filter_bar(self):
        bar = ctk.CTkFrame(self, fg_color=("white", "#1f2937"), corner_radius=10)
        bar.pack(fill="x", padx=20, pady=(0, 10))
        
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(padx=15, pady=10, fill="x")
        
        ctk.CTkLabel(inner, text="🔍 Tìm tên:", font=("Arial", 12)).pack(side="left", padx=(0, 5))
        
        self.entry_keyword = ctk.CTkEntry(inner, placeholder_text="Nhập tên laptop...", width=200)
        self.entry_keyword.pack(side="left", padx=(0, 15))
        self.entry_keyword.bind("<Return>", lambda e: self.apply_filters())

        def add_cb(values, attr):
            cb = ctk.CTkComboBox(inner, values=values, state="readonly", width=140,
                                 command=lambda val: self.apply_filters())
            cb.set(values[0]) 
            cb.pack(side="left", padx=5)
            setattr(self, attr, cb)

        add_cb(["Danh mục: Tất cả"] + self.product_service.get_all_categories(), "cb_cat")
        add_cb(["Hãng: Tất cả"] + self.product_service.get_all_brands(), "cb_brand")
        add_cb(["Giá: Tất cả", "< 10 Triệu", "10 - 20 Triệu", "20 - 30 Triệu", "> 30 Triệu"], "cb_price")
        
        ctk.CTkButton(inner, text="Lọc ngay", fg_color="#0984e3", hover_color="#00cec9", 
                      width=100, command=self.apply_filters).pack(side="left", padx=15)

    def apply_filters(self):
        kw = self.entry_keyword.get()
        cat = self.cb_cat.get().replace("Danh mục: ", "")
        brand = self.cb_brand.get().replace("Hãng: ", "")
        price = self.cb_price.get().replace("Giá: ", "")
        
        self.all_products = self.product_service.filter_products(category=cat, brand=brand, price_range=price, keyword=kw)
        self.current_page = 1
        self.render_page()
        
    def render_page(self):
        for w in self.scrollable_frame.winfo_children(): w.destroy()
        for w in self.pagination_frame.winfo_children(): w.destroy()
        
        if not self.all_products:
            ctk.CTkLabel(self.scrollable_frame, text="Không tìm thấy sản phẩm nào!", 
                         text_color="red", font=("Arial", 14)).pack(pady=40)
            return

        total_items = len(self.all_products)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_products = self.all_products[start_idx:end_idx]

        cols = 5 
        for i, p in enumerate(page_products):
            self.create_product_card(p, i // cols, i % cols)
            
        # Vẽ nút phân trang
        self.render_pagination_controls(total_pages)

    def render_pagination_controls(self, total_pages):
        # Canh giữa các nút phân trang
        inner_frame = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        inner_frame.pack(anchor="center")
        
        # Nút Prev
        btn_prev = ctk.CTkButton(inner_frame, text="<", width=40, height=40,
                                 state="normal" if self.current_page > 1 else "disabled",
                                 command=lambda: self.change_page(-1))
        btn_prev.pack(side="left", padx=5)
        
        # Nút số trang
        for page in range(1, total_pages + 1):
            btn = ctk.CTkButton(inner_frame, text=str(page), width=40, height=40,
                                fg_color="#0288d1" if page == self.current_page else "gray",
                                command=lambda p=page: self.go_to_page(p))
            btn.pack(side="left", padx=2)
            
        # Nút Next
        btn_next = ctk.CTkButton(inner_frame, text=">", width=40, height=40,
                                 state="normal" if self.current_page < total_pages else "disabled",
                                 command=lambda: self.change_page(1))
        btn_next.pack(side="left", padx=5)

    def change_page(self, delta):
        self.current_page += delta
        self.render_page()
        
    def go_to_page(self, page):
        self.current_page = page
        self.render_page()

    def create_product_card(self, p, row, col):
        card = ctk.CTkFrame(self.scrollable_frame, width=220, height=280, 
                            fg_color="#ffffff", # Nền trắng
                            border_width=1, border_color="#e0e0e0", corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10)
        card.grid_propagate(False) 

        brand_colors = {"Dell": "#74b9ff", "Asus": "#ff7675", "Apple": "#b2bec3", "HP": "#55efc4", "Acer": "#a29bfe"}
        bg_c = brand_colors.get(p[4], "#a29bfe")
        
        # Phần Header của Card (Thương hiệu / Hình ảnh minh họa)
        header_card = ctk.CTkLabel(card, text=p[4], fg_color=bg_c, text_color="white", 
                                   font=("Arial", 16, "bold"), width=218, height=100, corner_radius=8)
        header_card.place(x=1, y=1) 

        # Tên sản phẩm
        ctk.CTkLabel(card, text=p[2], font=("Segoe UI", 12, "bold"), text_color="#2d3436",
                     wraplength=190, anchor="n", 
                     width=200, height=50).place(x=10, y=110) 
        
        # Giá tiền (Nổi bật hơn chuẩn e-commerce)
        ctk.CTkLabel(card, text="{:,.0f} đ".format(p[6]), text_color="#e17055", 
                     font=("Consolas", 18, "bold"), 
                     width=200, anchor="w").place(x=10, y=180) 
                     
        # Chip cấu hình thu gọn
        ctk.CTkLabel(card, text=f"RAM: {p[9]} | Ổ cứng: {p[11] if len(p)>11 else 'N/A'}", 
                     text_color="gray", font=("Arial", 10), width=200, anchor="w").place(x=10, y=210)

        # --- NÂNG CẤP CHUẨN THƯƠNG MẠI: HOVER EFFECTS ---
        def on_enter(e):
            card.configure(border_color="#0984e3", border_width=2) # Đổi viền xanh đậm
            # Có thể đổi nền nhẹ
        def on_leave(e):
            card.configure(border_color="#e0e0e0", border_width=1)
            
        # Bind sự kiện cho card và TẤT CẢ các widget bên trong nó
        for w in card.winfo_children() + [card]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", lambda e, pid=p[0]: self.show_detail_popup(pid))

    # --- CÁC HÀM KHÁC (Popup, Cart...) GIỮ NGUYÊN NHƯ CŨ ---
    # Bạn copy lại phần popup chi tiết, giỏ hàng, checkout từ code trước đó vào đây nhé
    # (Do code quá dài nên mình chỉ focus vào phần thay đổi ở trên)
    
    # ... (Copy phần show_detail_popup, add_item_to_cart, open_cart_popup...)
    
    # Để code chạy được, bạn cần đảm bảo giữ lại các hàm cũ bên dưới này:
    def show_detail_popup(self, p_id):
        product = self.product_service.get_product_by_id(p_id)
        if not product: return
        top = ctk.CTkToplevel(self)
        top.title(product[2])
        top.geometry("700x600")
        top.grab_set()
        
        ctk.CTkLabel(top, text=product[2], font=("Segoe UI", 20, "bold"), wraplength=650).pack(pady=15)
        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20)
        left = ctk.CTkFrame(body, fg_color=("gray95", "gray20"), corner_radius=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        def val(v): return str(v) if v and v != "None" else "Đang cập nhật"
        specs = [("Hãng SX", val(product[4])), ("CPU", val(product[8])), ("RAM", val(product[9])), ("Màn hình", val(product[10]) if len(product)>10 else ""), ("Ổ cứng", val(product[11]) if len(product)>11 else ""), ("VGA", val(product[12]) if len(product)>12 else "")]
        for i, (k, v) in enumerate(specs):
            row = ctk.CTkFrame(left, fg_color="transparent", height=30)
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=k+":", width=80, anchor="w", font=("Arial", 12, "bold"), text_color="gray").pack(side="left")
            ctk.CTkLabel(row, text=v, font=("Arial", 12), wraplength=200, anchor="w").pack(side="left", fill="x")

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="right", fill="y", pady=10)
        ctk.CTkLabel(right, text="{:,.0f} VNĐ".format(product[6]), text_color="#d63031", font=("Arial", 26, "bold")).pack(pady=(20, 10))
        status = f"✅ Còn hàng ({product[7]})" if product[7] > 0 else "❌ Hết hàng"
        status_color = "#00b894" if product[7] > 0 else "red"
        ctk.CTkLabel(right, text=status, text_color=status_color, font=("Arial", 14)).pack(pady=5)
        btn_add = ctk.CTkButton(right, text="🛒 THÊM VÀO GIỎ", fg_color="#d63031", hover_color="#c0392b", font=("Segoe UI", 14, "bold"), height=45, corner_radius=10, command=lambda: [self.add_item_to_cart(product), top.destroy()])
        btn_add.pack(pady=30, fill="x")
        if product[7] <= 0: btn_add.configure(state="disabled", fg_color="gray")

    def add_item_to_cart(self, product):
        p_id = product[0]; p_name = product[2]; p_price = float(product[6]); p_stock = int(product[7])
        for item in self.cart:
            if item['id'] == p_id:
                if item['qty'] < p_stock:
                    item['qty'] += 1; item['total'] = item['qty'] * p_price
                    messagebox.showinfo("Giỏ hàng", f"Đã tăng số lượng {p_name} lên {item['qty']}")
                else: messagebox.showwarning("Kho", "Đã hết hàng trong kho!")
                self.update_cart_btn(); return
        self.cart.append({'id': p_id, 'name': p_name, 'price': p_price, 'qty': 1, 'total': p_price})
        messagebox.showinfo("Giỏ hàng", f"Đã thêm {p_name} vào giỏ!")
        self.update_cart_btn()

    def update_cart_btn(self):
        count = sum(item['qty'] for item in self.cart)
        self.btn_cart.configure(text=f"🛒 Giỏ hàng ({count})")

    def open_cart_popup(self):
        if not self.cart:
            messagebox.showinfo("Giỏ hàng", "Giỏ hàng đang trống! Hãy mua sắm đi nào.")
            return
        top = ctk.CTkToplevel(self)
        top.title("Giỏ Hàng Của Bạn"); top.geometry("650x650"); top.grab_set()
        ctk.CTkLabel(top, text="ĐƠN HÀNG CỦA BẠN", font=("Segoe UI", 18, "bold")).pack(pady=15)
        tree_frame = ctk.CTkFrame(top, fg_color="transparent"); tree_frame.pack(fill="x", padx=20)
        cols = ("name", "qty", "price", "total")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        tree.heading("name", text="Sản phẩm"); tree.heading("qty", text="SL"); tree.heading("price", text="Đơn giá"); tree.heading("total", text="Thành tiền")
        tree.column("name", width=250); tree.column("qty", width=50, anchor="center"); tree.column("price", width=100, anchor="e"); tree.column("total", width=100, anchor="e")
        tree.pack(fill="x")
        total_bill = 0
        for item in self.cart:
            total_bill += item['total']
            tree.insert("", "end", values=(item['name'], item['qty'], "{:,.0f}".format(item['price']), "{:,.0f}".format(item['total'])))
        bottom_frame = ctk.CTkFrame(top, fg_color=("gray95", "#2b2b2b"), corner_radius=15); bottom_frame.pack(fill="x", padx=20, pady=20)
        voucher_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent"); voucher_frame.pack(side="left", fill="x", padx=20, pady=20)
        ctk.CTkLabel(voucher_frame, text="Mã giảm giá:", font=("Arial", 12, "bold")).pack(anchor="w")
        v_row = ctk.CTkFrame(voucher_frame, fg_color="transparent"); v_row.pack(fill="x", pady=5)
        self.entry_voucher = ctk.CTkEntry(v_row, width=120, placeholder_text="Mã voucher"); self.entry_voucher.pack(side="left")
        if self.current_voucher: self.entry_voucher.insert(0, self.current_voucher)
        ctk.CTkButton(v_row, text="Áp dụng", width=80, fg_color="#6c5ce7", command=lambda: self.apply_voucher(total_bill)).pack(side="left", padx=5)
        total_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent"); total_frame.pack(side="right", padx=20, pady=20)
        ctk.CTkLabel(total_frame, text=f"Tạm tính: {total_bill:,.0f} đ", font=("Arial", 12)).pack(anchor="e")
        self.lbl_discount = ctk.CTkLabel(total_frame, text="Giảm giá: 0 đ", text_color="#d63031"); self.lbl_discount.pack(anchor="e")
        self.lbl_final = ctk.CTkLabel(total_frame, text=f"{total_bill:,.0f} đ", text_color="#d63031", font=("Arial", 20, "bold")); self.lbl_final.pack(anchor="e")
        self.final_total = total_bill
        if self.current_voucher: self.apply_voucher(total_bill, silent=True)
        action_frame = ctk.CTkFrame(top, fg_color="transparent"); action_frame.pack(fill="x", padx=20, side="bottom", pady=20)
        ctk.CTkButton(action_frame, text="Xóa Giỏ Hàng", fg_color="gray", hover_color="gray40", command=lambda: [self.cart.clear(), self.update_cart_btn(), top.destroy()]).pack(side="left")
        ctk.CTkButton(action_frame, text="✅ THANH TOÁN NGAY", fg_color="#00b894", hover_color="#00a884", font=("Segoe UI", 13, "bold"), height=40, width=200, command=lambda: self.checkout_cart(top)).pack(side="right")

    def apply_voucher(self, original_total, silent=False):
        code = self.entry_voucher.get().strip().upper()
        if not code: return
        is_valid, result = self.promotion_service.check_promotion(code, original_total)
        if is_valid:
            discount_amt = result; self.final_total = max(0, original_total - discount_amt); self.current_voucher = code
            self.lbl_discount.configure(text=f"Giảm giá ({code}): -{discount_amt:,.0f} đ"); self.lbl_final.configure(text=f"{self.final_total:,.0f} đ")
            if not silent: messagebox.showinfo("Thành công", f"Đã áp dụng mã {code} thành công!\nGiảm: {discount_amt:,.0f} đ")
        else:
            self.current_voucher = None; self.final_total = original_total
            self.lbl_discount.configure(text="Giảm giá: 0 đ"); self.lbl_final.configure(text=f"{original_total:,.0f} đ")
            if not silent: messagebox.showerror("Lỗi Voucher", result)

    def checkout_cart(self, popup):
        if messagebox.askyesno("Xác nhận", f"Bạn muốn đặt đơn hàng này với giá {self.final_total:,.0f} đ?"):
            voucher_code = self.current_voucher if self.current_voucher else ""
            success, msg = self.order_service.create_order(self.current_user['id'], voucher_code, self.final_total, self.cart)
            if success:
                messagebox.showinfo("Thành công", f"Đặt hàng thành công!\n{msg}")
                self.cart.clear(); self.current_voucher = None; self.update_cart_btn(); popup.destroy(); self.apply_filters()
                if self.on_buy_click: self.on_buy_click() 
            else: messagebox.showerror("Lỗi", f"Không thể đặt hàng: {msg}")