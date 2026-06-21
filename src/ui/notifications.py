import sys
import threading
import customtkinter

_NOTIFICATION_QUEUE = []
_NOTIFICATION_LOCK = threading.Lock()
_NOTIFICATION_WINDOW = None

class InAppNotification(customtkinter.CTkFrame):
    def __init__(self, master, message, duration=4000, **kwargs):
        super().__init__(master, fg_color="#2b2b2b", corner_radius=8, **kwargs)
        self.duration = duration
        self.place(relx=0.5, rely=0.0, anchor="n", relwidth=0.8)
        self.lift()

        label = customtkinter.CTkLabel(self, text=message, font=customtkinter.CTkFont(size=13), padx=20, pady=10)
        label.pack()

        self.after(200, self._slide_in)
        self.after(duration, self._slide_out)

    def _slide_in(self):
        for i in range(5):
            self.place(rely=i * 0.02)
            self.update_idletasks()

    def _slide_out(self):
        self.destroy()


def notify_in_app(master, message, duration=4000):
    InAppNotification(master, message, duration)


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
                except Exception:  # noqa: E722 - Windows API error handling
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
        self._show(title, message)

    def success(self, title, message):
        self._show(title, message)

    def error(self, title, message):
        self._show(title, message)

    def _show(self, title, message):
        if self.master and self.master.winfo_exists():
            notify_in_app(self.master, f"{title}: {message}", 4000)
        threading.Thread(target=notify_native, args=(title, message), daemon=True).start()
