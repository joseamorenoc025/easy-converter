"""
Componentes UI reutilizables con estilo cyber/neon.
"""
import customtkinter as ctk
from typing import Callable, Optional


def create_status_badge(parent, text: str, color: str) -> ctk.CTkLabel:
    """Crea una etiqueta de estado con color neon."""
    label = ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=11), text_color=color)
    return label


def create_queue_item_frame(parent, display_name: str, on_open: Optional[Callable] = None) -> dict:
    """
    Crea un frame de item de cola con nombre, barra de progreso, estado y botón.
    Retorna un dict con las referencias a los widgets para actualización dinámica.
    """
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=2, padx=5)

    # Nombre del archivo
    name_label = ctk.CTkLabel(
        frame, text=display_name, width=250, anchor="w",
        font=ctk.CTkFont(size=12, weight="bold")
    )
    name_label.pack(side="left", padx=10)

    # Barra de progreso
    progress_bar = ctk.CTkProgressBar(frame, width=150)
    progress_bar.set(0)
    progress_bar.pack(side="left", padx=10)

    # Estado
    status_label = ctk.CTkLabel(frame, text="En espera", width=150, font=ctk.CTkFont(size=11))
    status_label.pack(side="left", padx=10)

    # Botón abrir
    open_btn = ctk.CTkButton(
        frame, text="Abrir", width=60, height=24,
        state="disabled",
        command=on_open
    )
    open_btn.pack(side="right", padx=10)

    return {
        "frame": frame,
        "name": name_label,
        "progress": progress_bar,
        "status": status_label,
        "open_btn": open_btn,
    }


def update_queue_item_widgets(widgets: dict, item) -> None:
    """Actualiza los widgets de un item de cola con datos del QueueItem."""
    widgets["progress"].set(item.progress / 100)
    widgets["status"].configure(text=item.message)
    
    if item.status == "success":
        widgets["status"].configure(text_color="green")
        widgets["open_btn"].configure(state="normal")
    elif item.status == "failed":
        widgets["status"].configure(text_color="red")
    elif item.status == "running":
        widgets["status"].configure(text_color="orange")
    else:
        widgets["status"].configure(text_color="gray")
        widgets["open_btn"].configure(state="disabled")


def create_stat_card(parent, label: str, value: str) -> ctk.CTkLabel:
    """Crea una tarjeta de estadística estilo dashboard cyber."""
    card = ctk.CTkLabel(
        parent, text=f"{label}: {value}",
        font=ctk.CTkFont(size=14),
        anchor="w"
    )
    return card