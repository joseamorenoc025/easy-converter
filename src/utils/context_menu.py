import sys
import winreg
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def add_context_menu() -> tuple[bool, str]:
    """
    Añade opciones al menú contextual de Windows para archivos .pdf y .docx.
    Maneja errores de permisos y notifica adecuadamente.
    
    Returns:
        Tuple[bool, str]: (Éxito, Mensaje descriptivo)
    """
    if sys.platform != "win32":
        logger.warning("Menú contextual solo disponible en Windows")
        return False, "Solo disponible en Windows"

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

    try:
        for ext, (label, cmd) in commands.items():
            key_path = f"Software\\Classes\\SystemFileAssociations\\{ext}\\shell\\EasyConverter"
            
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, label)
                    
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{key_path}\\command") as key:
                    winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
            except PermissionError as pe:
                logger.error(f"Permiso denegado para extensión {ext}: {pe}")
                return False, f"Permiso denegado para modificar el registro. Ejecuta como administrador."
            except OSError as oe:
                logger.error(f"Error de OS para extensión {ext}: {oe}")
                return False, f"Error de sistema al modificar registro: {oe}"
        
        logger.info("Menú contextual añadido con éxito.")
        return True, "Menú contextual añadido correctamente"
    except Exception as e:
        logger.error(f"Error general al añadir menú contextual: {e}", exc_info=True)
        return False, f"Error inesperado: {str(e)}"

def remove_context_menu():
    """Elimina las entradas del registro."""
    if sys.platform != "win32":
        return False, "Solo disponible en Windows"
    
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
        logger.info("Menú contextual eliminado con éxito.")
        return True, "Menú contextual eliminado correctamente"
    except Exception as e:
        logger.error(f"Error al eliminar menú contextual: {e}", exc_info=True)
        return False, f"Error: {str(e)}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    
    if args.install:
        success, msg = add_context_menu()
        print(msg)
    elif args.uninstall:
        success, msg = remove_context_menu()
        print(msg)
