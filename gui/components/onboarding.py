import customtkinter as ctk
import json
import os

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".laptop_store_config.json")


class GuidedTour:
    """Hướng dẫn sử dụng từng bước với highlight từng vùng giao diện."""

    def __init__(self, parent):
        self.parent = parent
        self.steps = []
        self.current_step = 0
        self.overlay = None
        self.card = None
        self.highlight_border = None

    @staticmethod
    def should_show_tour():
        try:
            with open(CONFIG_PATH, 'r') as f:
                return not json.load(f).get('tour_done', False)
        except (FileNotFoundError, json.JSONDecodeError):
            return True

    @staticmethod
    def mark_done():
        data = {}
        try:
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        data['tour_done'] = True
        with open(CONFIG_PATH, 'w') as f:
            json.dump(data, f)

    def add_step(self, widget, title, description):
        """Thêm bước hướng dẫn. widget=None cho bước tổng quan."""
        self.steps.append({
            'widget': widget,
            'title': title,
            'description': description
        })

    def start(self):
        if not self.steps:
            return
        self.current_step = 0
        self.parent.after(500, self._show_step)

    def _show_step(self):
        self._cleanup()
        if self.current_step >= len(self.steps):
            self.mark_done()
            return

        step = self.steps[self.current_step]
        widget = step['widget']

        # Overlay bán trong suốt
        self.overlay = ctk.CTkFrame(self.parent, fg_color="black")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.configure(fg_color=("gray20", "gray20"))
        # Cho overlay mờ bằng cách dùng opacity thấp
        self.overlay.bind("<Button-1>", lambda e: None)  # Block clicks

        self.parent.update_idletasks()

        # Highlight widget nếu có
        if widget and widget.winfo_exists():
            try:
                # Tính vị trí tương đối trong parent
                wx = widget.winfo_rootx() - self.parent.winfo_rootx()
                wy = widget.winfo_rooty() - self.parent.winfo_rooty()
                ww = widget.winfo_width()
                wh = widget.winfo_height()

                # Border highlight
                pad = 4
                self.highlight_border = ctk.CTkFrame(
                    self.parent,
                    fg_color="transparent",
                    border_color="#00d4ff",
                    border_width=3,
                    corner_radius=8
                )
                self.highlight_border.place(
                    x=wx - pad, y=wy - pad,
                    width=ww + 2 * pad, height=wh + 2 * pad
                )
                self.highlight_border.lift()

                # Nâng widget lên trên overlay
                widget.lift()
            except Exception:
                wx, wy, ww, wh = 0, 0, 0, 0
        else:
            wx = self.parent.winfo_width() // 2 - 175
            wy = self.parent.winfo_height() // 2 - 100
            ww, wh = 0, 0

        # Card hướng dẫn
        self.card = ctk.CTkToplevel(self.parent)
        self.card.overrideredirect(True)
        self.card.attributes('-topmost', True)

        card_w, card_h = 350, 200

        # Vị trí card: bên phải hoặc bên dưới widget
        card_x = self.parent.winfo_rootx() + wx + ww + 15
        card_y = self.parent.winfo_rooty() + wy

        # Nếu tràn phải màn hình, đặt bên trái
        screen_w = self.parent.winfo_screenwidth()
        if card_x + card_w > screen_w:
            card_x = self.parent.winfo_rootx() + wx - card_w - 15
        # Nếu vẫn tràn, đặt bên dưới
        if card_x < 0:
            card_x = self.parent.winfo_rootx() + wx
            card_y = self.parent.winfo_rooty() + wy + wh + 15

        self.card.geometry(f"{card_w}x{card_h}+{card_x}+{card_y}")

        # Nội dung card
        frame = ctk.CTkFrame(self.card, corner_radius=15, fg_color="#ffffff",
                             border_width=2, border_color="#00d4ff")
        frame.pack(fill="both", expand=True)

        # Step counter
        step_text = f"Bước {self.current_step + 1}/{len(self.steps)}"
        ctk.CTkLabel(frame, text=step_text, font=("Segoe UI", 10),
                     text_color="#6b7280").pack(anchor="w", padx=20, pady=(15, 0))

        # Title
        ctk.CTkLabel(frame, text=step['title'], font=("Segoe UI", 15, "bold"),
                     text_color="#1f2937").pack(anchor="w", padx=20, pady=(5, 0))

        # Description
        ctk.CTkLabel(frame, text=step['description'], font=("Segoe UI", 11),
                     text_color="#4b5563", wraplength=300,
                     justify="left").pack(anchor="w", padx=20, pady=(5, 0))

        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 15))

        ctk.CTkButton(btn_frame, text="Bỏ qua", width=80, height=32,
                      fg_color="transparent", text_color="#6b7280",
                      border_width=1, border_color="#d1d5db",
                      corner_radius=8, font=("Segoe UI", 11),
                      command=self._skip).pack(side="left")

        is_last = self.current_step >= len(self.steps) - 1
        next_text = "Hoàn tất ✓" if is_last else "Tiếp theo →"
        ctk.CTkButton(btn_frame, text=next_text, width=100, height=32,
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      corner_radius=8, font=("Segoe UI", 11, "bold"),
                      command=self._next).pack(side="right")

    def _next(self):
        self.current_step += 1
        self._show_step()

    def _skip(self):
        self._cleanup()
        self.mark_done()

    def _cleanup(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
        if self.card:
            self.card.destroy()
            self.card = None
        if self.highlight_border:
            self.highlight_border.destroy()
            self.highlight_border = None
