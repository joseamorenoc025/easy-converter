import customtkinter
from core.workflow import WorkflowProfile, WorkflowRule, RuleType, WorkflowManager
from typing import Callable
from ui.themes import ThemeManager


class WorkflowPanel(customtkinter.CTkFrame):
    def __init__(self, master, workflow_manager: WorkflowManager, on_watcher_change: Callable, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.workflow_manager = workflow_manager
        self.on_watcher_change = on_watcher_change
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        header = customtkinter.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(12, 0))
        customtkinter.CTkLabel(header, text="\U0001f504",
                               font=customtkinter.CTkFont(size=20)).pack(side="left", padx=(0, 8))
        customtkinter.CTkLabel(header, text="Carpeta Inteligente",
                               font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left")

        customtkinter.CTkLabel(self, text="Configura perfiles para monitorear carpetas y convertir autom\u00e1ticamente",
                               font=customtkinter.CTkFont(size=12),
                               text_color=ThemeManager.get_color("text_secondary")).pack(padx=20, pady=(2, 8), anchor="w")

        self.profiles_frame = customtkinter.CTkScrollableFrame(self, height=220,
                                                               fg_color=ThemeManager.get_color("surface"))
        self.profiles_frame.pack(fill="x", padx=20, pady=10)
        self.render_profiles()

        self.btn_new = customtkinter.CTkButton(self, text="+ Nuevo Perfil",
                                               command=self.create_profile_dialog,
                                               fg_color=ThemeManager.get_color("primary"),
                                               corner_radius=8,
                                               font=customtkinter.CTkFont(size=12, weight="bold"))
        self.btn_new.pack(pady=10, padx=20, anchor="e")

    def render_profiles(self):
        for widget in self.profiles_frame.winfo_children():
            widget.destroy()

        if not self.workflow_manager.profiles:
            customtkinter.CTkLabel(self.profiles_frame,
                                   text="\U0001f4cb No hay perfiles configurados",
                                   text_color=ThemeManager.get_color("text_secondary"),
                                   font=customtkinter.CTkFont(size=12)).pack(pady=20)
            return

        for i, profile in enumerate(self.workflow_manager.profiles):
            row_bg = ThemeManager.get_color("queue_row") if i % 2 == 0 else ThemeManager.get_color("queue_row_alt")
            frame = customtkinter.CTkFrame(self.profiles_frame, fg_color=row_bg, corner_radius=8)
            frame.pack(fill="x", pady=3, padx=4)

            info_frame = customtkinter.CTkFrame(frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            customtkinter.CTkLabel(info_frame, text=profile.name,
                                   font=customtkinter.CTkFont(size=13, weight="bold")).pack(anchor="w")

            path_text = profile.watch_path if profile.watch_path else "Sin carpeta asignada"
            customtkinter.CTkLabel(info_frame, text=f"\U0001f4c1 {path_text}",
                                   font=customtkinter.CTkFont(size=11),
                                   text_color=ThemeManager.get_color("text_secondary")).pack(anchor="w")

            switch_var = customtkinter.BooleanVar(value=profile.is_active)
            customtkinter.CTkSwitch(frame, text="Activo", variable=switch_var,
                                    command=lambda p=profile, v=switch_var: self.toggle_profile(p, v)).pack(side="left", padx=15)

            customtkinter.CTkButton(frame, text="\U0001f5d1\ufe0f", width=30, height=28,
                                    fg_color="transparent",
                                    text_color=ThemeManager.get_color("text_secondary"),
                                    hover_color=ThemeManager.get_color("error"),
                                    font=customtkinter.CTkFont(size=12),
                                    command=lambda p=profile: self.delete_profile(p)).pack(side="right", padx=10)

    def toggle_profile(self, profile: WorkflowProfile, var: customtkinter.BooleanVar):
        profile.is_active = var.get()
        self.workflow_manager.save_profiles()
        self.on_watcher_change(profile)

    def delete_profile(self, profile: WorkflowProfile):
        if profile.is_active:
            profile.is_active = False
            self.on_watcher_change(profile)
        self.workflow_manager.delete_profile(profile.name)
        self.render_profiles()

    def create_profile_dialog(self):
        dialog = customtkinter.CTkInputDialog(text="Nombre del nuevo perfil:", title="Nuevo Perfil")
        name = dialog.get_input()
        if name:
            folder = customtkinter.filedialog.askdirectory(title=f"Seleccionar carpeta para monitorear ({name})")
            if folder:
                rules = [WorkflowRule(type=RuleType.RENAME, params={"pattern": "{name}_CONVERTIDO_{date}"})]
                new_profile = WorkflowProfile(name=name, watch_path=folder, rules=rules)
                self.workflow_manager.add_profile(new_profile)
                self.render_profiles()
