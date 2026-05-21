import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from appdirs import user_log_dir

class EasyConverterError(Exception):
    """Clase base para excepciones de Easy Converter"""
    def __init__(self, message, context=None):
        super().__init__(message)
        self.context = context

class WordMissingError(EasyConverterError):
    """Error cuando Microsoft Word no está instalado o accesible"""
    pass

class FileCorruptedError(EasyConverterError):
    """Error cuando el archivo de entrada está dañado"""
    pass

class PermissionDeniedError(EasyConverterError):
    """Error de permisos al intentar leer o escribir archivos"""
    pass

class ConversionTimeoutError(EasyConverterError):
    """Error cuando la conversión tarda demasiado"""
    pass

class ErrorHandler:
    def __init__(self, app_name="EasyConverter"):
        self.log_dir = Path(user_log_dir(app_name, "GeminiCLI"))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "error.log"
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger("EasyConverter")
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para archivo (rotativo simple por sesión para este ejemplo)
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def handle(self, error: Exception, context: dict = None) -> str:
        """
        Clasifica el error, loguea el stack trace y retorna un mensaje amigable.
        """
        error_type = type(error).__name__
        context_str = f" | Context: {context}" if context else ""
        
        self.logger.error(f"Captured {error_type}: {str(error)}{context_str}", exc_info=True)

        if isinstance(error, WordMissingError):
            return "No se pudo encontrar Microsoft Word. Es obligatorio para convertir de Word a PDF."
        
        if isinstance(error, FileCorruptedError):
            return "El archivo seleccionado parece estar dañado o no es válido."
        
        if isinstance(error, PermissionDeniedError):
            return "Error de permisos. Asegúrate de que el archivo no esté abierto en otro programa."
        
        if "comtypes" in str(error).lower() or "dispatch" in str(error).lower():
            return "Error de comunicación con Microsoft Word. Intenta reiniciar la aplicación."

        return f"Ocurrió un error inesperado: {str(error)}"

    @staticmethod
    def get_retry_decorator(max_attempts=3, base_delay=1):
        """Decorador para reintentos exponenciales real"""
        import time
        def decorator(func):
            def wrapper(*args, **kwargs):
                attempts = 0
                while attempts < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempts += 1
                        if attempts == max_attempts:
                            raise
                        delay = base_delay * (2 ** (attempts - 1))
                        time.sleep(delay)
                return None
            return wrapper
        return decorator

