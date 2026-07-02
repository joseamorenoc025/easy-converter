"""
Controlador principal de la aplicación.
Orquesta la lógica de negocio separada de la UI.
Implementa el patrón Controller para MVC.
"""
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

from core.interfaces import (
    IConverter,
    IQueueManager,
    IConfigManager,
    IWorkflowEngine,
    IPlatformService,
    IViewCallback,
    ConversionJob,
    ConversionStatus,
)
from utils.security import is_safe_path, validate_file_magic


@dataclass
class AppSettings:
    """Configuración centralizada de la aplicación."""
    max_queue_size: int = 10
    max_history_items: int = 20  # Por defecto, configurable hasta 100
    enable_notifications: bool = True
    auto_start_watch: bool = False
    default_profile: str = "default"


class AppController:
    """
    Controlador principal que coordina todas las operaciones de la aplicación.
    
    Este clase actúa como intermediario entre la UI (View) y los módulos de negocio (Model),
    aplicando inyección de dependencias para facilitar testing y mantenimiento.
    """
    
    def __init__(
        self,
        converter: IConverter,
        queue_manager: IQueueManager,
        config_manager: IConfigManager,
        workflow_engine: IWorkflowEngine,
        platform_service: IPlatformService,
        view_callback: Optional[IViewCallback] = None,
    ):
        self._converter = converter
        self._queue_manager = queue_manager
        self._config_manager = config_manager
        self._workflow_engine = workflow_engine
        self._platform_service = platform_service
        self._view_callback = view_callback
        
        self._settings = AppSettings()
        self._conversion_history: List[Dict] = []
        self._active_jobs: Dict[str, ConversionJob] = {}
        
        # Registrar callback de progreso en el queue manager
        if self._view_callback:
            self._queue_manager.register_progress_callback(self._on_progress_update)
    
    @property
    def settings(self) -> AppSettings:
        """Obtiene la configuración actual."""
        return self._settings
    
    @property
    def conversion_history(self) -> List[Dict]:
        """Obtiene el historial de conversiones (máximo max_history_items)."""
        return self._conversion_history[-self._settings.max_history_items:]
    
    def _notify_error(self, message: str, critical: bool = False):
        """Notifica un error a la vista si hay callback registrado."""
        if self._view_callback:
            self._view_callback.on_error(message, critical)
    
    def _notify_success(self, message: str):
        """Notifica un éxito a la vista si hay callback registrado."""
        if self._view_callback:
            self._view_callback.on_success(message)
    
    def _on_progress_update(self, job_id: str, progress: float):
        """Callback interno para actualizaciones de progreso."""
        if job_id in self._active_jobs:
            self._active_jobs[job_id].progress = progress
            
        if self._view_callback:
            self._view_callback.update_progress(job_id, progress)
    
    def validate_file_for_conversion(self, file_path: Path) -> tuple[bool, str]:
        """
        Valida que un archivo sea seguro y válido para conversión.
        
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_de_error_o_exito)
        """
        # Validar que el archivo exista (antes que seguridad, para mejor msg de error)
        if not file_path.exists():
            return False, f"El archivo no existe: {file_path}"
        
        # Validar que el path sea seguro (entorno local del usuario)
        if not is_safe_path(file_path):
            return False, f"El archivo está fuera del entorno local permitido: {file_path}"
        
        # Validar magic numbers
        ext = file_path.suffix.lower()
        expected = 'pdf' if ext == '.pdf' else ('docx' if ext in ['.docx', '.doc'] else '')
        is_valid, error_msg = validate_file_magic(file_path, expected)
        if not is_valid:
            return False, error_msg
        
        return True, "Archivo válido para conversión"
    
    def queue_conversion(
        self,
        source_path: Path,
        conversion_type: str,
        target_path: Optional[Path] = None,
    ) -> tuple[bool, str, Optional[str]]:
        """
        Encola un trabajo de conversión.
        
        Args:
            source_path: Ruta del archivo origen
            conversion_type: 'pdf2word' o 'word2pdf'
            target_path: Ruta de destino (opcional, se genera si es None)
            
        Returns:
            Tuple[bool, str, Optional[str]]: (éxito, mensaje, job_id)
        """
        # Validar archivo
        is_valid, validation_msg = self.validate_file_for_conversion(source_path)
        if not is_valid:
            self._notify_error(validation_msg)
            return False, validation_msg, None
        
        # Generar target path si no se proporcionó
        if target_path is None:
            if conversion_type == "pdf2word":
                target_path = source_path.with_suffix(".docx")
            else:
                target_path = source_path.with_suffix(".pdf")
        
        # Crear job
        job_id = str(uuid.uuid4())[:8]
        job = ConversionJob(
            id=job_id,
            source_path=source_path,
            target_path=target_path,
            conversion_type=conversion_type,
            status=ConversionStatus.PENDING,
            created_at=time.time(),
        )
        
        # Encolar
        added_to_primary = self._queue_manager.add_job(job)
        
        if added_to_primary:
            job.status = ConversionStatus.QUEUED
            self._active_jobs[job_id] = job
            
            if self._view_callback:
                self._view_callback.on_job_status_changed(job)
                self._view_callback.on_queue_stats_updated(self._queue_manager.get_stats())
            
            return True, f"Trabajo {job_id} encolado exitosamente", job_id
        else:
            job.status = ConversionStatus.WAITING
            self._active_jobs[job_id] = job
            
            if self._view_callback:
                self._view_callback.on_job_status_changed(job)
                self._view_callback.on_queue_stats_updated(self._queue_manager.get_stats())
            
            msg = f"Trabajo {job_id} en cola de espera (cola principal llena)"
            self._notify_success(msg)
            return True, msg, job_id
    
    def cancel_job(self, job_id: str) -> tuple[bool, str]:
        """Cancela un trabajo en curso."""
        if job_id not in self._active_jobs:
            return False, f"Trabajo {job_id} no encontrado"
        
        job = self._active_jobs[job_id]
        
        if job.status in [ConversionStatus.COMPLETED, ConversionStatus.FAILED]:
            return False, f"No se puede cancelar un trabajo {job.status.value}"
        
        # Intentar cancelar en el converter
        if job.status == ConversionStatus.PROCESSING:
            self._converter.cancel_current_conversion()
        
        job.status = ConversionStatus.FAILED
        job.error_message = "Cancelado por el usuario"
        job.completed_at = time.time()
        
        # Mover a historial
        self._add_to_history(job)
        del self._active_jobs[job_id]
        
        if self._view_callback:
            self._view_callback.on_job_status_changed(job)
        
        return True, f"Trabajo {job_id} cancelado"
    
    def _add_to_history(self, job: ConversionJob):
        """Añade un trabajo completado al historial."""
        history_entry = {
            "id": job.id,
            "source": str(job.source_path),
            "target": str(job.target_path) if job.target_path else None,
            "type": job.conversion_type,
            "status": job.status.value,
            "progress": job.progress,
            "error": job.error_message,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
        }
        
        self._conversion_history.append(history_entry)
        
        # Limitar historial
        max_history = min(self._settings.max_history_items, 100)
        if len(self._conversion_history) > max_history:
            self._conversion_history = self._conversion_history[-max_history:]
    
    def apply_workflow_to_file(self, file_path: Path, profile_name: str) -> tuple[bool, str]:
        """Aplica un flujo de trabajo (reglas) a un archivo."""
        is_valid, validation_msg = self.validate_file_for_conversion(file_path)
        if not is_valid:
            return False, validation_msg
        
        success, result_msg = self._workflow_engine.apply_rules(file_path, profile_name)
        
        if success:
            self._notify_success(f"Flujo '{profile_name}' aplicado: {result_msg}")
        else:
            self._notify_error(f"Error al aplicar flujo: {result_msg}")
        
        return success, result_msg
    
    def get_available_profiles(self) -> List[str]:
        """Obtiene la lista de perfiles de flujo de trabajo disponibles."""
        return self._workflow_engine.get_profiles()
    
    def is_word_installed(self) -> bool:
        """Verifica si Microsoft Word está instalado."""
        return self._platform_service.is_word_installed()
    
    def get_tesseract_path(self) -> Optional[Path]:
        """Obtiene la ruta de Tesseract OCR."""
        return self._platform_service.get_tesseract_path()
    
    def toggle_context_menu(self, enabled: bool) -> tuple[bool, str]:
        """Activa o desactiva el menú contextual."""
        success, msg = self._platform_service.register_context_menu(enabled)
        
        if success:
            state = "activado" if enabled else "desactivado"
            self._notify_success(f"Menú contextual {state}")
        else:
            self._notify_error(msg, critical=True)
        
        return success, msg
    
    def send_notification(self, title: str, message: str):
        """Envía una notificación al usuario."""
        if self._settings.enable_notifications:
            self._platform_service.send_notification(title, message)
    
    def update_setting(self, key: str, value):
        """Actualiza una configuración y la persiste."""
        if hasattr(self._settings, key):
            setattr(self._settings, key, value)
            self._config_manager.set(key, value)
            self._config_manager.save()
        else:
            raise ValueError(f"Configuración desconocida: {key}")
    
    def get_queue_stats(self) -> dict:
        """Obtiene estadísticas actuales de las colas."""
        return self._queue_manager.get_stats()
    
    def get_active_jobs(self) -> Dict[str, ConversionJob]:
        """Obtiene los trabajos activos."""
        return self._active_jobs.copy()

    def batch_convert_folder(
        self, folder_path: Path, conversion_type: str = "pdf2word", recursive: bool = False
    ) -> tuple:
        """
        Convierte todos los archivos compatibles de una carpeta.

        Args:
            folder_path: Carpeta fuente.
            conversion_type: 'pdf2word' o 'word2pdf'.
            recursive: Si True, incluye subcarpetas.

        Returns:
            Tuple[bool, str, List[str]]: (éxito, mensaje, job_ids)
        """
        if not folder_path.is_dir():
            return False, f"No es una carpeta válida: {folder_path}", []

        extensions: Tuple[str, ...]
        if conversion_type == "pdf2word":
            extensions = (".pdf",)
        elif conversion_type == "word2pdf":
            extensions = (".docx", ".doc")
        else:
            return False, f"Tipo de conversión desconocido: {conversion_type}", []

        files: List[Path] = []
        if recursive:
            for ext in extensions:
                files.extend(folder_path.rglob(f"*{ext}"))
        else:
            for ext in extensions:
                files.extend(folder_path.glob(f"*{ext}"))

        files = [f for f in files if f.is_file()]
        if not files:
            return False, "No se encontraron archivos compatibles", []

        job_ids = []
        queued = 0
        failed = 0
        for f in files:
            success, msg, job_id = self.queue_conversion(f, conversion_type)
            if success and job_id:
                job_ids.append(job_id)
                queued += 1
            else:
                failed += 1

        summary = f"Encolados: {queued} | Fallidos: {failed} | Total: {len(files)}"
        self._notify_success(f"Lote: {summary}")
        return True, summary, job_ids
