"""
Interfaces abstractas para definir contratos entre módulos.
Esto permite desacoplar la implementación concreta de la lógica de negocio y la UI.
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class ConversionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUEUED = "queued"
    WAITING = "waiting"  # En cola secundaria


@dataclass
class ConversionJob:
    """Representa un trabajo de conversión."""
    id: str
    source_path: Path
    target_path: Optional[Path]
    conversion_type: str  # 'pdf2word' o 'word2pdf'
    status: ConversionStatus
    progress: float = 0.0
    error_message: Optional[str] = None
    created_at: float = 0.0
    completed_at: Optional[float] = None


class IConverter(ABC):
    """Interfaz para los motores de conversión."""
    
    @abstractmethod
    def convert_pdf_to_word(self, pdf_path: Path, output_path: Path) -> Tuple[bool, str]:
        """Convierte un PDF a Word."""
        pass

    @abstractmethod
    def convert_word_to_pdf(self, word_path: Path, output_path: Path) -> Tuple[bool, str]:
        """Convierte un Word a PDF."""
        pass

    @abstractmethod
    def cancel_current_conversion(self) -> bool:
        """Cancela la conversión en curso si la hay."""
        pass


class IQueueManager(ABC):
    """Interfaz para el gestor de colas."""
    
    @abstractmethod
    def add_job(self, job: ConversionJob) -> bool:
        """Añade un trabajo a la cola. Retorna False si se usa la cola secundaria."""
        pass

    @abstractmethod
    def get_next_job(self) -> Optional[ConversionJob]:
        """Obtiene el siguiente trabajo disponible."""
        pass

    @abstractmethod
    def mark_job_completed(self, job_id: str, success: bool, error_msg: Optional[str] = None):
        """Marca un trabajo como completado."""
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """Retorna estadísticas de las colas."""
        pass

    @abstractmethod
    def register_progress_callback(self, callback: Callable[[str, float], None]):
        """Registra un callback para actualizaciones de progreso."""
        pass


class IConfigManager(ABC):
    """Interfaz para la gestión de configuración."""
    
    @abstractmethod
    def get(self, key: str, default=None):
        """Obtiene un valor de configuración."""
        pass

    @abstractmethod
    def set(self, key: str, value):
        """Establece un valor de configuración."""
        pass

    @abstractmethod
    def save(self) -> bool:
        """Guarda la configuración en disco."""
        pass

    @abstractmethod
    def get_all(self) -> dict:
        """Retorna toda la configuración."""
        pass


class IWorkflowEngine(ABC):
    """Interfaz para el motor de flujos de trabajo."""
    
    @abstractmethod
    def apply_rules(self, file_path: Path, profile_name: str) -> Tuple[bool, str]:
        """Aplica las reglas de un perfil a un archivo."""
        pass

    @abstractmethod
    def get_profiles(self) -> List[str]:
        """Retorna la lista de perfiles disponibles."""
        pass

    @abstractmethod
    def validate_profile(self, profile_name: str) -> Tuple[bool, str]:
        """Valida si un perfil existe y es válido."""
        pass


class IPlatformService(ABC):
    """Interfaz para servicios específicos de plataforma (Windows, Linux, Mac)."""
    
    @abstractmethod
    def register_context_menu(self, enabled: bool) -> Tuple[bool, str]:
        """Registra o elimina el menú contextual."""
        pass

    @abstractmethod
    def is_word_installed(self) -> bool:
        """Verifica si Microsoft Word está instalado."""
        pass

    @abstractmethod
    def send_notification(self, title: str, message: str) -> bool:
        """Envía una notificación nativa del sistema."""
        pass

    @abstractmethod
    def get_tesseract_path(self) -> Optional[Path]:
        """Obtiene la ruta de instalación de Tesseract OCR."""
        pass


class IViewCallback(ABC):
    """Interfaz para que el Controller se comunique con la View."""
    
    @abstractmethod
    def on_job_status_changed(self, job: ConversionJob):
        """Notifica cambio de estado de un trabajo."""
        pass

    @abstractmethod
    def on_queue_stats_updated(self, stats: dict):
        """Notifica actualización de estadísticas de cola."""
        pass

    @abstractmethod
    def on_error(self, message: str, critical: bool = False):
        """Notifica un error al usuario."""
        pass

    @abstractmethod
    def on_success(self, message: str):
        """Notifica un éxito al usuario."""
        pass

    @abstractmethod
    def update_progress(self, job_id: str, progress: float):
        """Actualiza la barra de progreso de un trabajo."""
        pass
