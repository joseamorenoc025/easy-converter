import win32com.client
import sys

class WordChecker:
    @staticmethod
    def is_word_installed() -> bool:
        """
        Verifica si Microsoft Word está instalado y es accesible vía COM.
        """
        if sys_platform := sys.platform != "win32":
            return False
            
        try:
            # Intentar crear una instancia de Word sin mostrar la ventana
            word = win32com.client.GetActiveObject("Word.Application")
            return True
        except Exception:
            try:
                word = win32com.client.Dispatch("Word.Application")
                # Si llegamos aquí, Word está instalado. Cerramos la instancia creada.
                word.Quit()
                return True
            except Exception:
                return False

    @staticmethod
    def check_word_or_fail():
        """Lanza WordMissingError si Word no está disponible"""
        from core.error_handler import WordMissingError
        if not WordChecker.is_word_installed():
            raise WordMissingError("Microsoft Word no está instalado o no se puede acceder vía COM.")
