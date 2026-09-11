import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk # Import CustomTkinter
from PIL import Image, ImageTk 
import os

# Cấu hình giao diện chung
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTk):
    def __init__(self, user_service, on_login_success):
        super().__init__()
        self.user_service = user_service
        self.on_login_success = on_login_success
        
        # --- CẤU HÌNH CỬA SỔ CHÍNH ---
        self.title("Đăng nhập Hệ thống")
        self.geometry("500x650")
        self.resizable(False, False) 
        
        # fg_color set background cho cửa sổ chính (Xám nhạt ở Light mode, Đen ở Dark mode)
        self.configure(fg_color="#e3f2fd")

        # --- CARD TRUNG TÂM (Khung chứa form) ---
        # corner_radius=20 tạo góc bo tròn
        self.card_frame = ctk.CTkFrame(self, width=500, corner_radius=20, fg_color="#ffffff", border_width=0)
        self.card_frame.place(relx=0.5, rely=0.5, anchor="center",relwidth=0.9, relheight=0.8)

        # Layout bên trong Card
        # Tạo một frame con trong suốt để padding nội dung cho đẹp
        self.content_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # --- 1. LOGO & TIÊU ĐỀ ---
        try:
            img_path = "logo.png" 
            if os.path.exists(img_path):
                # Dùng CTkImage để hỗ trợ HighDPI tốt hơn
                pil_img = Image.open(img_path)
                self.logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(80, 80))
                
                ctk.CTkLabel(self.content_frame, image=self.logo_img, text="").pack(pady=(0, 10))
            else:
                # Placeholder Icon
                ctk.CTkLabel(self.content_frame, text="💻", font=("Arial", 60)).pack(pady=(0, 10))
        except Exception:
             ctk.CTkLabel(self.content_frame, text="💻", font=("Arial", 60)).pack(pady=(0, 10))

        # Tiêu đề chính
        ctk.CTkLabel(self.content_frame, text="Đăng Nhập", 
                     font=("Segoe UI", 26, "bold"), text_color=("black", "white")).pack()
        
        # Tiêu đề phụ
        ctk.CTkLabel(self.content_frame, text="Tiếp tục đến Laptop System", 
                     font=("Segoe UI", 13), text_color="gray").pack(pady=(5, 30))

        # --- 2. CÁC Ô NHẬP LIỆU ---
        
        # Tài khoản
        ctk.CTkLabel(self.content_frame, text="Tài khoản", font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", pady=(0, 5))
        
        self.entry_user = ctk.CTkEntry(self.content_frame, 
                                     placeholder_text="Nhập tên đăng nhập...",
                                     height=40, 
                                     corner_radius=10,
                                     border_width=1,
                                     font=("Segoe UI", 13))
        self.entry_user.pack(fill="x", pady=(0, 15))
        self.entry_user.insert(0, "admin") # Demo only, remove in production

        # Mật khẩu
        ctk.CTkLabel(self.content_frame, text="Mật khẩu", font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", pady=(0, 5))
        
        self.entry_pass = ctk.CTkEntry(self.content_frame, 
                                     placeholder_text="Nhập mật khẩu...",
                                     height=40, 
                                     corner_radius=10,
                                     border_width=1,
                                     show="*",
                                     font=("Segoe UI", 13))
        self.entry_pass.pack(fill="x", pady=(0, 10))
        self.entry_pass.insert(0, "123456") # Demo only, remove in production

        # Link "Quên mật khẩu?"
        forgot_lbl = ctk.CTkLabel(self.content_frame, text="Quên mật khẩu?", 
                                font=("Segoe UI", 12, "bold"), 
                                text_color=("#1a73e8", "#60a5fa"), 
                                cursor="hand2")
        forgot_lbl.pack(anchor="e", pady=(0, 30))
        # (Optional) Bind sự kiện click cho label này nếu cần

        # --- 3. NÚT ĐĂNG NHẬP ---
        self.btn_login = ctk.CTkButton(self.content_frame, text="ĐĂNG NHẬP", 
                                     fg_color="#1a73e8", hover_color="#1557b0",
                                     height=45, 
                                     corner_radius=10, 
                                     font=("Segoe UI", 13, "bold"),
                                     command=self.check_login)
        self.btn_login.pack(fill="x")

        # Gắn sự kiện Enter (CustomTkinter cũng hỗ trợ bind như thường)
        self.bind('<Return>', lambda event: self.check_login())

    # --- LOGIC GIỮ NGUYÊN ---
    def check_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        
        # Gọi DAO kiểm tra
        user_info = self.user_service.login(user, pwd)
        
        if user_info:
            self.withdraw()
            self.on_login_success(user_info) # Callback mở cửa sổ chính
            self.destroy()
        else:
            messagebox.showerror("Lỗi Đăng Nhập", "Tài khoản hoặc mật khẩu không đúng!\nVui lòng thử lại.")

# Phần test chạy thử độc lập (nếu cần)
if __name__ == "__main__":
    # Mock DAO để test giao diện
    class MockUserDAO:
        def login(self, u, p):
            print(f"Login attempt: {u}/{p}")
            if u == "admin" and p == "1": return {"full_name": "Admin Test", "role": "admin"}
            return None

    app = LoginWindow(MockUserDAO(), lambda u: print("Success:", u))
    app.mainloop()