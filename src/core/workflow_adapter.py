"""Adapter: IWorkflowEngine → WorkflowManager"""
from pathlib import Path
from typing import List, Tuple
from core.interfaces import IWorkflowEngine
from core.workflow import WorkflowManager


class WorkflowAdapter(IWorkflowEngine):
    def __init__(self, config_manager):
        self._manager = WorkflowManager(config_manager)

    def apply_rules(self, file_path: Path, profile_name: str) -> Tuple[bool, str]:
        try:
            result = self._manager.apply_workflow(profile_name, file_path)
            return True, f"Reglas aplicadas: {result}"
        except Exception as e:
            return False, str(e)

    def get_profiles(self) -> List[str]:
        return [p.name for p in self._manager.profiles]

    def validate_profile(self, profile_name: str) -> Tuple[bool, str]:
        exists = any(p.name == profile_name for p in self._manager.profiles)
        if exists:
            return True, "Perfil válido"
        return False, f"Perfil '{profile_name}' no encontrado"
