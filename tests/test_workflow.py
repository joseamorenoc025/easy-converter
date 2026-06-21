import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.workflow import (
    RuleType, WorkflowRule, WorkflowProfile, WorkflowManager
)


class TestWorkflowRule:
    def test_create_rename_rule(self):
        rule = WorkflowRule(type=RuleType.RENAME, params={"pattern": "{name}_{date}"})
        assert rule.type == RuleType.RENAME
        assert rule.params["pattern"] == "{name}_{date}"

    def test_rule_to_dict_and_from_dict(self):
        rule = WorkflowRule(type=RuleType.MOVE, params={"destination": "/output"})
        data = rule.to_dict()
        restored = WorkflowRule.from_dict(data)
        assert restored.type == RuleType.MOVE
        assert restored.params["destination"] == "/output"

    def test_rule_all_types_serialize(self):
        for t in RuleType:
            rule = WorkflowRule(type=t, params={"key": "val"})
            data = rule.to_dict()
            restored = WorkflowRule.from_dict(data)
            assert restored.type == t


class TestWorkflowProfile:
    def test_create_profile(self):
        profile = WorkflowProfile(
            name="test",
            rules=[WorkflowRule(type=RuleType.RENAME)],
            watch_path="/watch",
            is_active=True
        )
        assert profile.name == "test"
        assert len(profile.rules) == 1

    def test_profile_roundtrip(self):
        original = WorkflowProfile(
            name="roundtrip",
            rules=[WorkflowRule(type=RuleType.COPY, params={"destination": "/out"})],
            watch_path="/watch",
            is_active=False
        )
        data = original.to_dict()
        restored = WorkflowProfile.from_dict(data)
        assert restored.name == "roundtrip"
        assert restored.rules[0].type == RuleType.COPY
        assert restored.watch_path == "/watch"
        assert restored.is_active is False


class TestWorkflowManager:
    @pytest.fixture
    def config_mock(self):
        cfg = MagicMock()
        cfg.get.return_value = []
        return cfg

    def test_init_loads_profiles(self, config_mock):
        mgr = WorkflowManager(config_mock)
        assert mgr.profiles == []

    def test_add_and_save_profile(self, config_mock):
        mgr = WorkflowManager(config_mock)
        profile = WorkflowProfile(name="nuevo", watch_path="/path")
        mgr.add_profile(profile)
        assert len(mgr.profiles) == 1
        config_mock.set.assert_called_once()

    def test_delete_profile(self, config_mock):
        mgr = WorkflowManager(config_mock)
        mgr.add_profile(WorkflowProfile(name="p1"))
        mgr.add_profile(WorkflowProfile(name="p2"))
        mgr.delete_profile("p1")
        assert len(mgr.profiles) == 1
        assert mgr.profiles[0].name == "p2"

    def test_delete_nonexistent_profile(self, config_mock):
        mgr = WorkflowManager(config_mock)
        mgr.add_profile(WorkflowProfile(name="p1"))
        mgr.delete_profile("no_existe")
        assert len(mgr.profiles) == 1

    def test_apply_workflow_nonexistent_profile_returns_same_path(self, config_mock, tmp_path):
        mgr = WorkflowManager(config_mock)
        f = tmp_path / "test.pdf"
        f.write_text("dummy")
        result = mgr.apply_workflow("no_existe", f)
        assert result == f

    def test_apply_rename_rule(self, config_mock, tmp_path):
        mgr = WorkflowManager(config_mock)
        f = tmp_path / "documento.pdf"
        f.write_text("contenido")
        profile = WorkflowProfile(
            name="renombrar",
            rules=[WorkflowRule(type=RuleType.RENAME, params={"pattern": "{name}_v2"})],
            is_active=True
        )
        mgr.add_profile(profile)
        result = mgr.apply_workflow("renombrar", f)
        assert "documento_v2" in result.name
        assert not f.exists()
        assert result.exists()

    def test_apply_move_rule(self, config_mock, tmp_path):
        mgr = WorkflowManager(config_mock)
        dest = tmp_path / "destino"
        f = tmp_path / "archivo.pdf"
        f.write_text("contenido")
        profile = WorkflowProfile(
            name="mover",
            rules=[WorkflowRule(type=RuleType.MOVE, params={"destination": str(dest)})],
            is_active=True
        )
        mgr.add_profile(profile)
        result = mgr.apply_workflow("mover", f)
        assert result.parent == dest
        assert result.exists()

    def test_apply_copy_rule(self, config_mock, tmp_path):
        mgr = WorkflowManager(config_mock)
        dest = tmp_path / "copia_dir"
        f = tmp_path / "original.pdf"
        f.write_text("contenido")
        profile = WorkflowProfile(
            name="copiar",
            rules=[WorkflowRule(type=RuleType.COPY, params={"destination": str(dest)})],
            is_active=True
        )
        mgr.add_profile(profile)
        result = mgr.apply_workflow("copiar", f)
        assert result == f  # COPY returns original
        assert f.exists()
        copied = dest / "original.pdf"
        assert copied.exists()

    @patch("core.workflow.Document")
    def test_apply_sanitize_rule(self, mock_document_cls, config_mock, tmp_path):
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "texto de prueba"
        mock_para.runs = []
        mock_doc.paragraphs = [mock_para]
        mock_document_cls.return_value = mock_doc

        mgr = WorkflowManager(config_mock)
        f = tmp_path / "documento.docx"
        f.write_text("dummy docx")
        profile = WorkflowProfile(
            name="sanitizar",
            rules=[WorkflowRule(type=RuleType.SANITIZE, params={"font": "Arial", "size": 12})],
            is_active=True
        )
        mgr.add_profile(profile)
        result = mgr.apply_workflow("sanitizar", f)
        assert result == f
