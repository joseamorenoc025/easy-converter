"""
Servicios específicos de plataforma Windows.
Implementa IPlatformService para aislar dependencias de win32com.
"""
import sys
import importlib.util
from pathlib import Path
from typing import Optional, Tuple

from core.interfaces import IPlatformService


class WindowsPlatformService(IPlatformService):
    """Implementación de servicios de plataforma para Windows."""
    
    def __init__(self):
        self._winreg_available = False
        self._win32com_available = False
        
        # Verificar disponibilidad de módulos Windows sin importarlos
        if sys.platform == "win32":
            self._winreg_available = importlib.util.find_spec("winreg") is not None
            self._win32com_available = importlib.util.find_spec("win32com.client") is not None
    
    def register_context_menu(self, enabled: bool) -> Tuple[bool, str]:
        """Registra o elimina el menú contextual en Windows."""
        if sys.platform != "win32":
            return False, "El menú contextual solo está disponible en Windows"
        
        if not self._winreg_available:
            return False, "Módulo winreg no disponible"
        
        import winreg
        
        try:
            # Clave para el menú contextual de archivos
            base_key = r"*\shell\EasyConverter"
            
            if enabled:
                # Crear clave principal
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, base_key)
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Convertir con Easy Converter")
                winreg.CloseKey(key)
                
                # Crear comando
                cmd_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, base_key + r"\command")
                exe_path = sys.executable
                script_path = Path(__file__).parent.parent / "main.py"
                command = f'"{exe_path}" "{script_path}" --convert "%1"'
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)
                winreg.CloseKey(cmd_key)
                
                return True, "Menú contextual registrado exitosamente"
            else:
                # Eliminar clave
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base_key + r"\command")
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base_key)
                    return True, "Menú contextual eliminado"
                except FileNotFoundError:
                    return True, "El menú contextual ya no existía"
                    
        except PermissionError as e:
            return False, f"Permisos insuficientes para modificar el registro: {str(e)}"
        except OSError as e:
            return False, f"Error al acceder al registro de Windows: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def is_word_installed(self) -> bool:
        """Verifica si Microsoft Word está instalado."""
        if sys.platform != "win32":
            return False
        
        if not self._win32com_available:
            return False
        
        try:
            import win32com.client
            # Intentar crear instancia de Word
            word = win32com.client.Dispatch("Word.Application")
            word.Quit()
            return True
        except Exception:
            return False
    
    def send_notification(self, title: str, message: str) -> bool:
        """Envía una notificación nativa de Windows."""
        if sys.platform != "win32":
            print(f"[NOTIFICATION] {title}: {message}")
            return True
        
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5)
            return True
        except ImportError:
            # Fallback si win10toast no está disponible
            print(f"[NOTIFICATION] {title}: {message}")
            return True
        except Exception:
            return False
    
    def get_tesseract_path(self) -> Optional[Path]:
        """Obtiene la ruta de instalación de Tesseract OCR."""
        if sys.platform != "win32":
            # En Linux/Mac, verificar rutas comunes
            common_paths = [
                Path("/usr/bin/tesseract"),
                Path("/usr/local/bin/tesseract"),
                Path("/opt/homebrew/bin/tesseract"),
            ]
            for path in common_paths:
                if path.exists():
                    return path
            return None
        
        # En Windows, verificar rutas comunes
        common_paths = [
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
            Path(Path.home() / "AppData/Local/Tesseract-OCR/tesseract.exe"),
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        
        # Verificar variable de entorno
        import os
        tesseract_env = os.environ.get("TESSERACT_PATH")
        if tesseract_env:
            tesseract_path = Path(tesseract_env)
            if tesseract_path.exists():
                return tesseract_path
        
        return None


class MockPlatformService(IPlatformService):
    """Implementación mock para testing o plataformas no soportadas."""
    
    def __init__(self, word_installed: bool = True, tesseract_path: Optional[Path] = None):
        self._word_installed = word_installed
        self._tesseract_path = tesseract_path
        self._context_menu_enabled = False
    
    def register_context_menu(self, enabled: bool) -> Tuple[bool, str]:
        self._context_menu_enabled = enabled
        return True, f"Menú contextual {'activado' if enabled else 'desactivado'} (mock)"
    
    def is_word_installed(self) -> bool:
        return self._word_installed
    
    def send_notification(self, title: str, message: str) -> bool:
        print(f"[MOCK NOTIFICATION] {title}: {message}")
        return True
    
    def get_tesseract_path(self) -> Optional[Path]:
        return self._tesseract_path
