import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, List

class SmartFolderHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[Path], None]):
        self.callback = callback
        self.last_triggered = {}

    def on_created(self, event):
        if event.is_directory:
            return
        self._handle_event(event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self._handle_event(event.dest_path)

    def _handle_event(self, file_path_str: str):
        path = Path(file_path_str)
        ext = path.suffix.lower()
        if ext in ['.pdf', '.docx', '.doc']:
            # Evitar disparos duplicados rápidos (algunos programas crean y luego escriben)
            now = time.time()
            if file_path_str in self.last_triggered and now - self.last_triggered[file_path_str] < 1.0:
                return
            
            self.last_triggered[file_path_str] = now
            # Pequeña espera para asegurar que el archivo terminó de escribirse
            time.sleep(0.5)
            self.callback(path)

class SmartWatcher:
    def __init__(self, callback: Callable[[Path], None]):
        self.callback = callback
        self.observer = Observer()
        self.watch_paths = {}

    def add_watch(self, path: str):
        if path not in self.watch_paths:
            handler = SmartFolderHandler(self.callback)
            watch = self.observer.schedule(handler, path, recursive=False)
            self.watch_paths[path] = watch

    def remove_watch(self, path: str):
        if path in self.watch_paths:
            self.observer.unschedule(self.watch_paths[path])
            del self.watch_paths[path]

    def start(self):
        if not self.observer.is_alive():
            self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
