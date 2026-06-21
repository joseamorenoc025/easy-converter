import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.observers.api import ObservedWatch
from typing import Callable, Dict

# Configuración de logging
logger = logging.getLogger(__name__)

class SmartFolderHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[Path], None]):
        self.callback = callback
        self.last_triggered: Dict[str, float] = {}

    def on_created(self, event):
        if event.is_directory:
            return
        self._handle_event(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self._handle_event(event.dest_path)

    def _wait_until_ready(self, path: Path, timeout: int = 10) -> bool:
        """
        Espera activa con backoff para asegurar que el archivo no esté bloqueado
        por el sistema operativo (útil para archivos grandes o descargas).
        """
        start_time = time.monotonic()
        retries = 0
        while time.time() - start_time < timeout:
            try:
                # Intentamos abrir el archivo en modo exclusivo (lectura/escritura)
                # Si falla, es que el SO aún lo está escribiendo.
                with open(path, 'rb+'):
                    logger.debug(f"Archivo {path.name} está listo para procesar.")
                    return True
            except (IOError, OSError):
                retries += 1
                wait_time = min(0.1 * (2 ** retries), 2.0) # Backoff exponencial
                time.sleep(wait_time)
        
        logger.warning(f"Timeout esperando al archivo {path.name}. Puede estar bloqueado.")
        return False

    def _handle_event(self, file_path_str: str):
        path = Path(file_path_str)
        ext = path.suffix.lower()
        
        # Ignorar archivos temporales de Word (~$...) y archivos ya convertidos por nosotros
        if path.name.startswith("~$") or "_CONVERTIDO_" in path.name:
            return

        if ext in ['.pdf', '.docx', '.doc']:
            # Debounce: Evitar disparos duplicados (ventana de 2s con time.monotonic)
            now = time.monotonic()
            if file_path_str in self.last_triggered and now - self.last_triggered[file_path_str] < 2.0:
                return
            
            self.last_triggered[file_path_str] = now
            
            # Verificación de bloqueo (Race Condition Fix)
            if self._wait_until_ready(path):
                self.callback(path)
            else:
                logger.error(f"No se pudo procesar {path.name}: Archivo bloqueado por el sistema.")

class SmartWatcher:
    def __init__(self, callback: Callable[[Path], None]):
        self.callback = callback
        self.observer = Observer()
        self.watch_paths: Dict[str, ObservedWatch] = {}

    def add_watch(self, path: str):
        if path not in self.watch_paths:
            handler = SmartFolderHandler(self.callback)
            watch = self.observer.schedule(handler, path, recursive=False)
            self.watch_paths[path] = watch
            logger.info(f"Vigilando carpeta: {path}")

    def remove_watch(self, path: str):
        if path in self.watch_paths:
            self.observer.unschedule(self.watch_paths[path])
            del self.watch_paths[path]
            logger.info(f"Dejado de vigilar carpeta: {path}")

    def start(self):
        if not self.observer.is_alive():
            self.observer.start()
            logger.info("Servidor de vigilancia iniciado.")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        logger.info("Servidor de vigilancia detenido.")
