import customtkinter
from tkinterdnd2 import DND_FILES
from pathlib import Path
from typing import Callable


class FileDropZone(customtkinter.CTkFrame):
    def __init__(self, master, on_drop: Callable, text=None, **kwargs):
        from ui.themes import ThemeManager
        super().__init__(master, height=110, corner_radius=12,
                         fg_color=ThemeManager.get_color("drop_zone_bg"),
                         border_width=2,
                         border_color=ThemeManager.get_color("drop_zone_border"),
                         **kwargs)
        self.on_drop = on_drop
        self.pack_propagate(False)

        self._default_fg = ThemeManager.get_color("drop_zone_bg")
        self._hover_fg = ThemeManager.get_color("drop_zone_hover")
        self._border_default = ThemeManager.get_color("drop_zone_border")

        icon_label = customtkinter.CTkLabel(self, text="\u2b07\ufe0f", font=customtkinter.CTkFont(size=28))
        icon_label.pack(pady=(12, 0))

        display_text = text or "Arrastra archivos aqu\u00ed o haz clic"
        self.label = customtkinter.CTkLabel(self, text=display_text,
                                            font=customtkinter.CTkFont(size=12),
                                            text_color=ThemeManager.get_color("text_secondary"))
        self.label.pack(pady=(0, 10))

        self.bind("<Button-1>", lambda e: self.on_click())
        icon_label.bind("<Button-1>", lambda e: self.on_click())
        self.label.bind("<Button-1>", lambda e: self.on_click())
        self._bind_drag()

    def _bind_drag(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._handle_drop)
        self.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        self.dnd_bind('<<DragLeave>>', self._on_drag_leave)

    def _handle_drop(self, event):
        import re
        self.configure(fg_color=self._default_fg, border_color=self._border_default)
        data = event.data
        paths = re.findall(r'\{([^}]+)\}|(\S+)', data)
        file_paths = [Path(p[0] if p[0] else p[1]) for p in paths]
        for path in file_paths:
            if path.exists():
                self.on_drop(str(path))

    def _on_drag_enter(self, event):
        self.configure(fg_color=self._hover_fg, border_color="accent")

    def _on_drag_leave(self, event):
        self.configure(fg_color=self._default_fg, border_color=self._border_default)

    def on_click(self):
        file_paths = customtkinter.filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[("Archivos compatibles", "*.pdf *.docx *.doc"), ("PDF", "*.pdf"), ("Word", "*.docx *.doc")]
        )
        for path in file_paths:
            self.on_drop(path)


class ProgressCard(customtkinter.CTkFrame):
    def __init__(self, master, filename, mode="pdf2word", **kwargs):
        from ui.themes import ThemeManager
        super().__init__(master, fg_color=ThemeManager.get_color("card_bg"),
                         corner_radius=8, **kwargs)
        self.pack(fill="x", pady=3, padx=5)

        ext = Path(filename).suffix.lower()
        is_pdf = ext == ".pdf"
        badge_text = "PDF" if is_pdf else "DOCX"
        badge_color = ThemeManager.get_color("badge_pdf" if is_pdf else "badge_docx")

        self.badge = customtkinter.CTkLabel(self, text=badge_text, width=42, height=20,
                                            font=customtkinter.CTkFont(size=9, weight="bold"),
                                            fg_color=badge_color, text_color="white",
                                            corner_radius=4)
        self.badge.pack(side="left", padx=(10, 6), pady=6)

        self.name_label = customtkinter.CTkLabel(self, text=filename, width=220, anchor="w",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        self.name_label.pack(side="left", padx=4, pady=6)

        self.progress_bar = customtkinter.CTkProgressBar(self, width=130, height=12)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=10, pady=6)

        self.status_label = customtkinter.CTkLabel(self, text="En espera", width=140,
                                                   font=customtkinter.CTkFont(size=11),
                                                   text_color=ThemeManager.get_color("text_secondary"))
        self.status_label.pack(side="left", padx=4, pady=6)

        self.open_btn = customtkinter.CTkButton(self, text="Abrir", width=55, height=24,
                                                state="disabled",
                                                fg_color=ThemeManager.get_color("primary"))
        self.open_btn.pack(side="right", padx=(0, 6), pady=6)
        self.open_btn.configure(command=self._open_callback)

        self._result_path = None
        self._last_msg = ""
        self._last_status = ""
        self._last_progress = -1

    def _open_callback(self):
        if self._result_path:
            path = Path(self._result_path)
            try:
                import os
                if path.exists():
                    os.startfile(str(path))
            except Exception:
                pass

    def update(self, progress, message, status, result_path=None):
        from ui.themes import ThemeManager
        if progress != self._last_progress:
            self.progress_bar.set(progress / 100)
            self._last_progress = progress
        if message != self._last_msg:
            self.status_label.configure(text=message)
            self._last_msg = message
        if status != self._last_status:
            if status == "success":
                self.status_label.configure(text_color=ThemeManager.get_color("success"))
                self.open_btn.configure(state="normal")
            elif status == "failed":
                self.status_label.configure(text_color=ThemeManager.get_color("error"))
            elif status == "running":
                self.status_label.configure(text_color=ThemeManager.get_color("warning"))
            else:
                self.status_label.configure(text_color=ThemeManager.get_color("text_secondary"))
            self._last_status = status
        if result_path:
            self._result_path = result_path


class ModeToggle(customtkinter.CTkFrame):
    def __init__(self, master, on_change: Callable, **kwargs):
        from ui.themes import ThemeManager
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_change = on_change
        self._mode = "pdf2word"
        self._primary = ThemeManager.get_color("primary")

        self.btn_pdf2word = customtkinter.CTkButton(
            self, text="PDF a Word", command=lambda: self.set_mode("pdf2word"),
            width=130, height=36,
            font=customtkinter.CTkFont(size=13, weight="bold"),
            corner_radius=8)
        self.btn_pdf2word.grid(row=0, column=0, padx=6)

        self.btn_word2pdf = customtkinter.CTkButton(
            self, text="Word a PDF", command=lambda: self.set_mode("word2pdf"),
            width=130, height=36,
            font=customtkinter.CTkFont(size=13, weight="bold"),
            fg_color="gray30", corner_radius=8)
        self.btn_word2pdf.grid(row=0, column=1, padx=6)

        self.set_mode("pdf2word")

    def set_mode(self, mode):
        from ui.themes import ThemeManager
        self._mode = mode
        self._primary = ThemeManager.get_color("primary")
        self.btn_pdf2word.configure(
            fg_color=self._primary if mode == "pdf2word" else "gray30")
        self.btn_word2pdf.configure(
            fg_color=self._primary if mode == "word2pdf" else "gray30")
        self.on_change(mode)

    def get_mode(self):
        return self._mode


class StatusBadge(customtkinter.CTkLabel):
    def __init__(self, master, text="", status="pending", **kwargs):
        super().__init__(master, text=text, font=customtkinter.CTkFont(size=11), **kwargs)
        self.set_status(status)

    def set_status(self, status):
        from ui.themes import ThemeManager
        color_map = {
            "success": ThemeManager.get_color("success"),
            "failed": ThemeManager.get_color("error"),
            "running": ThemeManager.get_color("warning"),
            "retry_pending": ThemeManager.get_color("accent"),
            "pending": ThemeManager.get_color("text_secondary"),
        }
        color = color_map.get(status, ThemeManager.get_color("text_secondary"))
        self.configure(text_color=color)


class ToolTip:
    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._tip_window = None
        self._after_id = None
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
        self._after_id = self.widget.after(self.delay, self._show)

    def _on_leave(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self):
        from ui.themes import ThemeManager
        import tkinter as tk
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self._tip_window = tk.Toplevel(self.widget)
        self._tip_window.wm_overrideredirect(True)
        self._tip_window.wm_geometry(f"+{x}+{y}")
        bg = ThemeManager.get_color("card_bg")
        fg = ThemeManager.get_color("text")
        border = ThemeManager.get_color("border")
        label = tk.Label(self._tip_window, text=self.text, justify="left",
                         background=bg, foreground=fg,
                         font=("Segoe UI", 9), padx=8, pady=4,
                         borderwidth=1, relief="solid", highlightbackground=border)
        label.pack()

    def _hide(self):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None
