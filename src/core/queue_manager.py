import threading
import time as _time
from queue import Queue, Full, Empty
from dataclasses import dataclass
from typing import List, Callable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

RETRY_DELAYS = {0: 2, 1: 5, 2: 15}  # retries 0/1/2 → seconds


@dataclass
class QueueItem:
    file_path: Path
    mode: str  # 'pdf2word' o 'word2pdf'
    status: str = "pending"  # pending, running, success, failed, waiting_secondary, retry_pending
    progress: int = 0
    message: str = "En cola"
    result_path: str = None
    workflow_profile: str = None
    use_ocr: bool = False
    retry_count: int = 0
    max_retries: int = 3
    last_error: str = ""
    next_retry_at: float = 0.0  # timestamp for scheduled retry

class ConversionQueue:
    def __init__(self, worker_func: Callable, on_queue_update: Callable = None, max_size: int = 10):
        """
        Inicializa la cola de conversiones con soporte para cola secundaria y reintentos.
        """
        self.queue: Queue = Queue(maxsize=max_size)
        self.secondary_queue: List[QueueItem] = []  # Cola secundaria (espera)
        self.items: List[QueueItem] = []
        self.worker_func = worker_func
        self.on_queue_update = on_queue_update
        self.is_running = False
        self._lock = threading.Lock()
        self._max_size = max_size
        
        # Evento para notificar cuando hay espacio en la cola principal
        self._space_available = threading.Condition(self._lock)
        
        # Retry timer threads
        self._retry_timers: dict = {}
        self._retry_lock = threading.Lock()

    def add_item(self, file_path: Path, mode: str, workflow_profile: str = None, use_ocr: bool = False) -> tuple[bool, str]:
        """
        Añade un item a la cola. Si la cola principal está llena, lo mueve a la secundaria.
        
        Returns:
            Tuple[bool, str]: (Éxito, Mensaje descriptivo)
        """
        with self._lock:
            item = QueueItem(file_path=file_path, mode=mode, workflow_profile=workflow_profile, use_ocr=use_ocr)
            self.items.append(item)
            
            # Intentar añadir a la cola principal
            try:
                # Verificar si hay espacio sin bloquear
                if self.queue.qsize() < self._max_size:
                    self.queue.put(item)
                    item.message = "En procesamiento"
                    logger.info(f"Archivo añadido a cola principal: {file_path.name}")
                else:
                    # Cola llena, usar cola secundaria
                    self.secondary_queue.append(item)
                    item.status = "waiting_secondary"
                    item.message = f"En espera (cola llena). Posición: {len(self.secondary_queue)}"
                    logger.info(f"Archivo añadido a cola secundaria: {file_path.name}. Tamaño cola: {len(self.secondary_queue)}")
            except Full:
                # Fallback por si acaso
                self.secondary_queue.append(item)
                item.status = "waiting_secondary"
                item.message = "En espera (cola llena)"
            
            if self.on_queue_update:
                self.on_queue_update()
            
            if not self.is_running:
                self.is_running = True
                thread = threading.Thread(target=self._process_queue, daemon=True)
                thread.start()
                
            return True, item.message

    def _promote_from_secondary(self):
        """Mueve items de la cola secundaria a la principal si hay espacio."""
        while self.secondary_queue and self.queue.qsize() < self._max_size:
            item = self.secondary_queue.pop(0)
            item.status = "pending"
            item.message = "Movido a procesamiento"
            self.queue.put(item)
            logger.info(f"Archivo promovido de cola secundaria a principal: {item.file_path.name}")
        
        # Notificar que hay espacio liberado
        self._space_available.notify_all()

    def _process_queue(self):
        while True:
            with self._lock:
                if self.queue.empty() and not self.secondary_queue:
                    self.is_running = False
                    break
                    
                # Si la cola principal está vacía pero hay secundaria, promover items
                if self.queue.empty() and self.secondary_queue:
                    self._promote_from_secondary()
            
            try:
                # Obtener item con timeout para permitir verificar la cola secundaria periódicamente
                item = self.queue.get(timeout=0.5)
            except Empty:  # noqa: E722 - Timeout esperado para polling
                continue  # Timeout, volver a verificar estado
            
            with self._lock:
                item.status = "running"
                item.message = "Iniciando..."
            
            if self.on_queue_update:
                self.on_queue_update()

            try:
                self.worker_func(item)
                with self._lock:
                    item.status = "success"
                    item.progress = 100
                    item.message = "Completado"
            except Exception as e:
                with self._lock:
                    item.last_error = str(e)
                    if item.retry_count < item.max_retries:
                        delay = RETRY_DELAYS.get(item.retry_count, 15)
                        item.status = "retry_pending"
                        item.message = f"Reintento {item.retry_count + 1}/{item.max_retries} en {delay}s"
                        item.next_retry_at = _time.time() + delay
                        self._schedule_retry(item, delay)
                    else:
                        item.status = "failed"
                        item.message = f"Error (sin reintentos): {str(e)}"
                logger.error(f"Error procesando {item.file_path}: {e}", exc_info=True)
            
            if self.on_queue_update:
                self.on_queue_update()
            
            self.queue.task_done()
            
            # Después de completar un item, intentar promover desde secundaria
            with self._lock:
                if self.secondary_queue:
                    self._promote_from_secondary()
        
        if self.on_queue_update:
            self.on_queue_update()

    def _schedule_retry(self, item: QueueItem, delay: float):
        """Programa un reintento después de `delay` segundos."""
        def _do_retry():
            with self._lock:
                item.retry_count += 1
                item.status = "pending"
                item.message = f"Reintento {item.retry_count}/{item.max_retries}"
                try:
                    if self.queue.qsize() < self._max_size:
                        self.queue.put(item)
                    else:
                        self.secondary_queue.append(item)
                        item.status = "waiting_secondary"
                        item.message = "Reintento en cola de espera"
                except Full:
                    self.secondary_queue.append(item)
                    item.status = "waiting_secondary"
            if self.on_queue_update:
                self.on_queue_update()
            if not self.is_running:
                self.is_running = True
                thread = threading.Thread(target=self._process_queue, daemon=True)
                thread.start()

        timer = threading.Timer(delay, _do_retry)
        timer.daemon = True
        with self._retry_lock:
            self._retry_timers[id(item)] = timer
        timer.start()

    def retry_item(self, item: QueueItem) -> bool:
        """Reintenta un item que falló o está en retry_pending."""
        with self._lock:
            if item.status not in ("failed", "retry_pending"):
                return False
            if item.retry_count >= item.max_retries:
                return False
            delay = RETRY_DELAYS.get(item.retry_count, 15)
            item.status = "retry_pending"
            item.message = f"Reintento {item.retry_count + 1}/{item.max_retries} en {delay}s"
            item.next_retry_at = _time.time() + delay
            self._schedule_retry(item, delay)
        if self.on_queue_update:
            self.on_queue_update()
        return True

    def remove_item(self, item):
        with self._lock:
            if item in self.items:
                self.items.remove(item)
                self._cancel_retry_timer(item)
        if self.on_queue_update:
            self.on_queue_update()

    def _cancel_retry_timer(self, item: QueueItem):
        """Cancela el timer de reintento de un item si existe."""
        with self._retry_lock:
            timer = self._retry_timers.pop(id(item), None)
        if timer:
            timer.cancel()

    def clear_completed(self):
        with self._lock:
            cleared = [item for item in self.items if item.status in ("success", "failed")]
            self.items = [item for item in self.items if item.status not in ("success", "failed")]
            for item in cleared:
                self._cancel_retry_timer(item)
        if self.on_queue_update:
            self.on_queue_update()

    def get_all_items(self):
        with self._lock:
            return list(self.items)
    
    def get_queue_stats(self) -> dict:
        """Obtiene estadísticas de las colas."""
        with self._lock:
            return {
                'primary_count': self.queue.qsize(),
                'secondary_count': len(self.secondary_queue),
                'total_items': len(self.items),
                'max_size': self._max_size,
                'is_running': self.is_running
            }
    
    def get_secondary_queue(self) -> List[QueueItem]:
        """Obtiene una copia de la cola secundaria."""
        with self._lock:
            return list(self.secondary_queue)
