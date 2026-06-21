import customtkinter
from tkinterdnd2 import DND_FILES
from pathlib import Path
from typing import Callable, Optional

class FileDropZone(customtkinter.CTkFrame):
    def __init__(self, master, on_drop: Callable, text="Arrastra archivos aquí o haz clic", **kwargs):
        super().__init__(master, height=100, corner_radius=15, **kwargs)
        self.on_drop = on_drop
        self.pack_propagate(False)

        self.label = customtkinter.CTkLabel(self, text=text)
        self.label.pack(expand=True)

        self.bind("<Button-1>", lambda e: self.on_click())
        self.label.bind("<Button-1>", lambda e: self.on_click())
        self._bind_drag()

    def _bind_drag(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._handle_drop)
        self.dnd_bind('<<DragEnter>>', self._on_drag_enter)
        self.dnd_bind('<<DragLeave>>', self._on_drag_leave)

    def _handle_drop(self, event):
        import re
        self.configure(fg_color=None)
        data = event.data
        paths = re.findall(r'\{([^}]+)\}|(\S+)', data)
        file_paths = [Path(p[0] if p[0] else p[1]) for p in paths]
        for path in file_paths:
            if path.exists():
                self.on_drop(str(path))

    def _on_drag_enter(self, event):
        self.configure(fg_color="#1a3a5c")

    def _on_drag_leave(self, event):
        self.configure(fg_color=None)

    def on_click(self):
        file_paths = customtkinter.filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[("Archivos compatibles", "*.pdf *.docx *.doc"), ("PDF", "*.pdf"), ("Word", "*.docx *.doc")]
        )
        for path in file_paths:
            self.on_drop(path)


class ProgressCard(customtkinter.CTkFrame):
    def __init__(self, master, filename, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill="x", pady=2, padx=5)

        self.name_label = customtkinter.CTkLabel(self, text=filename, width=250, anchor="w", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.name_label.pack(side="left", padx=10)

        self.progress_bar = customtkinter.CTkProgressBar(self, width=150)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=10)

        self.status_label = customtkinter.CTkLabel(self, text="En espera", width=150, font=customtkinter.CTkFont(size=11))
        self.status_label.pack(side="left", padx=10)

        self.open_btn = customtkinter.CTkButton(self, text="Abrir", width=60, height=24, state="disabled")
        self.open_btn.pack(side="right", padx=10)
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
                if path.is_file():
                    os.startfile(path.parent)
                else:
                    os.startfile(path)
            except Exception:
                pass

    def update(self, progress, message, status, result_path=None):
        if progress != self._last_progress:
            self.progress_bar.set(progress / 100)
            self._last_progress = progress
        if message != self._last_msg:
            self.status_label.configure(text=message)
            self._last_msg = message
        if status != self._last_status:
            if status == "success":
                self.status_label.configure(text_color="green")
                self.open_btn.configure(state="normal")
            elif status == "failed":
                self.status_label.configure(text_color="red")
            elif status == "running":
                self.status_label.configure(text_color="orange")
            self._last_status = status
        if result_path:
            self._result_path = result_path


class ModeToggle(customtkinter.CTkFrame):
    def __init__(self, master, on_change: Callable, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_change = on_change
        self._mode = "pdf2word"

        self.btn_pdf2word = customtkinter.CTkButton(self, text="PDF a Word", command=lambda: self.set_mode("pdf2word"), width=120)
        self.btn_pdf2word.grid(row=0, column=0, padx=10)

        self.btn_word2pdf = customtkinter.CTkButton(self, text="Word a PDF", command=lambda: self.set_mode("word2pdf"), width=120, fg_color="gray30")
        self.btn_word2pdf.grid(row=0, column=1, padx=10)

    def set_mode(self, mode):
        self._mode = mode
        self.btn_pdf2word.configure(fg_color="#1f538d" if mode == "pdf2word" else "gray30")
        self.btn_word2pdf.configure(fg_color="#1f538d" if mode == "word2pdf" else "gray30")
        self.on_change(mode)

    def get_mode(self):
        return self._mode


class StatusBadge(customtkinter.CTkLabel):
    COLORS = {
        "success": "green",
        "failed": "red",
        "running": "orange",
        "pending": "gray",
    }

    def __init__(self, master, text="", status="pending", **kwargs):
        super().__init__(master, text=text, font=customtkinter.CTkFont(size=11), **kwargs)
        self.set_status(status)

    def set_status(self, status):
        color = self.COLORS.get(status, "gray")
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
        import tkinter as tk
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self._tip_window = tk.Toplevel(self.widget)
        self._tip_window.wm_overrideredirect(True)
        self._tip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self._tip_window, text=self.text, justify="left",
                         background="#2b2b2b", foreground="white",
                         font=("Segoe UI", 9), padx=8, pady=4,
                         borderwidth=1, relief="solid")
        label.pack()

    def _hide(self):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None
