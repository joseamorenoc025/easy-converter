import sys
import winreg
import os
from pathlib import Path

def add_context_menu():
    """
    Añade opciones al menú contextual de Windows para archivos .pdf y .docx.
    """
    if sys.platform != "win32":
        return

    # Ruta al ejecutable
    if getattr(sys, 'frozen', False):
        # Si es un ejecutable (PyInstaller)
        exe_path = f'"{sys.executable}"'
    else:
        # Si es un script de Python (desarrollo)
        python_exe = sys.executable
        main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        exe_path = f'"{python_exe}" "{main_script}"'
    
    # Extensiones y sus comandos
    commands = {
        ".pdf": ("Convertir a Word", f'{exe_path} --pdf2word "%1"'),
        ".docx": ("Convertir a PDF", f'{exe_path} --word2pdf "%1"'),
        ".doc": ("Convertir a PDF", f'{exe_path} --word2pdf "%1"')
    }

    failed = []
    succeeded = []
    for ext, (label, cmd) in commands.items():
        ext_key_path = f"Software\\Classes\\SystemFileAssociations\\{ext}\\shell\\EasyConverter"
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, ext_key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, label)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{ext_key_path}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
            succeeded.append(ext)
        except Exception as e:
            failed.append((ext, str(e)))
    
    if succeeded and not failed:
        print(f"Menú contextual añadido: {', '.join(succeeded)}.")
    elif succeeded and failed:
        print(f"Partial success — registradas: {', '.join(succeeded)}.")
        for ext, err in failed:
            print(f"  {ext}: {err}")
    else:
        print(f"Error al añadir menú contextual.")

def remove_context_menu():
    """Elimina las entradas del registro."""
    if sys.platform != "win32":
        return
    
    extensions = [".pdf", ".docx", ".doc"]
    try:
        for ext in extensions:
            key_path = f"Software\\Classes\\SystemFileAssociations\\{ext}\\shell\\EasyConverter"
            # winreg.DeleteKey no borra recursivamente, hay que borrar subclaves primero
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{key_path}\\command")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except FileNotFoundError:
                pass
        print("Menú contextual eliminado con éxito.")
    except Exception as e:
        print(f"Error al eliminar menú contextual: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    
    if args.install:
        add_context_menu()
    elif args.uninstall:
        remove_context_menu()
