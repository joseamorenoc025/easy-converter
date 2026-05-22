"""
Notificaciones de escritorio para Easy Converter.
Soporta Windows Toast (winotify) con fallback a tkinter messagebox.
"""
import sys
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-load winotify solo en Windows, con fallback seguro
_notifier = None

def _get_notifier():
    """Obtiene o crea el notificador de Windows (lazy)."""
    global _notifier
    if _notifier is None:
        if sys.platform == "win32":
            try:
                import winotify
                _notifier = winotify.Notifier(app_id="EasyConverter", app_name="Easy Converter")
            except Exception as e:
                logger.debug(f"winotify no disponible: {e}")
                _notifier = None
        else:
            _notifier = None
    return _notifier


def notify(title: str, message: str, icon_path: Optional[str] = None, sound: bool = True):
    """
    Envía una notificación de escritorio.
    
    En Windows usa winotify para notificaciones nativas con sonido.
    En otros sistemas hace fallback silencioso (no bloquea la UI).
    """
    notifier = _get_notifier()
    
    if notifier is not None:
        try:
            notifier.notify(
                title=title,
                msg=message,
                icon=icon_path,
                sound=sound,
            )
        except Exception as e:
            logger.warning(f"Error enviando notificación: {e}")
            _tk_fallback(title, message)
    else:
        _tk_fallback(title, message)


def _tk_fallback(title: str, message: str):
    """Fallback con tkinter messagebox — solo si no hay notificador nativo."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo(title, message)
        root.destroy()
    except Exception:
        logger.debug(f" tkinter fallback falló (normal en headless): {title}")


def notify_conversion_complete(input_path: Path, output_path: Path, mode: str):
    """Notifica al usuario que una conversión terminó."""
    direction = "PDF → Word" if mode == "pdf2word" else "Word → PDF"
    notify(
        title="Conversión completada",
        message=f"{direction}\n{input_path.name}\n→ {output_path.name}"
    )


def notify_error(error_title: str, error_message: str):
    """Notifica un error al usuario."""
    notify(title=error_title, message=error_message, sound=True)