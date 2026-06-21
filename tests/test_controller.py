"""
Tests para el controlador de la aplicación (AppController).
Verifica la inyección de dependencias y la lógica de negocio.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import Mock

from src.core.controller import AppController
from src.core.interfaces import (
    IConverter,
    IQueueManager,
    IConfigManager,
    IWorkflowEngine,
    IViewCallback,
    ConversionJob,
    ConversionStatus,
)
from src.utils.platform_service import MockPlatformService


@pytest.fixture
def mock_converter():
    """Crea un mock del converter."""
    converter = Mock(spec=IConverter)
    converter.convert_pdf_to_word.return_value = (True, "Éxito")
    converter.convert_word_to_pdf.return_value = (True, "Éxito")
    converter.cancel_current_conversion.return_value = True
    return converter


@pytest.fixture
def mock_queue_manager():
    """Crea un mock del queue manager."""
    queue_manager = Mock(spec=IQueueManager)
    queue_manager.add_job.return_value = True  # Por defecto, cola principal disponible
    queue_manager.get_stats.return_value = {
        "primary_queue_size": 0,
        "secondary_queue_size": 0,
        "max_size": 10,
    }
    return queue_manager


@pytest.fixture
def mock_config_manager():
    """Crea un mock del config manager."""
    config_manager = Mock(spec=IConfigManager)
    config_manager.get.return_value = None
    config_manager.set.return_value = None
    config_manager.save.return_value = True
    config_manager.get_all.return_value = {}
    return config_manager


@pytest.fixture
def mock_workflow_engine():
    """Crea un mock del workflow engine."""
    workflow_engine = Mock(spec=IWorkflowEngine)
    workflow_engine.apply_rules.return_value = (True, "Reglas aplicadas")
    workflow_engine.get_profiles.return_value = ["default", "archive", "rename_date"]
    workflow_engine.validate_profile.return_value = (True, "Perfil válido")
    return workflow_engine


@pytest.fixture
def mock_platform_service():
    """Crea un mock del platform service."""
    return MockPlatformService(word_installed=True, tesseract_path=Path("/usr/bin/tesseract"))


@pytest.fixture
def mock_view_callback():
    """Crea un mock del view callback."""
    callback = Mock(spec=IViewCallback)
    return callback


@pytest.fixture
def controller(mock_converter, mock_queue_manager, mock_config_manager, 
               mock_workflow_engine, mock_platform_service, mock_view_callback):
    """Crea una instancia del controller con mocks."""
    return AppController(
        converter=mock_converter,
        queue_manager=mock_queue_manager,
        config_manager=mock_config_manager,
        workflow_engine=mock_workflow_engine,
        platform_service=mock_platform_service,
        view_callback=mock_view_callback,
    )


class TestAppControllerInitialization:
    """Tests para la inicialización del controller."""
    
    def test_controller_creates_with_defaults(self, controller):
        """Verifica que el controller se crea con valores por defecto."""
        assert controller.settings.max_queue_size == 10
        assert controller.settings.max_history_items == 20
        assert controller.settings.enable_notifications is True
        assert len(controller.conversion_history) == 0
        assert len(controller.get_active_jobs()) == 0
    
    def test_controller_registers_progress_callback(self, controller, mock_queue_manager):
        """Verifica que se registra el callback de progreso."""
        mock_queue_manager.register_progress_callback.assert_called_once()


class TestFileValidation:
    """Tests para validación de archivos."""
    
    def test_validate_safe_local_file(self, controller, tmp_path):
        """Valida un archivo en entorno local."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        
        is_valid, msg = controller.validate_file_for_conversion(test_file)
        assert is_valid is True
        assert "válido" in msg.lower()
    
    def test_validate_unsafe_path(self, controller):
        """Rechaza archivos fuera del entorno local."""
        # Usar un path que exista pero esté fuera del entorno permitido
        if os.name == 'nt':
            unsafe_path = Path(os.environ.get('SystemRoot', 'C:\\Windows')) / "System32" / "notepad.exe"
        else:
            unsafe_path = Path("/etc/passwd")
    
        is_valid, msg = controller.validate_file_for_conversion(unsafe_path)
        assert is_valid is False
        assert "fuera del entorno local" in msg
    
    def test_validate_nonexistent_file(self, controller):
        """Rechaza archivos que no existen."""
        nonexistent = Path("/tmp/does_not_exist_12345.pdf")
        
        is_valid, msg = controller.validate_file_for_conversion(nonexistent)
        assert is_valid is False
        assert "no existe" in msg.lower()
    
    def test_validate_invalid_magic_number(self, controller, tmp_path):
        """Rechaza archivos con magic number incorrecto."""
        # Crear un archivo .pdf que no es realmente PDF
        fake_pdf = tmp_path / "fake.pdf"
        fake_pdf.write_text("This is not a PDF file")
        
        is_valid, msg = controller.validate_file_for_conversion(fake_pdf)
        assert is_valid is False
        assert "magic" in msg.lower() or "tipo" in msg.lower()


class TestConversionQueueing:
    """Tests para encolado de conversiones."""
    
    def test_queue_conversion_success(self, controller, tmp_path, mock_queue_manager):
        """Encola una conversión exitosamente."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        
        success, msg, job_id = controller.queue_conversion(
            source_path=test_file,
            conversion_type="pdf2word"
        )
        
        assert success is True
        assert job_id is not None
        assert len(job_id) == 8
        assert "encolado" in msg.lower()
        mock_queue_manager.add_job.assert_called_once()
    
    def test_queue_conversion_with_custom_target(self, controller, tmp_path, mock_queue_manager):
        """Encola una conversión con ruta de destino personalizada."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        custom_target = tmp_path / "custom_output.docx"
        
        success, msg, job_id = controller.queue_conversion(
            source_path=test_file,
            conversion_type="pdf2word",
            target_path=custom_target
        )
        
        assert success is True
        # Verificar que el job fue creado con el target personalizado
        call_args = mock_queue_manager.add_job.call_args[0][0]
        assert call_args.target_path == custom_target
    
    def test_queue_conversion_validation_fails(self, controller, mock_queue_manager):
        """No encola si la validación falla."""
        unsafe_path = Path("/root/unsafe/file.pdf")
        
        success, msg, job_id = controller.queue_conversion(
            source_path=unsafe_path,
            conversion_type="pdf2word"
        )
        
        assert success is False
        assert job_id is None
        mock_queue_manager.add_job.assert_not_called()
    
    def test_queue_conversion_secondary_queue(self, controller, tmp_path, mock_queue_manager):
        """Encola en secundaria cuando la principal está llena."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        
        # Simular cola principal llena
        mock_queue_manager.add_job.return_value = False
        
        success, msg, job_id = controller.queue_conversion(
            source_path=test_file,
            conversion_type="pdf2word"
        )
        
        assert success is True
        assert job_id is not None
        assert "cola de espera" in msg.lower()
        
        # Verificar que el job está en estado WAITING
        active_jobs = controller.get_active_jobs()
        assert active_jobs[job_id].status == ConversionStatus.WAITING


class TestJobCancellation:
    """Tests para cancelación de trabajos."""
    
    def test_cancel_active_job(self, controller, tmp_path, mock_converter):
        """Cancela un trabajo activo."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        
        # Encolar un trabajo
        success, msg, job_id = controller.queue_conversion(
            source_path=test_file,
            conversion_type="pdf2word"
        )
        assert success is True
        
        # Marcar como processing manualmente para el test
        controller._active_jobs[job_id].status = ConversionStatus.PROCESSING
        
        # Cancelar
        cancel_success, cancel_msg = controller.cancel_job(job_id)
        
        assert cancel_success is True
        assert "cancelado" in cancel_msg.lower()
        mock_converter.cancel_current_conversion.assert_called_once()
        
        # Verificar que ya no está en activos
        assert job_id not in controller.get_active_jobs()
        
        # Verificar que está en historial
        history = controller.conversion_history
        assert len(history) > 0
        assert history[-1]["id"] == job_id
        assert history[-1]["status"] == "failed"
        assert history[-1]["error"] == "Cancelado por el usuario"
    
    def test_cancel_nonexistent_job(self, controller):
        """Fallar al cancelar trabajo inexistente."""
        success, msg = controller.cancel_job("nonexistent")
        
        assert success is False
        assert "no encontrado" in msg.lower()
    
    def test_cancel_completed_job(self, controller, tmp_path):
        """No permite cancelar trabajo completado."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        
        # Encolar y completar manualmente
        success, msg, job_id = controller.queue_conversion(
            source_path=test_file,
            conversion_type="pdf2word"
        )
        controller._active_jobs[job_id].status = ConversionStatus.COMPLETED
        
        cancel_success, cancel_msg = controller.cancel_job(job_id)
        
        assert cancel_success is False
        assert "no se puede cancelar" in cancel_msg.lower()


class TestHistoryManagement:
    """Tests para gestión del historial."""
    
    def test_history_limit_default(self, controller, tmp_path):
        """El historial respeta el límite por defecto (20)."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        
        # Añadir 25 trabajos al historial
        for i in range(25):
            job = ConversionJob(
                id=f"job{i:02d}",
                source_path=test_file,
                target_path=test_file.with_suffix(".docx"),
                conversion_type="pdf2word",
                status=ConversionStatus.COMPLETED,
                created_at=1000 + i,
                completed_at=2000 + i,
            )
            controller._add_to_history(job)
        
        # Debería tener máximo 20 items
        assert len(controller.conversion_history) == 20
        # Los primeros deberían haber sido eliminados
        assert controller.conversion_history[0]["id"] == "job05"
    
    def test_history_limit_configurable(self, controller, tmp_path):
        """El historial respeta el límite configurable."""
        controller.update_setting("max_history_items", 5)
        
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        
        # Añadir 10 trabajos
        for i in range(10):
            job = ConversionJob(
                id=f"job{i:02d}",
                source_path=test_file,
                target_path=test_file.with_suffix(".docx"),
                conversion_type="pdf2word",
                status=ConversionStatus.COMPLETED,
                created_at=1000 + i,
                completed_at=2000 + i,
            )
            controller._add_to_history(job)
        
        assert len(controller.conversion_history) == 5
        assert controller.conversion_history[0]["id"] == "job05"
    
    def test_history_max_cap_at_100(self, controller, tmp_path):
        """El historial tiene tope máximo de 100 aunque se configure más."""
        controller.update_setting("max_history_items", 150)
        
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        
        # Añadir 120 trabajos
        for i in range(120):
            job = ConversionJob(
                id=f"job{i:03d}",
                source_path=test_file,
                target_path=test_file.with_suffix(".docx"),
                conversion_type="pdf2word",
                status=ConversionStatus.COMPLETED,
                created_at=1000 + i,
                completed_at=2000 + i,
            )
            controller._add_to_history(job)
        
        # Debería respetar el tope de 100
        assert len(controller.conversion_history) == 100


class TestWorkflowIntegration:
    """Tests para integración con workflows."""
    
    def test_apply_workflow_success(self, controller, tmp_path, mock_workflow_engine):
        """Aplica un workflow exitosamente."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")
        
        success, msg = controller.apply_workflow_to_file(test_file, "default")
        
        assert success is True
        mock_workflow_engine.apply_rules.assert_called_once_with(test_file, "default")
    
    def test_get_available_profiles(self, controller, mock_workflow_engine):
        """Obtiene la lista de perfiles disponibles."""
        profiles = controller.get_available_profiles()
        
        assert profiles == ["default", "archive", "rename_date"]
        mock_workflow_engine.get_profiles.assert_called_once()


class TestPlatformIntegration:
    """Tests para integración con servicios de plataforma."""
    
    def test_is_word_installed(self, controller, mock_platform_service):
        """Verifica si Word está instalado."""
        result = controller.is_word_installed()
        assert result is True
    
    def test_get_tesseract_path(self, controller, mock_platform_service):
        """Obtiene la ruta de Tesseract."""
        path = controller.get_tesseract_path()
        assert path == Path("/usr/bin/tesseract")
    
    def test_toggle_context_menu_success(self, controller, mock_platform_service):
        """Activa/desactiva menú contextual."""
        success, msg = controller.toggle_context_menu(True)
        assert success is True
        assert "activado" in msg.lower()
        
        success, msg = controller.toggle_context_menu(False)
        assert success is True
        assert "desactivado" in msg.lower()
    
    def test_send_notification_enabled(self, controller, mock_platform_service):
        """Envía notificación cuando está habilitada."""
        controller.send_notification("Test", "Message")
        # MockPlatformService imprime en stdout, no hay método directo para verificar


class TestSettingsManagement:
    """Tests para gestión de configuraciones."""
    
    def test_update_setting_valid(self, controller, mock_config_manager):
        """Actualiza configuración válida."""
        controller.update_setting("max_queue_size", 20)
        assert controller.settings.max_queue_size == 20
        mock_config_manager.set.assert_called_with("max_queue_size", 20)
        mock_config_manager.save.assert_called()
    
    def test_update_setting_invalid(self, controller):
        """Rechaza configuración inválida."""
        with pytest.raises(ValueError) as exc_info:
            controller.update_setting("invalid_key", "value")
        
        assert "desconocida" in str(exc_info.value).lower()
    
    def test_get_queue_stats(self, controller, mock_queue_manager):
        """Obtiene estadísticas de cola."""
        stats = controller.get_queue_stats()
        
        assert "primary_queue_size" in stats
        assert "secondary_queue_size" in stats
        mock_queue_manager.get_stats.assert_called_once()
