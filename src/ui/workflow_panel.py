import customtkinter
from core.workflow import WorkflowProfile, WorkflowRule, RuleType, WorkflowManager
from typing import Callable

class WorkflowPanel(customtkinter.CTkFrame):
    def __init__(self, master, workflow_manager: WorkflowManager, on_watcher_change: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.workflow_manager = workflow_manager
        self.on_watcher_change = on_watcher_change
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        self.title_label = customtkinter.CTkLabel(self, text="Gestión de Flujos Inteligentes", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.title_label.pack(pady=10, padx=20, anchor="w")

        # Listado de perfiles
        self.profiles_frame = customtkinter.CTkScrollableFrame(self, height=200)
        self.profiles_frame.pack(fill="x", padx=20, pady=10)
        self.render_profiles()

        # Botón Nuevo Perfil
        self.btn_new = customtkinter.CTkButton(self, text="+ Nuevo Perfil", command=self.create_profile_dialog)
        self.btn_new.pack(pady=10, padx=20, anchor="e")

    def render_profiles(self):
        for widget in self.profiles_frame.winfo_children():
            widget.destroy()

        if not self.workflow_manager.profiles:
            label = customtkinter.CTkLabel(self.profiles_frame, text="No hay perfiles configurados", text_color="gray")
            label.pack(pady=20)
            return

        for profile in self.workflow_manager.profiles:
            frame = customtkinter.CTkFrame(self.profiles_frame)
            frame.pack(fill="x", pady=5, padx=5)
            
            name_label = customtkinter.CTkLabel(frame, text=profile.name, font=customtkinter.CTkFont(weight="bold"))
            name_label.pack(side="left", padx=10)
            
            # Switch de activado
            switch_var = customtkinter.BooleanVar(value=profile.is_active)
            switch = customtkinter.CTkSwitch(frame, text="Monitorear", variable=switch_var, 
                                            command=lambda p=profile, v=switch_var: self.toggle_profile(p, v))
            switch.pack(side="left", padx=20)
            
            desc = f"Carpeta: {profile.watch_path if profile.watch_path else 'No asignada'}"
            path_label = customtkinter.CTkLabel(frame, text=desc, font=customtkinter.CTkFont(size=11), text_color="gray")
            path_label.pack(side="left", padx=10)

            btn_del = customtkinter.CTkButton(frame, text="Eliminar", width=60, height=24, fg_color="transparent", 
                                             text_color="red", hover_color="#330000",
                                             command=lambda p=profile: self.delete_profile(p))
            btn_del.pack(side="right", padx=10)

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
            # Seleccionar carpeta
            folder = customtkinter.filedialog.askdirectory(title=f"Seleccionar carpeta para monitorear ({name})")
            if folder:
                # Perfil por defecto con regla de renombrado (fecha)
                rules = [WorkflowRule(type=RuleType.RENAME, params={"pattern": "{name}_CONVERTIDO_{date}"})]
                new_profile = WorkflowProfile(name=name, watch_path=folder, rules=rules)
                self.workflow_manager.add_profile(new_profile)
                self.render_profiles()
