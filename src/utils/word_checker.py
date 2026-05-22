import sys
import gc

class WordChecker:
    @staticmethod
    def is_word_installed() -> bool:
        """
        Verifica si Microsoft Word está instalado y es accesible vía COM.
        Implementa limpieza agresiva para evitar procesos zombis.
        """
        if sys.platform != "win32":
            return False
            
        import pythoncom
        import win32com.client
            
        already_initialized = False
        try:
            try:
                pythoncom.CoInitialize()
            except pythoncom.com_error:
                already_initialized = True
                
            # Intentar crear una instancia de Word sin mostrar la ventana
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.Quit()
            
            # Limpieza explícita
            word = None
            gc.collect()
            return True
        except Exception:
            return False
        finally:
            if not already_initialized:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

    @staticmethod
    def check_word_or_fail():
        """Lanza WordMissingError si Word no está disponible"""
        from core.error_handler import WordMissingError
        if not WordChecker.is_word_installed():
            raise WordMissingError("Microsoft Word no está instalado o no se puede acceder vía COM.")
