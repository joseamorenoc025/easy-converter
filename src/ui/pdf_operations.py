import os
import threading
import customtkinter
from pathlib import Path
from tkinter import messagebox
from utils.pdf_tools import merge_pdfs, split_pdf, get_page_count


class MergePanel(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.file_list: list[Path] = []
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        title = customtkinter.CTkLabel(self, text="Combinar PDFs", font=customtkinter.CTkFont(size=16, weight="bold"))
        title.pack(pady=10, padx=20, anchor="w")

        desc = customtkinter.CTkLabel(self, text="Selecciona múltiples PDFs para combinarlos en uno solo", font=customtkinter.CTkFont(size=12), text_color="gray")
        desc.pack(pady=(0, 10), padx=20, anchor="w")

        btn_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=5)

        self.btn_add = customtkinter.CTkButton(btn_frame, text="+ Agregar PDFs", command=self.add_files, width=120)
        self.btn_add.pack(side="left", padx=(0, 10))

        self.btn_up = customtkinter.CTkButton(btn_frame, text="▲ Subir", command=self.move_up, width=80, fg_color="gray30")
        self.btn_up.pack(side="left", padx=5)

        self.btn_down = customtkinter.CTkButton(btn_frame, text="▼ Bajar", command=self.move_down, width=80, fg_color="gray30")
        self.btn_down.pack(side="left", padx=5)

        self.btn_remove = customtkinter.CTkButton(btn_frame, text="✕ Quitar", command=self.remove_selected, width=80, fg_color="gray30")
        self.btn_remove.pack(side="left", padx=5)

        self.list_frame = customtkinter.CTkScrollableFrame(self, height=180)
        self.list_frame.pack(fill="x", padx=20, pady=5)
        self.list_labels = []

        output_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        output_frame.pack(fill="x", padx=20, pady=10)

        self.output_path_var = customtkinter.StringVar(value=str(Path.home() / "Desktop" / "combinado.pdf"))
        output_label = customtkinter.CTkLabel(output_frame, text="Guardar como:", font=customtkinter.CTkFont(size=12))
        output_label.pack(side="left", padx=(0, 10))

        self.output_entry = customtkinter.CTkEntry(output_frame, textvariable=self.output_path_var, width=300)
        self.output_entry.pack(side="left", padx=(0, 10))

        self.btn_browse = customtkinter.CTkButton(output_frame, text="Examinar", command=self.browse_output, width=80, fg_color="gray30")
        self.btn_browse.pack(side="left")

        self.btn_merge = customtkinter.CTkButton(self, text="Combinar PDFs", command=self.start_merge, height=40, font=customtkinter.CTkFont(size=14, weight="bold"))
        self.btn_merge.pack(pady=10, padx=20)

        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label = customtkinter.CTkLabel(self, text="", font=customtkinter.CTkFont(size=11))
        self.status_label.pack()

    def add_files(self):
        files = customtkinter.filedialog.askopenfilenames(title="Seleccionar PDFs", filetypes=[("PDF", "*.pdf")])
        for f in files:
            p = Path(f)
            if p not in self.file_list:
                self.file_list.append(p)
        self.render_list()

    def render_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        self.list_labels = []
        for i, path in enumerate(self.file_list):
            frame = customtkinter.CTkFrame(self.list_frame)
            frame.pack(fill="x", pady=1, padx=2)
            label = customtkinter.CTkLabel(frame, text=f"{i+1}. {path.name}", anchor="w", font=customtkinter.CTkFont(size=12))
            label.pack(side="left", padx=10)
            size_label = customtkinter.CTkLabel(frame, text=f"{path.stat().st_size / 1024:.0f} KB", font=customtkinter.CTkFont(size=10), text_color="gray")
            size_label.pack(side="right", padx=10)
            self.list_labels.append(frame)
        self.update_status()

    def move_up(self):
        selected = self._get_selected_index()
        if selected and selected > 0:
            self.file_list[selected], self.file_list[selected - 1] = self.file_list[selected - 1], self.file_list[selected]
            self.render_list()

    def move_down(self):
        selected = self._get_selected_index()
        if selected is not None and selected < len(self.file_list) - 1:
            self.file_list[selected], self.file_list[selected + 1] = self.file_list[selected + 1], self.file_list[selected]
            self.render_list()

    def remove_selected(self):
        selected = self._get_selected_index()
        if selected is not None:
            self.file_list.pop(selected)
            self.render_list()

    def _get_selected_index(self):
        for i, frame in enumerate(self.list_labels):
            if frame.winfo_containing(self.list_frame.winfo_rootx() + 10, self.list_frame.winfo_rooty() + 30 + i * 30):
                return i
        return None

    def browse_output(self):
        path = customtkinter.filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            title="Guardar PDF combinado"
        )
        if path:
            self.output_path_var.set(path)

    def start_merge(self):
        if len(self.file_list) < 2:
            messagebox.showwarning("Aviso", "Selecciona al menos 2 archivos PDF para combinar.")
            return
        output = self.output_path_var.get()
        if not output:
            messagebox.showwarning("Aviso", "Especifica una ruta de salida.")
            return

        self.btn_merge.configure(state="disabled", text="Combinando...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Iniciando...")

        def task():
            def on_progress(pct, msg):
                self.after(0, lambda: self.progress_bar.set(pct / 100))
                self.after(0, lambda: self.status_label.configure(text=msg))
            try:
                merge_pdfs([str(p) for p in self.file_list], output, progress_callback=on_progress)
                self.after(0, lambda: self.status_label.configure(text=f"Completado: {os.path.basename(output)}", text_color="green"))
                self.after(0, lambda: self.progress_bar.set(1))
            except Exception as ex:
                error_msg = str(ex)
                self.after(0, lambda err=error_msg: self.status_label.configure(text=f"Error: {err}", text_color="red"))
            self.after(0, lambda: self.btn_merge.configure(state="normal", text="Combinar PDFs"))

        threading.Thread(target=task, daemon=True).start()

    def update_status(self):
        self.status_label.configure(text=f"{len(self.file_list)} archivos seleccionados")


class SplitPanel(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.input_pdf = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        title = customtkinter.CTkLabel(self, text="Dividir PDF", font=customtkinter.CTkFont(size=16, weight="bold"))
        title.pack(pady=10, padx=20, anchor="w")

        desc = customtkinter.CTkLabel(self, text="Divide un PDF en varios archivos por rangos o cada N páginas", font=customtkinter.CTkFont(size=12), text_color="gray")
        desc.pack(pady=(0, 10), padx=20, anchor="w")

        input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)

        self.btn_select = customtkinter.CTkButton(input_frame, text="Seleccionar PDF", command=self.select_file, width=120)
        self.btn_select.pack(side="left", padx=(0, 10))

        self.file_label = customtkinter.CTkLabel(input_frame, text="Ningún archivo seleccionado", font=customtkinter.CTkFont(size=12), text_color="gray")
        self.file_label.pack(side="left")

        mode_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=10)

        self.split_mode = customtkinter.StringVar(value="pages_per_file")
        self.radio_range = customtkinter.CTkRadioButton(mode_frame, text="Rangos personalizados", variable=self.split_mode, value="ranges", command=self.toggle_mode)
        self.radio_range.pack(anchor="w", pady=2)
        self.radio_npages = customtkinter.CTkRadioButton(mode_frame, text="Cada N páginas", variable=self.split_mode, value="pages_per_file", command=self.toggle_mode)
        self.radio_npages.pack(anchor="w", pady=2)

        self.options_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=20, pady=5)

        self.npages_frame = customtkinter.CTkFrame(self.options_frame, fg_color="transparent")
        self.npages_label = customtkinter.CTkLabel(self.npages_frame, text="Páginas por archivo:")
        self.npages_label.pack(side="left", padx=(0, 10))
        self.npages_var = customtkinter.StringVar(value="5")
        self.npages_entry = customtkinter.CTkEntry(self.npages_frame, textvariable=self.npages_var, width=60)
        self.npages_entry.pack(side="left")
        self.npages_frame.pack(fill="x", pady=5)

        self.ranges_frame = customtkinter.CTkFrame(self.options_frame, fg_color="transparent")
        ranges_label = customtkinter.CTkLabel(self.ranges_frame, text="Rangos (ej: 1-3, 5-7, 10-15):")
        ranges_label.pack(anchor="w")
        self.ranges_var = customtkinter.StringVar(value="1-3, 4-6, 7-10")
        self.ranges_entry = customtkinter.CTkEntry(self.ranges_frame, textvariable=self.ranges_var, width=300)
        self.ranges_entry.pack(anchor="w", pady=2)
        self.ranges_frame.pack(fill="x", pady=5)
        self.ranges_frame.pack_forget()

        output_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        output_frame.pack(fill="x", padx=20, pady=10)

        self.output_dir_var = customtkinter.StringVar(value=str(Path.home() / "Desktop"))
        out_label = customtkinter.CTkLabel(output_frame, text="Guardar en carpeta:")
        out_label.pack(side="left", padx=(0, 10))

        self.out_dir_entry = customtkinter.CTkEntry(output_frame, textvariable=self.output_dir_var, width=250)
        self.out_dir_entry.pack(side="left", padx=(0, 10))

        self.btn_browse_dir = customtkinter.CTkButton(output_frame, text="Examinar", command=self.browse_output_dir, width=80, fg_color="gray30")
        self.btn_browse_dir.pack(side="left")

        self.btn_split = customtkinter.CTkButton(self, text="Dividir PDF", command=self.start_split, height=40, font=customtkinter.CTkFont(size=14, weight="bold"))
        self.btn_split.pack(pady=10, padx=20)

        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label = customtkinter.CTkLabel(self, text="", font=customtkinter.CTkFont(size=11))
        self.status_label.pack()

    def toggle_mode(self):
        mode = self.split_mode.get()
        if mode == "ranges":
            self.ranges_frame.pack(fill="x", pady=5)
            self.npages_frame.pack_forget()
        else:
            self.npages_frame.pack(fill="x", pady=5)
            self.ranges_frame.pack_forget()

    def select_file(self):
        path = customtkinter.filedialog.askopenfilename(title="Seleccionar PDF", filetypes=[("PDF", "*.pdf")])
        if path:
            self.input_pdf = Path(path)
            pages = get_page_count(path)
            self.file_label.configure(text=f"{self.input_pdf.name} ({pages} páginas)", text_color="white")

    def browse_output_dir(self):
        folder = customtkinter.filedialog.askdirectory(title="Carpeta de destino")
        if folder:
            self.output_dir_var.set(folder)

    def start_split(self):
        if not self.input_pdf:
            messagebox.showwarning("Aviso", "Selecciona un archivo PDF primero.")
            return
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showwarning("Aviso", "Especifica una carpeta de destino.")
            return
        os.makedirs(output_dir, exist_ok=True)

        self.btn_split.configure(state="disabled", text="Dividiendo...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Iniciando...")

        def task():
            try:
                mode = self.split_mode.get()
                if mode == "ranges":
                    ranges = []
                    for part in self.ranges_var.get().split(","):
                        part = part.strip()
                        if "-" in part:
                            a, b = part.split("-")
                            ranges.append((int(a.strip()) - 1, int(b.strip()) - 1))
                    result = split_pdf(str(self.input_pdf), output_dir, ranges=ranges)
                else:
                    n = int(self.npages_var.get())
                    result = split_pdf(str(self.input_pdf), output_dir, pages_per_file=n)

                self.after(0, lambda: self.status_label.configure(
                    text=f"Completado: {len(result)} archivos generados en {output_dir}", text_color="green"))
                self.after(0, lambda: self.progress_bar.set(1))
            except Exception as ex:
                error_msg = str(ex)
                self.after(0, lambda err=error_msg: self.status_label.configure(text=f"Error: {err}", text_color="red"))
            self.after(0, lambda: self.btn_split.configure(state="normal", text="Dividir PDF"))

        threading.Thread(target=task, daemon=True).start()
