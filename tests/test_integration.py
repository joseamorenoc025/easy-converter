"""Tests de integración: flujo completo."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from core.controller import AppController
from core.interfaces import (
    IConverter, IQueueManager, IConfigManager,
    IWorkflowEngine, ConversionJob
)
from utils.platform_service import MockPlatformService


@pytest.fixture
def integration_setup():
    converter = Mock(spec=IConverter)
    converter.convert_pdf_to_word.return_value = (True, "output.docx")

    queue = Mock(spec=IQueueManager)
    queue.add_job.return_value = True
    queue.get_stats.return_value = {"primary": 0, "secondary": 0}

    config = Mock(spec=IConfigManager)
    config.get.return_value = None

    workflow = Mock(spec=IWorkflowEngine)
    workflow.get_profiles.return_value = ["default"]

    platform = MockPlatformService(word_installed=True)

    callback = Mock()

    controller = AppController(
        converter=converter,
        queue_manager=queue,
        config_manager=config,
        workflow_engine=workflow,
        platform_service=platform,
        view_callback=callback,
    )

    return controller, converter, queue, callback


class TestIntegration:
    def test_validate_and_queue_pdf(self, integration_setup, tmp_path):
        controller, _, queue, _ = integration_setup
        pdf = tmp_path / "test.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake content for test")

        with patch('core.controller.validate_file_magic', return_value=(True, "OK")):
            with patch('core.controller.is_safe_path', return_value=True):
                success, msg, job_id = controller.queue_conversion(
                    pdf, "pdf2word"
                )

        assert success is True
        queue.add_job.assert_called_once()

    def test_cancel_nonexistent_job(self, integration_setup):
        controller, _, _, _ = integration_setup
        success, msg = controller.cancel_job("nonexistent_id")
        assert success is False

    def test_get_queue_stats(self, integration_setup):
        controller, _, _, _ = integration_setup
        stats = controller.get_queue_stats()
        assert "primary" in stats

    def test_get_available_profiles(self, integration_setup):
        controller, _, _, _ = integration_setup
        profiles = controller.get_available_profiles()
        assert "default" in profiles

    def test_is_word_installed(self, integration_setup):
        controller, _, _, _ = integration_setup
        result = controller.is_word_installed()
        assert result is True
