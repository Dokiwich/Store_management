import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk # Import CustomTkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import datetime
import matplotlib.pyplot as plt
from gui.components.tooltip import ToolTip

class DashboardTab(ctk.CTkFrame): # Kế thừa CTkFrame
    def __init__(self, parent, report_service):
        super().__init__(parent, fg_color="transparent")
        self.report_service = report_service
        
        # --- 1. THANH CÔNG CỤ (CONTROL PANEL) ---
        # Frame chứa công cụ điều khiển
        self.control_frame = ctk.CTkFrame(self, fg_color=("white", "#1f2937"), corner_radius=10)
        self.control_frame.pack(fill="x", padx=20, pady=(10, 10))
        
        # Container bên trong để căn lề
        inner_ctrl = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        inner_ctrl.pack(fill="x", padx=20, pady=15)

        # Tiêu đề
        ctk.CTkLabel(inner_ctrl, text="BẢNG ĐIỀU KHIỂN", 
                     text_color=("#111827", "white"),
                     font=("Segoe UI", 16, "bold")).pack(side="left")

        # Separator (kẻ dọc)
        ctk.CTkLabel(inner_ctrl, text="|", text_color="gray").pack(side="left", padx=15)

        # Chọn Loại Biểu Đồ
        ctk.CTkLabel(inner_ctrl, text="Loại biểu đồ:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
        
        self.chart_type = tk.StringVar(value="bar")
        
        # Radio Button của CTK
        radio_bar = ctk.CTkRadioButton(inner_ctrl, text="Doanh thu (Cột)", variable=self.chart_type, value="bar", 
                           command=self.update_chart)
        radio_bar.pack(side="left", padx=10)
        radio_pie = ctk.CTkRadioButton(inner_ctrl, text="Danh mục (Tròn)", variable=self.chart_type, value="pie", 
                           command=self.update_chart)
        radio_pie.pack(side="left", padx=10)

        # Separator
        ctk.CTkLabel(inner_ctrl, text="|", text_color="gray").pack(side="left", padx=15)

        # Chọn Năm
        ctk.CTkLabel(inner_ctrl, text="Chọn Năm:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
        
        self.years = self.report_service.get_available_years()
        # Nếu không có data, default năm nay
        if not self.years: self.years = [str(datetime.datetime.now().year)]
        
        # CTK ComboBox: dùng command thay vì bind
        self.cb_year = ctk.CTkComboBox(inner_ctrl, values=[str(y) for y in self.years], 
                                       width=100, state="readonly",
                                       command=lambda x: self.update_chart())
        self.cb_year.pack(side="left")
        self.cb_year.set(str(self.years[0])) # Set default

        # Nút Làm mới
        btn_refresh = ctk.CTkButton(inner_ctrl, text="Tải lại", width=100, 
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      command=self.update_chart)
        btn_refresh.pack(side="right")
        
        ToolTip(radio_bar, "Xem biểu đồ doanh thu dạng cột")
        ToolTip(radio_pie, "Xem tỷ trọng sản phẩm bán ra")
        ToolTip(self.cb_year, "Chọn năm thống kê")
        ToolTip(btn_refresh, "Cập nhật dữ liệu mới nhất")

        # --- 2. KHUNG CHỨA BIỂU ĐỒ ---
        # Frame này sẽ chứa Canvas của Matplotlib
        self.chart_frame = ctk.CTkFrame(self, fg_color=("white", "#1f2937"), corner_radius=10)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.canvas = None
        
        # Vẽ lần đầu
        self.update_chart()

    def update_chart(self, event=None):
        # Xóa biểu đồ cũ nếu có
        if hasattr(self, 'current_fig'):
            plt.close(self.current_fig)
            
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        chart_mode = self.chart_type.get()
        
        # Tạo Figure mới
        # dpi=100 chuẩn, figsize tùy chỉnh
        fig = Figure(figsize=(10, 5), dpi=100)
        self.current_fig = fig
        
        # Chỉnh màu nền cho Figure để khớp với Dark/Light mode (Tùy chọn)
        # Ở đây mình để trắng mặc định cho an toàn, hoặc bạn có thể chỉnh
        # fig.patch.set_facecolor('#f0f0f0') 
        
        ax = fig.add_subplot(111)

        if chart_mode == "bar":
            self.draw_revenue_bar_chart(ax)
        else:
            self.draw_category_pie_chart(ax)

        # Hiển thị lên Tkinter (nhúng vào chart_frame)
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        
        # Widget của Canvas là một tk.Widget thông thường, pack vào CTKFrame vô tư
        widget = self.canvas.get_tk_widget()
        widget.pack(fill="both", expand=True, padx=10, pady=10)

    # --- LOGIC VẼ BIỂU ĐỒ (GIỮ NGUYÊN) ---
    def draw_revenue_bar_chart(self, ax):
        # Lấy năm từ combobox
        try:
            year = int(self.cb_year.get()) # CTK Entry/Combo dùng get bình thường
        except (ValueError, TypeError):
            year = datetime.datetime.now().year

        # Lấy dữ liệu từ DAO
        data = self.report_service.get_revenue_by_year(year)
        months = [f"T{i}" for i in range(1, 13)] 
        
        # Vẽ cột
        bars = ax.bar(months, data, color="#3b82f6", width=0.6)
        
        # Trang trí
        ax.set_title(f"DOANH THU NĂM {year}", fontsize=14, fontweight='bold', color="#333")
        ax.set_ylabel("Doanh thu (VNĐ)")
        ax.set_xlabel("Tháng")
        
        # Hiện số tiền trên đầu cột
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height):,}',
                        ha='center', va='bottom', fontsize=9, rotation=0)

        # Grid mờ
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    def draw_category_pie_chart(self, ax):
        # Lấy dữ liệu tỷ trọng
        data = self.report_service.get_category_share()
        
        if not data:
            ax.text(0.5, 0.5, "Chưa có dữ liệu bán hàng", ha='center')
            return

        labels = [row[0] for row in data]
        sizes = [row[1] for row in data]
        
        # Màu sắc đẹp (Pastel)
        colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0', '#ffb3e6']

        # Vẽ hình tròn
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                          startangle=90, colors=colors, pctdistance=0.85)
        
        # Donut Chart
        centre_circle = Circle((0,0),0.70,fc='white')
        ax.add_artist(centre_circle)

        # Trang trí text
        ax.set_title("TỶ TRỌNG SẢN PHẨM ĐÃ BÁN", fontsize=14, fontweight='bold', color="#333")
        
        for text in texts:
            text.set_color("#374151")
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")
            
        ax.axis('equal')