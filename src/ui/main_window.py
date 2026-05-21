import customtkinter
import os
import threading
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_FILES
from core.converter import EasyConverter
from core.error_handler import ErrorHandler
from core.progress import ConversionProgress
from core.queue_manager import ConversionQueue, QueueItem
from core.file_manager import PathManager
from core.workflow import WorkflowManager, WorkflowProfile
from core.watcher import SmartWatcher
from ui.workflow_panel import WorkflowPanel
from utils.config import ConfigManager
from tkinter import messagebox

# Configuración estética global
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # Configuración de ventana
        self.title("Easy Converter v2.0")
        self.geometry("800x650")
        self.resizable(True, True)
        self.minsize(700, 550)

        # Inicializar Componentes Core
        self.config_manager = ConfigManager()
        self.path_manager = PathManager(self.config_manager)
        self.error_handler = ErrorHandler()
        self.workflow_manager = WorkflowManager(self.config_manager)
        self.watcher = SmartWatcher(callback=self.on_file_detected)
        self.queue_manager = ConversionQueue(
            worker_func=self.process_item,
            on_queue_update=self.update_queue_ui
        )

        # Variables de estado
        self.conversion_mode = "pdf2word"

        self.setup_ui()
        self.setup_watchers()

    def setup_watchers(self):
        self.watcher.start()
        for profile in self.workflow_manager.profiles:
            if profile.is_active and profile.watch_path:
                self.watcher.add_watch(profile.watch_path)

    def on_file_detected(self, file_path: Path):
        # Encontrar qué perfil disparó esto
        for profile in self.workflow_manager.profiles:
            if profile.is_active and profile.watch_path:
                if str(file_path.parent).lower() == str(Path(profile.watch_path)).lower():
                    ext = file_path.suffix.lower()
                    mode = 'pdf2word' if ext == '.pdf' else 'word2pdf'
                    self.after(0, lambda: self.queue_manager.add_item(file_path, mode, workflow_profile=profile.name))
                    break

    def handle_watcher_change(self, profile: WorkflowProfile):
        if profile.is_active and profile.watch_path:
            self.watcher.add_watch(profile.watch_path)
        elif profile.watch_path:
            self.watcher.remove_watch(profile.watch_path)

    def setup_ui(self):
        # Frame Izquierdo: Configuración
        self.sidebar = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar, text="EasyConverter", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20, padx=20)

        self.label_settings = customtkinter.CTkLabel(self.sidebar, text="Configuración de Salida", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.label_settings.pack(pady=(10, 5), padx=20, anchor="w")

        self.out_mode_var = customtkinter.StringVar(value=self.config_manager.get("output_mode"))
        
        self.radio_same = customtkinter.CTkRadioButton(self.sidebar, text="Misma carpeta", variable=self.out_mode_var, value="same_folder", command=self.save_settings)
        self.radio_same.pack(pady=5, padx=30, anchor="w")
        
        self.radio_sub = customtkinter.CTkRadioButton(self.sidebar, text="Subcarpeta 'convertidos'", variable=self.out_mode_var, value="subfolder", command=self.save_settings)
        self.radio_sub.pack(pady=5, padx=30, anchor="w")
        
        self.radio_custom = customtkinter.CTkRadioButton(self.sidebar, text="Carpeta personalizada", variable=self.out_mode_var, value="custom", command=self.save_settings)
        self.radio_custom.pack(pady=5, padx=30, anchor="w")

        self.btn_select_custom = customtkinter.CTkButton(self.sidebar, text="Seleccionar Carpeta", command=self.select_custom_folder, height=24, font=customtkinter.CTkFont(size=11))
        self.btn_select_custom.pack(pady=5, padx=30)
        
        self.check_open = customtkinter.CTkCheckBox(self.sidebar, text="Abrir al finalizar", command=self.save_settings)
        if self.config_manager.get("open_folder_on_finish"): self.check_open.select()
        self.check_open.pack(pady=20, padx=20, anchor="w")

        self.btn_context_menu = customtkinter.CTkButton(self.sidebar, text="Añadir a Menú Contextual", command=self.register_context_menu, height=30, fg_color="gray30")
        self.btn_context_menu.pack(pady=10, padx=20, side="bottom")

        # Main Content
        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20)

        # Tabview para separar Conversión Manual y Flujos
        self.tabview = customtkinter.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, pady=10)
        self.tabview.add("Conversión Manual")
        self.tabview.add("Flujos de Trabajo")

        # --- TAB: Conversión Manual ---
        self.manual_tab = self.tabview.tab("Conversión Manual")

        # Layout para Manual Tab: Izquierda (Controles) | Derecha (Preview)
        self.manual_content = customtkinter.CTkFrame(self.manual_tab, fg_color="transparent")
        self.manual_content.pack(fill="both", expand=True)

        self.left_manual = customtkinter.CTkFrame(self.manual_content, fg_color="transparent")
        self.left_manual.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Selector de modo
        self.mode_frame = customtkinter.CTkFrame(self.left_manual, fg_color="transparent")
        self.mode_frame.pack(pady=10)

        self.btn_pdf2word = customtkinter.CTkButton(self.mode_frame, text="PDF a Word", command=lambda: self.set_mode("pdf2word"), width=120)
        self.btn_pdf2word.grid(row=0, column=0, padx=10)
        self.btn_word2pdf = customtkinter.CTkButton(self.mode_frame, text="Word a PDF", command=lambda: self.set_mode("word2pdf"), width=120, fg_color="gray30")
        self.btn_word2pdf.grid(row=0, column=1, padx=10)

        # Drop Zone
        self.drop_frame = customtkinter.CTkFrame(self.left_manual, height=100, corner_radius=15)
        self.drop_frame.pack(pady=10, fill="x")
        self.drop_frame.pack_propagate(False)

        self.drop_label = customtkinter.CTkLabel(self.drop_frame, text="Arrastra archivos aquí o haz clic")
        self.drop_label.pack(expand=True)
        self.drop_frame.bind("<Button-1>", lambda e: self.select_files_dialog())
        self.drop_label.bind("<Button-1>", lambda e: self.select_files_dialog())
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

        # Preview Panel (Nuevo)
        self.preview_frame = customtkinter.CTkFrame(self.manual_content, width=200, corner_radius=10)
        self.preview_frame.pack(side="right", fill="y", pady=10)
        self.preview_frame.pack_propagate(False)

        self.preview_title = customtkinter.CTkLabel(self.preview_frame, text="Vista Previa", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.preview_title.pack(pady=5)

        self.preview_image_label = customtkinter.CTkLabel(self.preview_frame, text="Sin selección")
        self.preview_image_label.pack(expand=True, padx=10, pady=10)

        # Queue (ahora dentro de la tab manual para mejor enfoque)
        self.scroll_frame = customtkinter.CTkScrollableFrame(self.left_manual, height=250)
        self.scroll_frame.pack(pady=10, fill="both", expand=True)
        self.item_widgets = {}

        # --- TAB: Flujos de Trabajo ---
        self.workflow_tab = self.tabview.tab("Flujos de Trabajo")
        self.workflow_panel = WorkflowPanel(self.workflow_tab, self.workflow_manager, on_watcher_change=self.handle_watcher_change)
        self.workflow_panel.pack(fill="both", expand=True)

        # Footer
        self.footer = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.footer.pack(fill="x", pady=10)
        
        self.clear_button = customtkinter.CTkButton(self.footer, text="Limpiar completados", command=self.queue_manager.clear_completed, width=150, fg_color="gray30")
        self.clear_button.pack(side="left")
        
        self.status_global = customtkinter.CTkLabel(self.footer, text="Listo")
        self.status_global.pack(side="right")

    def save_settings(self):
        self.config_manager.set("output_mode", self.out_mode_var.get())
        self.config_manager.set("open_folder_on_finish", self.check_open.get())

    def select_custom_folder(self):
        folder = customtkinter.filedialog.askdirectory()
        if folder:
            self.config_manager.set("custom_path", folder)
            self.out_mode_var.set("custom")
            self.save_settings()

    def select_files_dialog(self):
        file_paths = customtkinter.filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[("Archivos compatibles", "*.pdf *.docx *.doc"), ("PDF", "*.pdf"), ("Word", "*.docx *.doc")]
        )
        for path in file_paths:
            self.process_selected_file(path)

    def handle_drop(self, event):
        data = event.data
        import re
        # Limpia llaves y divide correctamente (soporta espacios en rutas de Windows)
        paths = re.findall(r'\{([^}]+)\}|(\S+)', data)
        file_paths = [Path(p[0] if p[0] else p[1]) for p in paths]
        
        for path in file_paths:
            if path.exists():
                self.process_selected_file(str(path))

    def process_selected_file(self, file_path):
        path = Path(file_path)
        ext = path.suffix.lower()
        
        # Actualizar vista previa si es PDF
        if ext == '.pdf':
            self.update_preview(path)
        
        # Lógica de Auto-Detección mejorada
        mode = None
        if ext == '.pdf':
            mode = 'pdf2word'
        elif ext in ['.docx', '.doc']:
            mode = 'word2pdf'
            
        if mode:
            self.queue_manager.add_item(path, mode)

    def update_preview(self, pdf_path):
        import fitz
        from PIL import Image
        try:
            doc = fitz.open(str(pdf_path))
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)) # Baja resolución para preview rápida
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Ajustar al tamaño del panel
            preview_width = 180
            aspect = img.height / img.width
            preview_height = int(preview_width * aspect)
            
            ctk_img = customtkinter.CTkImage(light_image=img, dark_image=img, size=(preview_width, preview_height))
            self.preview_image_label.configure(image=ctk_img, text="")
            doc.close()
        except Exception as e:
            self.preview_image_label.configure(image=None, text=f"Error en preview")
            print(f"Error generando preview: {e}")

    def set_mode(self, mode):
        self.conversion_mode = mode
        self.btn_pdf2word.configure(fg_color="#1f538d" if mode == "pdf2word" else "gray30")
        self.btn_word2pdf.configure(fg_color="#1f538d" if mode == "word2pdf" else "gray30")

    def process_item(self, item: QueueItem):
        # Calcular ruta de salida real
        output_path = self.path_manager.resolve_output_path(item.file_path, item.mode)
        
        def on_update(percent, message):
            item.progress = percent
            item.message = message
            self.update_queue_ui()

        tracker = ConversionProgress(on_update=on_update)
        try:
            if item.mode == "pdf2word":
                success, result = EasyConverter.pdf_to_docx(item.file_path, output_path=output_path, progress_tracker=tracker)
            else:
                success, result = EasyConverter.docx_to_pdf(item.file_path, output_path=output_path, progress_tracker=tracker)
            
            if success:
                # Aplicar workflow si existe
                if item.workflow_profile:
                    item.message = "Aplicando reglas..."
                    self.update_queue_ui()
                    final_path = self.workflow_manager.apply_workflow(item.workflow_profile, Path(result))
                    item.result_path = str(final_path)
                else:
                    item.result_path = result
                
                if self.config_manager.get("open_folder_on_finish"):
                    self.path_manager.open_in_explorer(Path(item.result_path))
        except Exception as e:
            raise e

    def register_context_menu(self):
        from utils.context_menu import add_context_menu
        try:
            add_context_menu()
            messagebox.showinfo("Éxito", "Menú contextual añadido correctamente.\nAhora puedes hacer clic derecho en archivos PDF/DOCX.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo añadir al registro: {e}")

    def update_queue_ui(self):
        self.after(0, self._render_queue)

    def _render_queue(self):
        items = self.queue_manager.get_all_items()
        current_ids = [id(item) for item in items]
        for item_id in list(self.item_widgets.keys()):
            if item_id not in current_ids:
                self.item_widgets[item_id]['frame'].destroy()
                del self.item_widgets[item_id]

        for item in items:
            item_id = id(item)
            if item_id not in self.item_widgets:
                frame = customtkinter.CTkFrame(self.scroll_frame)
                frame.pack(fill="x", pady=2, padx=5)
                name_label = customtkinter.CTkLabel(frame, text=item.file_path.name, width=250, anchor="w", font=customtkinter.CTkFont(size=12, weight="bold"))
                name_label.pack(side="left", padx=10)
                progress_bar = customtkinter.CTkProgressBar(frame, width=150)
                progress_bar.set(0)
                progress_bar.pack(side="left", padx=10)
                status_label = customtkinter.CTkLabel(frame, text="En espera", width=150, font=customtkinter.CTkFont(size=11))
                status_label.pack(side="left", padx=10)
                open_btn = customtkinter.CTkButton(frame, text="Abrir", width=60, height=24, command=lambda p=item: self.path_manager.open_in_explorer(Path(p.result_path)) if p.result_path else None, state="disabled")
                open_btn.pack(side="right", padx=10)
                self.item_widgets[item_id] = {'frame': frame, 'progress': progress_bar, 'status': status_label, 'open_btn': open_btn}

            widgets = self.item_widgets[item_id]
            widgets['progress'].set(item.progress / 100)
            widgets['status'].configure(text=item.message)
            if item.status == "success":
                widgets['status'].configure(text_color="green")
                widgets['open_btn'].configure(state="normal")
            elif item.status == "failed":
                widgets['status'].configure(text_color="red")
            elif item.status == "running":
                widgets['status'].configure(text_color="orange")

        running = sum(1 for i in items if i.status == "running")
        self.status_global.configure(text=f"Procesando {running}..." if running else "Listo", text_color="orange" if running else "gray")

if __name__ == "__main__":
    app = App()
    app.mainloop()
