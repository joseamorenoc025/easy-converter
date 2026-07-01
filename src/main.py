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


def _run_cli_tool(args):
    """Ejecuta operaciones CLI sin abrir la GUI. Retorna True si se procesó algo."""
    from pathlib import Path
    from utils.pdf_tools import (
        merge_pdfs, split_pdf, compress_pdf, sanitize_pdf,
        decrypt_pdf, get_pdf_info,
    )

    if args.info:
        path = Path(args.info)
        if not path.exists():
            print(f"Error: {path} no existe")
            return True
        info = get_pdf_info(str(path))
        print(f"Archivo:       {info['path']}")
        print(f"Páginas:       {info['pages']}")
        print(f"Cifrado:       {'Sí' if info['encrypted'] else 'No'}")
        print(f"Tamaño:        {info['size_mb']} MB")
        if info.get("title"):
            print(f"Título:        {info['title']}")
        if info.get("author"):
            print(f"Autor:         {info['author']}")
        return True

    if args.compress:
        src = Path(args.compress)
        if not src.exists():
            print(f"Error: {src} no existe")
            return True
        quality = getattr(args, "quality", "medium")
        out = src.with_name(f"{src.stem}_comprimido.pdf")
        print(f"Comprimiendo {src.name} (calidad: {quality})...")
        result = compress_pdf(str(src), str(out), quality=quality)
        ratio = result["ratio"]
        orig = result["original_size"] / (1024 * 1024)
        comp = result["compressed_size"] / (1024 * 1024)
        print(f"Completado: {orig:.1f} MB → {comp:.1f} MB ({ratio}% reducción)")
        print(f"Guardado: {out}")
        return True

    if args.sanitize:
        src = Path(args.sanitize)
        if not src.exists():
            print(f"Error: {src} no existe")
            return True
        out = src.with_name(f"{src.stem}_sanitizado.pdf")
        print(f"Sanitizando {src.name}...")
        result = sanitize_pdf(str(src), str(out))
        print(f"Completado: {result['items_removed']} elemento(s) eliminado(s)")
        print(f"Guardado: {out}")
        return True

    if args.decrypt:
        src = Path(args.decrypt)
        if not src.exists():
            print(f"Error: {src} no existe")
            return True
        password = getattr(args, "password", "")
        if not password:
            print("Error: se requiere --password para descifrar")
            return True
        out = src.with_name(f"{src.stem}_descifrado.pdf")
        print(f"Descifrando {src.name}...")
        result = decrypt_pdf(str(src), str(out), password)
        if result["success"]:
            print(f"Completado: {result.get('pages', 0)} páginas")
            print(f"Guardado: {out}")
        else:
            print(f"Error: {result.get('error', 'Contraseña incorrecta')}")
        return True

    if args.merge:
        srcs = [Path(p) for p in args.merge]
        for s in srcs:
            if not s.exists():
                print(f"Error: {s} no existe")
                return True
        out = Path(args.output) if args.output else Path("merged_output.pdf")
        print(f"Combinando {len(srcs)} archivos...")
        result = merge_pdfs([str(s) for s in srcs], str(out))
        print(f"Guardado: {result}")
        return True

    if args.split:
        src = Path(args.split)
        if not src.exists():
            print(f"Error: {src} no existe")
            return True
        pages_str = getattr(args, "pages", None)
        if not pages_str:
            print("Error: se requiere --pages para dividir (ej: 1-3,5,7-9)")
            return True
        output_dir = str(src.parent)
        ranges = []
        for part in pages_str.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                ranges.append((int(a) - 1, int(b) - 1))
            else:
                n = int(part) - 1
                ranges.append((n, n))
        print(f"Dividiendo {src.name}...")
        out_files = split_pdf(str(src), output_dir, ranges=ranges)
        print(f"Completado: {len(out_files)} archivo(s) generado(s)")
        for f in out_files:
            print(f"  {f}")
        return True

    if args.batch:
        folder = Path(args.batch)
        if not folder.is_dir():
            print(f"Error: {folder} no es una carpeta válida")
            return True
        mode = getattr(args, "mode", "pdf2word")
        recursive = getattr(args, "recursive", False)
        if mode == "pdf2word":
            exts = ("*.pdf",)
        else:
            exts = ("*.docx", "*.doc")
        files = []
        for ext in exts:
            if recursive:
                files.extend(folder.rglob(ext))
            else:
                files.extend(folder.glob(ext))
        files = [f for f in files if f.is_file()]
        if not files:
            print("No se encontraron archivos compatibles")
            return True
        print(f"Encontrados {len(files)} archivos. Encolando...")
        for f in files:
            print(f"  + {f.name}")
        print("Abra la aplicación para ver el progreso.")
        return True

    return False


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
            from pathlib import Path
            from utils.platform_service import WindowsPlatformService
            ps = WindowsPlatformService()
            tesseract_path = ps.get_tesseract_path()
            if not tesseract_path:
                app_dir = Path(__file__).parent.parent
                portable = app_dir / "tesseract" / "tesseract.exe"
                if portable.exists():
                    tesseract_path = portable
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = str(tesseract_path)
                os.environ["TESSDATA_PREFIX"] = str(tesseract_path.parent)
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
            msg = "Bienvenido a Easy Converter v2.2\n\n" + \
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
    parser = argparse.ArgumentParser(
        prog="EasyConverter",
        description="Easy Converter — Convertidor de PDF/Word de escritorio"
    )

    # Conversión rápida
    parser.add_argument("--pdf2word", type=str, help="Convertir un PDF a Word vía CLI")
    parser.add_argument("--word2pdf", type=str, help="Convertir un Word a PDF vía CLI")

    # Menú contextual
    parser.add_argument("--setup-context-menu", action="store_true", help="Registrar menú contextual")
    parser.add_argument("--remove-context-menu", action="store_true", help="Eliminar menú contextual")

    # Operaciones PDF
    parser.add_argument("--info", type=str, metavar="PDF", help="Mostrar información de un PDF")
    parser.add_argument("--compress", type=str, metavar="PDF", help="Comprimir un PDF")
    parser.add_argument("--quality", choices=["low", "medium", "high"], default="medium", help="Calidad de compresión (default: medium)")
    parser.add_argument("--sanitize", type=str, metavar="PDF", help="Sanitizar un PDF (eliminar scripts/formularios)")
    parser.add_argument("--decrypt", type=str, metavar="PDF", help="Descifrar un PDF protegido con contraseña")
    parser.add_argument("--password", type=str, default="", help="Contraseña para descifrar PDF")
    parser.add_argument("--merge", nargs="+", metavar="PDF", help="Combinar varios PDFs en uno")
    parser.add_argument("--split", type=str, metavar="PDF", help="Dividir un PDF por páginas")
    parser.add_argument("--pages", type=str, metavar="RANGO", help="Páginas para --split (ej: 1-3,5,7-9)")
    parser.add_argument("--output", type=str, metavar="PATH", help="Ruta de salida para --merge")
    parser.add_argument("--batch", type=str, metavar="CARPETA", help="Convertir todos los archivos de una carpeta")
    parser.add_argument("--mode", choices=["pdf2word", "word2pdf"], default="pdf2word", help="Modo para --batch (default: pdf2word)")
    parser.add_argument("--recursive", action="store_true", help="Incluir subcarpetas en --batch")
    parser.add_argument("--silent", action="store_true", help="No abrir ventana (solo CLI)")

    args, unknown = parser.parse_known_args()

    if args.setup_context_menu:
        from utils.context_menu import add_context_menu
        add_context_menu()
        return
    if args.remove_context_menu:
        from utils.context_menu import remove_context_menu
        remove_context_menu()
        return

    # CLI tools that don't need the GUI
    if any([args.info, args.compress, args.sanitize, args.decrypt,
            args.merge, args.split, args.batch]):
        handled = _run_cli_tool(args)
        if handled:
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
