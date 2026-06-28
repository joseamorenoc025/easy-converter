import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

MUTEX_NAME = "EasyConverter_SingleInstance_v2"


def check_single_instance():
    """Verifica si ya hay una instancia corriendo. Retorna True si es la primera."""
    try:
        import ctypes
        ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
        last_error = ctypes.windll.kernel32.GetLastError()

        if last_error == 183:  # ERROR_ALREADY_EXISTS
            _focus_existing_window()
            return False

        return True
    except Exception:
        return True


def _focus_existing_window():
    """Intenta enfocar la ventana existente de EasyConverter."""
    try:
        import win32gui
        import win32con

        def enum_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Easy Converter" in title or "EasyConverter" in title:
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    return False
            return True

        win32gui.EnumWindows(enum_callback, None)
    except Exception:
        pass

from ui.main_window import App  # noqa: E402
from utils.config import ConfigManager  # noqa: E402
from core.error_handler import WordMissingError  # noqa: E402
from utils.word_checker import WordChecker  # noqa: E402
from tkinter import messagebox  # noqa: E402


def _first_run_setup(parent):
    config = ConfigManager()
    if not config.get("first_run_complete", False):
        messages = []
        try:
            WordChecker.check_word_or_fail()
        except WordMissingError:
            messages.append(
                "• Microsoft Word no está instalado.\n"
                "  La conversión de Word a PDF (DOCX→PDF) no estará disponible.\n"
                "  La conversión PDF a Word sí funciona sin Word."
            )
        except Exception:
            messages.append(
                "• No se pudo verificar Microsoft Word.\n"
                "  Si no está instalado, la conversión Word→PDF no funcionará."
            )

        try:
            import pytesseract
            pytesseract.get_tesseract_version()
        except Exception:
            install_tesseract = messagebox.askyesno(
                "Easy Converter - Tesseract OCR",
                "Tesseract OCR no está instalado.\n\n"
                "Esta herramienta es necesaria para la función OCR "
                "(extraer texto de imágenes en PDF).\n\n"
                "¿Quieres descargar e instalar Tesseract ahora?\n\n"
                "Se abrirá el navegador en la página de descarga oficial."
            )
            if install_tesseract:
                import webbrowser
                webbrowser.open("https://github.com/UB-Mannheim/tesseract/wiki")
                messagebox.showinfo(
                    "Easy Converter",
                    "Descarga e instala Tesseract desde la página abierta.\n\n"
                    "Una vez instalado, reinicia Easy Converter para "
                    "que la opción OCR esté disponible."
                )

        if messages:
            msg = "Bienvenido a Easy Converter v2.0\n\n" + \
                  "Se detectaron los siguientes puntos a tener en cuenta:\n\n" + \
                  "\n\n".join(messages) + \
                  "\n\nPuedes cambiar estas opciones más tarde desde la aplicación."

            messagebox.showinfo("Easy Converter - Primer inicio", msg)

        from utils.context_menu import add_context_menu
        try:
            add_context_menu()
        except Exception:
            pass

        config.set("first_run_complete", True)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf2word", type=str, help="Convertir PDF a Word vía CLI")
    parser.add_argument("--word2pdf", type=str, help="Convertir Word a PDF vía CLI")
    parser.add_argument("--setup-context-menu", action="store_true", help="Registrar menú contextual")
    parser.add_argument("--remove-context-menu", action="store_true", help="Eliminar menú contextual")
    args, unknown = parser.parse_known_args()

    if args.setup_context_menu:
        from utils.context_menu import add_context_menu
        add_context_menu()
        return
    if args.remove_context_menu:
        from utils.context_menu import remove_context_menu
        remove_context_menu()
        return

    if not check_single_instance():
        sys.exit(0)

    app = App()

    _first_run_setup(app)

    if args.pdf2word:
        app.after(1000, lambda: app.process_selected_file(args.pdf2word))
    elif args.word2pdf:
        app.after(1000, lambda: app.process_selected_file(args.word2pdf))

    app.mainloop()


if __name__ == "__main__":
    main()
