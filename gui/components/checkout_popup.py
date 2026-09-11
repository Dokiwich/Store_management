# gui/components/checkout_popup.py
import tkinter as tk
from tkinter import messagebox

class CheckoutPopup(tk.Toplevel):
    def __init__(self, parent, total_amount, on_confirm_callback):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self.title("Xác nhận thanh toán")
        self.geometry("400x350")
        self.total_amount = total_amount
        self.on_confirm_callback = on_confirm_callback # Hàm callback để báo lại cho POS tab
        
        # UI Layout
        tk.Label(self, text="THÔNG TIN THANH TOÁN", font=("Arial", 14, "bold"), fg="#2c3e50").pack(pady=15)

        # 1. Tổng tiền
        tk.Label(self, text=f"Tổng tiền cần thu:", font=("Arial", 10)).pack()
        tk.Label(self, text=f"{total_amount:,.0f} VNĐ", font=("Arial", 18, "bold"), fg="#e74c3c").pack(pady=5)

        # 2. Nhập khách hàng
        frame_cust = tk.Frame(self)
        frame_cust.pack(pady=10, padx=20, fill="x")
        
        tk.Label(frame_cust, text="SĐT Khách hàng (Nếu có):").pack(anchor="w")
        self.entry_phone = tk.Entry(frame_cust)
        self.entry_phone.pack(fill="x", pady=5)
        
        tk.Label(frame_cust, text="Ghi chú đơn hàng:").pack(anchor="w")
        self.entry_note = tk.Entry(frame_cust)
        self.entry_note.pack(fill="x", pady=5)

        # 3. Nút bấm
        frame_btn = tk.Frame(self, pady=10)
        frame_btn.pack()
        
        tk.Button(frame_btn, text="Hủy Bỏ", command=self.destroy, width=10).pack(side="left", padx=10)
        tk.Button(frame_btn, text="XÁC NHẬN", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), 
                  command=self.confirm_payment, width=15).pack(side="left", padx=10)

    def confirm_payment(self):
        # Lấy dữ liệu và gửi về callback
        phone = self.entry_phone.get().strip()
        note = self.entry_note.get().strip()
        
        if phone and (not phone.isdigit() or len(phone) != 10 or not phone.startswith('0')):
            messagebox.showwarning("Lỗi", "Số điện thoại phải có 10 chữ số và bắt đầu bằng 0.")
            self.focus_force()
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn chắc chắn muốn xuất hóa đơn này?"):
            self.on_confirm_callback(customer_phone=phone, note=note)
            self.destroy()