"""Adapter: IViewCallback → UI callbacks"""
from core.interfaces import IViewCallback, ConversionJob


class ViewAdapter(IViewCallback):
    """Conecta el Controller con la UI de main_window.py"""

    def __init__(self, main_window):
        self._window = main_window

    def on_job_status_changed(self, job: ConversionJob):
        self._window.after(0, lambda: self._window.update_queue_ui())

    def on_queue_stats_updated(self, stats: dict):
        pass

    def on_error(self, message: str, critical: bool = False):
        self._window.after(0, lambda: self._window.notifications.error(
            "Error", message
        ))

    def on_success(self, message: str):
        self._window.after(0, lambda: self._window.notifications.success(
            "Éxito", message
        ))

    def update_progress(self, job_id: str, progress: float):
        pass
