import sys
import threading
import customtkinter

_NOTIFICATION_QUEUE: list = []
_NOTIFICATION_LOCK = threading.Lock()
_NOTIFICATION_WINDOW = None

_TYPE_CONFIG = {
    "info":    {"icon": "\u2139\ufe0f", "bg_key": "primary",   "fg": "white"},
    "success": {"icon": "\u2705",       "bg_key": "success",   "fg": "white"},
    "error":   {"icon": "\u274c",       "bg_key": "error",     "fg": "white"},
    "warning": {"icon": "\u26a0\ufe0f", "bg_key": "warning",  "fg": "white"},
}


class InAppNotification(customtkinter.CTkFrame):
    def __init__(self, master, message, ntype="info", duration=4000, **kwargs):
        from ui.themes import ThemeManager
        cfg = _TYPE_CONFIG.get(ntype, _TYPE_CONFIG["info"])
        bg = ThemeManager.get_color(cfg["bg_key"])
        super().__init__(master, fg_color=bg, corner_radius=10, **kwargs)
        self.duration = duration

        content = customtkinter.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=16, pady=10)

        icon = customtkinter.CTkLabel(content, text=cfg["icon"],
                                      font=customtkinter.CTkFont(size=18))
        icon.pack(side="left", padx=(0, 10))

        msg_label = customtkinter.CTkLabel(content, text=message,
                                           font=customtkinter.CTkFont(size=13),
                                           text_color=cfg["fg"],
                                           wraplength=500, justify="left")
        msg_label.pack(side="left", fill="x", expand=True)

        close_btn = customtkinter.CTkButton(content, text="\u2715", width=24, height=24,
                                            fg_color="transparent",
                                            text_color=cfg["fg"],
                                            hover_color="gray40",
                                            font=customtkinter.CTkFont(size=12),
                                            command=self._dismiss)
        close_btn.pack(side="right", padx=(8, 0))

        self.place(relx=0.5, rely=0.02, anchor="n", relwidth=0.75)
        self.lift()
        self.after(200, self._slide_in)
        self.after(duration, self._dismiss)

    def _slide_in(self):
        for i in range(6):
            self.place(rely=0.01 + i * 0.015)
            self.update_idletasks()

    def _dismiss(self):
        try:
            self.destroy()
        except Exception:
            pass


def notify_in_app(master, message, ntype="info", duration=4000):
    InAppNotification(master, message, ntype=ntype, duration=duration)


def notify_native(title, message):
    if sys.platform != "win32":
        return
    try:
        import win32gui
        import win32con

        class _ToastWindow:
            def __init__(self):
                self.hwnd = None
                self._register()

            def _register(self):
                wc = win32gui.WNDCLASS()
                wc.lpfnWndProc = self._wndproc
                wc.lpszClassName = "EasyConverterToast"
                wc.hInstance = win32gui.GetModuleHandle(None)
                try:
                    win32gui.RegisterClass(wc)
                except Exception:  # noqa: E722
                    pass
                self.hwnd = win32gui.CreateWindow(
                    wc.lpszClassName, "EasyConverter", win32con.WS_OVERLAPPEDWINDOW,
                    0, 0, 0, 0, 0, 0, wc.hInstance, None
                )

            def _wndproc(self, hwnd, msg, wparam, lparam):
                return 0

        from win32gui import Shell_NotifyIcon, NIM_ADD, NIM_DELETE, NIF_INFO, NIF_TIP, NIF_MESSAGE

        toast = _ToastWindow()
        flags = NIF_INFO | NIF_TIP | NIF_MESSAGE
        nid = (toast.hwnd, 0, flags, 0, "Easy Converter", message, 5000, title, 0)
        Shell_NotifyIcon(NIM_ADD, nid)
        import time
        time.sleep(0.5)
        Shell_NotifyIcon(NIM_DELETE, nid)
        win32gui.DestroyWindow(toast.hwnd)
    except Exception:
        pass


class NotificationManager:
    def __init__(self, master=None):
        self.master = master

    def info(self, title, message):
        self._show(title, message, "info")

    def success(self, title, message):
        self._show(title, message, "success")

    def error(self, title, message):
        self._show(title, message, "error")

    def warning(self, title, message):
        self._show(title, message, "warning")

    def _show(self, title, message, ntype="info"):
        if self.master and self.master.winfo_exists():
            notify_in_app(self.master, f"{title}: {message}", ntype=ntype, duration=4000)
        threading.Thread(target=notify_native, args=(title, message), daemon=True).start()
