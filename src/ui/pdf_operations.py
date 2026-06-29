import os
import threading
import customtkinter
from pathlib import Path
from tkinter import messagebox
from utils.pdf_tools import (
    merge_pdfs, split_pdf, get_page_count,
    compress_pdf, sanitize_pdf, decrypt_pdf, get_pdf_info,
)
from ui.themes import ThemeManager


def _theme_color(key):
    return ThemeManager.get_color(key)


def _panel_title(parent, icon_text, title_text, desc_text):
    header = customtkinter.CTkFrame(parent, fg_color="transparent")
    header.pack(fill="x", padx=20, pady=(12, 0))
    customtkinter.CTkLabel(header, text=icon_text,
                           font=customtkinter.CTkFont(size=20)).pack(side="left", padx=(0, 8))
    customtkinter.CTkLabel(header, text=title_text,
                           font=customtkinter.CTkFont(size=16, weight="bold")).pack(side="left")
    customtkinter.CTkLabel(parent, text=desc_text,
                           font=customtkinter.CTkFont(size=12),
                           text_color=_theme_color("text_secondary")).pack(padx=20, pady=(2, 8), anchor="w")


def _action_btn(parent, text, command, primary=True):
    fg = _theme_color("primary") if primary else "gray30"
    return customtkinter.CTkButton(parent, text=text, command=command,
                                   height=38, corner_radius=8,
                                   font=customtkinter.CTkFont(size=13, weight="bold") if primary else customtkinter.CTkFont(size=12),
                                   fg_color=fg)


def _secondary_btn(parent, text, command, width=80):
    return customtkinter.CTkButton(parent, text=text, command=command,
                                   width=width, height=28, corner_radius=6,
                                   fg_color="gray30",
                                   font=customtkinter.CTkFont(size=11))


class MergePanel(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.file_list = []
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        _panel_title(self, "\U0001f500", "Combinar PDFs",
                     "Selecciona m\u00faltiples PDFs para combinarlos en uno solo")

        btn_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=5)

        _action_btn(btn_frame, "+ Agregar PDFs", self.add_files, primary=True).pack(side="left", padx=(0, 8))
        _secondary_btn(btn_frame, "\u25b2 Subir", self.move_up).pack(side="left", padx=3)
        _secondary_btn(btn_frame, "\u25bc Bajar", self.move_down).pack(side="left", padx=3)
        _secondary_btn(btn_frame, "\u2715 Quitar", self.remove_selected).pack(side="left", padx=3)

        self.list_frame = customtkinter.CTkScrollableFrame(self, height=180,
                                                           fg_color=_theme_color("surface"))
        self.list_frame.pack(fill="x", padx=20, pady=5)
        self.list_labels = []

        output_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        output_frame.pack(fill="x", padx=20, pady=8)
        customtkinter.CTkLabel(output_frame, text="Guardar como:",
                               font=customtkinter.CTkFont(size=12)).pack(side="left", padx=(0, 8))
        self.output_path_var = customtkinter.StringVar(value=str(Path.home() / "Desktop" / "combinado.pdf"))
        customtkinter.CTkEntry(output_frame, textvariable=self.output_path_var, width=300).pack(side="left", padx=(0, 8))
        _secondary_btn(output_frame, "Examinar", self.browse_output).pack(side="left")

        self.btn_merge = _action_btn(self, "\U0001f500 Combinar PDFs", self.start_merge)
        self.btn_merge.pack(pady=10, padx=20, fill="x")

        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label = customtkinter.CTkLabel(self, text="",
                                                   font=customtkinter.CTkFont(size=11),
                                                   text_color=_theme_color("text_secondary"))
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
            row_bg = _theme_color("queue_row") if i % 2 == 0 else _theme_color("queue_row_alt")
            frame = customtkinter.CTkFrame(self.list_frame, fg_color=row_bg, corner_radius=6)
            frame.pack(fill="x", pady=2, padx=2)
            customtkinter.CTkLabel(frame, text=f"  \U0001f4c4  {i+1}. {path.name}",
                                   anchor="w", font=customtkinter.CTkFont(size=12)).pack(side="left", padx=6)
            customtkinter.CTkLabel(frame, text=f"{path.stat().st_size / 1024:.0f} KB",
                                   font=customtkinter.CTkFont(size=10),
                                   text_color=_theme_color("text_secondary")).pack(side="right", padx=10)
            self.list_labels.append(frame)
        self.status_label.configure(text=f"{len(self.file_list)} archivos seleccionados")

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
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar PDF combinado")
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
                self.after(0, lambda: self.status_label.configure(
                    text=f"\u2705 Completado: {os.path.basename(output)}",
                    text_color=_theme_color("success")))
                self.after(0, lambda: self.progress_bar.set(1))
            except Exception as ex:
                error_msg = str(ex)
                self.after(0, lambda err=error_msg: self.status_label.configure(
                    text=f"\u274c Error: {err}", text_color=_theme_color("error")))
            self.after(0, lambda: self.btn_merge.configure(state="normal", text="\U0001f500 Combinar PDFs"))

        threading.Thread(target=task, daemon=True).start()


class SplitPanel(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.input_pdf = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        _panel_title(self, "\u2702\ufe0f", "Dividir PDF",
                     "Divide un PDF en varios archivos por rangos o cada N p\u00e1ginas")

        input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        _action_btn(input_frame, "Seleccionar PDF", self.select_file).pack(side="left", padx=(0, 10))
        self.file_label = customtkinter.CTkLabel(input_frame, text="Ning\u00fan archivo seleccionado",
                                                 font=customtkinter.CTkFont(size=12),
                                                 text_color=_theme_color("text_secondary"))
        self.file_label.pack(side="left")

        mode_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=8)
        self.split_mode = customtkinter.StringVar(value="pages_per_file")
        customtkinter.CTkRadioButton(mode_frame, text="Rangos personalizados",
                                     variable=self.split_mode, value="ranges",
                                     command=self.toggle_mode).pack(anchor="w", pady=2)
        customtkinter.CTkRadioButton(mode_frame, text="Cada N p\u00e1ginas",
                                     variable=self.split_mode, value="pages_per_file",
                                     command=self.toggle_mode).pack(anchor="w", pady=2)

        self.options_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=20, pady=5)

        self.npages_frame = customtkinter.CTkFrame(self.options_frame, fg_color="transparent")
        customtkinter.CTkLabel(self.npages_frame, text="P\u00e1ginas por archivo:").pack(side="left", padx=(0, 10))
        self.npages_var = customtkinter.StringVar(value="5")
        customtkinter.CTkEntry(self.npages_frame, textvariable=self.npages_var, width=60).pack(side="left")
        self.npages_frame.pack(fill="x", pady=5)

        self.ranges_frame = customtkinter.CTkFrame(self.options_frame, fg_color="transparent")
        customtkinter.CTkLabel(self.ranges_frame, text="Rangos (ej: 1-3, 5-7, 10-15):").pack(anchor="w")
        self.ranges_var = customtkinter.StringVar(value="1-3, 4-6, 7-10")
        customtkinter.CTkEntry(self.ranges_frame, textvariable=self.ranges_var, width=300).pack(anchor="w", pady=2)
        self.ranges_frame.pack(fill="x", pady=5)
        self.ranges_frame.pack_forget()

        output_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        output_frame.pack(fill="x", padx=20, pady=8)
        customtkinter.CTkLabel(output_frame, text="Guardar en carpeta:").pack(side="left", padx=(0, 8))
        self.output_dir_var = customtkinter.StringVar(value=str(Path.home() / "Desktop"))
        customtkinter.CTkEntry(output_frame, textvariable=self.output_dir_var, width=250).pack(side="left", padx=(0, 8))
        _secondary_btn(output_frame, "Examinar", self.browse_output_dir).pack(side="left")

        self.btn_split = _action_btn(self, "\u2702\ufe0f Dividir PDF", self.start_split)
        self.btn_split.pack(pady=10, padx=20, fill="x")

        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label = customtkinter.CTkLabel(self, text="",
                                                   font=customtkinter.CTkFont(size=11),
                                                   text_color=_theme_color("text_secondary"))
        self.status_label.pack()

    def toggle_mode(self):
        if self.split_mode.get() == "ranges":
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
            self.file_label.configure(text=f"{self.input_pdf.name} ({pages} p\u00e1ginas)",
                                      text_color=_theme_color("text"))

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
                    text=f"\u2705 {len(result)} archivos generados", text_color=_theme_color("success")))
                self.after(0, lambda: self.progress_bar.set(1))
            except Exception as ex:
                error_msg = str(ex)
                self.after(0, lambda err=error_msg: self.status_label.configure(
                    text=f"\u274c Error: {err}", text_color=_theme_color("error")))
            self.after(0, lambda: self.btn_split.configure(state="normal", text="\u2702\ufe0f Dividir PDF"))

        threading.Thread(target=task, daemon=True).start()


class CompressPanel(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.input_pdf = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        _panel_title(self, "\U0001f4e6", "Comprimir PDF",
                     "Reduce el tama\u00f1o de un PDF re-salvando con optimizaci\u00f3n")

        input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        _action_btn(input_frame, "Seleccionar PDF", self.select_file).pack(side="left", padx=(0, 10))
        self.file_label = customtkinter.CTkLabel(input_frame, text="Ning\u00fan archivo seleccionado",
                                                 font=customtkinter.CTkFont(size=12),
                                                 text_color=_theme_color("text_secondary"))
        self.file_label.pack(side="left")

        quality_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        quality_frame.pack(fill="x", padx=20, pady=8)
        customtkinter.CTkLabel(quality_frame, text="Calidad:").pack(anchor="w")
        self.quality_var = customtkinter.StringVar(value="medium")
        radio_f = customtkinter.CTkFrame(quality_frame, fg_color="transparent")
        radio_f.pack(fill="x", pady=2)
        customtkinter.CTkRadioButton(radio_f, text="Alta", variable=self.quality_var, value="high").pack(side="left", padx=(0, 12))
        customtkinter.CTkRadioButton(radio_f, text="Media", variable=self.quality_var, value="medium").pack(side="left", padx=(0, 12))
        customtkinter.CTkRadioButton(radio_f, text="Baja", variable=self.quality_var, value="low").pack(side="left")

        self.btn_compress = _action_btn(self, "\U0001f4e6 Comprimir", self.start_compress)
        self.btn_compress.pack(pady=10, padx=20, fill="x")

        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label = customtkinter.CTkLabel(self, text="",
                                                   font=customtkinter.CTkFont(size=11),
                                                   text_color=_theme_color("text_secondary"))
        self.status_label.pack()

        self.btn_save = _secondary_btn(self, "Guardar como...", self.save_as, width=120)
        self.btn_save.configure(state="disabled")
        self.btn_save.pack(pady=5)

        self.last_result = None
        self.last_output = None

    def select_file(self):
        path = customtkinter.filedialog.askopenfilename(title="Seleccionar PDF", filetypes=[("PDF", "*.pdf")])
        if path:
            self.input_pdf = Path(path)
            info = get_pdf_info(path)
            self.file_label.configure(text=f"{self.input_pdf.name} ({info['size_mb']} MB, {info['pages']} p\u00e1gs)",
                                      text_color=_theme_color("text"))

    def start_compress(self):
        if not self.input_pdf:
            messagebox.showwarning("Aviso", "Selecciona un archivo PDF primero.")
            return
        output = str(self.input_pdf.parent / f"{self.input_pdf.stem}_comprimido.pdf")
        self.btn_compress.configure(state="disabled", text="Comprimiendo...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Iniciando...")

        def task():
            try:
                self.after(0, lambda: self.progress_bar.set(0.5))
                result = compress_pdf(str(self.input_pdf), output, quality=self.quality_var.get())
                self.last_result = result
                self.last_output = output
                ratio = result["ratio"]
                orig = result["original_size"] / (1024 * 1024)
                comp = result["compressed_size"] / (1024 * 1024)
                self.after(0, lambda: self.status_label.configure(
                    text=f"\u2705 {orig:.1f} MB \u2192 {comp:.1f} MB ({ratio}% reducci\u00f3n)",
                    text_color=_theme_color("success")))
                self.after(0, lambda: self.progress_bar.set(1))
                self.after(0, lambda: self.btn_save.configure(state="normal"))
            except Exception as ex:
                error_msg = str(ex)
                self.after(0, lambda err=error_msg: self.status_label.configure(
                    text=f"\u274c Error: {err}", text_color=_theme_color("error")))
            self.after(0, lambda: self.btn_compress.configure(state="normal", text="\U0001f4e6 Comprimir"))

        threading.Thread(target=task, daemon=True).start()

    def save_as(self):
        path = customtkinter.filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar PDF comprimido")
        if path and self.last_output:
            import shutil
            shutil.copy2(self.last_output, path)
            self.status_label.configure(text=f"\U0001f4be Guardado: {path}",
                                        text_color=_theme_color("success"))


class SanitizePanel(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.input_pdf = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        _panel_title(self, "\U0001f6e1\ufe0f", "Sanitizar PDF",
                     "Elimina scripts, formularios y metadatos potencialmente peligrosos")

        input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        _action_btn(input_frame, "Seleccionar PDF", self.select_file).pack(side="left", padx=(0, 10))
        self.file_label = customtkinter.CTkLabel(input_frame, text="Ning\u00fan archivo seleccionado",
                                                 font=customtkinter.CTkFont(size=12),
                                                 text_color=_theme_color("text_secondary"))
        self.file_label.pack(side="left")

        options_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=8)
        self.remove_js_var = customtkinter.BooleanVar(value=True)
        customtkinter.CTkCheckBox(options_frame, text="Eliminar scripts JavaScript (recomendado)",
                                  variable=self.remove_js_var).pack(anchor="w", pady=2)
        self.remove_forms_var = customtkinter.BooleanVar(value=True)
        customtkinter.CTkCheckBox(options_frame, text="Eliminar formularios y acetatas",
                                  variable=self.remove_forms_var).pack(anchor="w", pady=2)
        self.remove_metadata_var = customtkinter.BooleanVar(value=False)
        customtkinter.CTkCheckBox(options_frame, text="Limpiar metadatos (t\u00edtulo, autor, etc.)",
                                  variable=self.remove_metadata_var).pack(anchor="w", pady=2)

        self.btn_sanitize = _action_btn(self, "\U0001f6e1\ufe0f Sanitizar", self.start_sanitize)
        self.btn_sanitize.pack(pady=10, padx=20, fill="x")

        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label = customtkinter.CTkLabel(self, text="",
                                                   font=customtkinter.CTkFont(size=11),
                                                   text_color=_theme_color("text_secondary"))
        self.status_label.pack()

        self.btn_save = _secondary_btn(self, "Guardar como...", self.save_as, width=120)
        self.btn_save.configure(state="disabled")
        self.btn_save.pack(pady=5)
        self.last_output = None

    def select_file(self):
        path = customtkinter.filedialog.askopenfilename(title="Seleccionar PDF", filetypes=[("PDF", "*.pdf")])
        if path:
            self.input_pdf = Path(path)
            info = get_pdf_info(path)
            self.file_label.configure(text=f"{self.input_pdf.name} ({info['size_mb']} MB, {info['pages']} p\u00e1gs)",
                                      text_color=_theme_color("text"))

    def start_sanitize(self):
        if not self.input_pdf:
            messagebox.showwarning("Aviso", "Selecciona un archivo PDF primero.")
            return
        output = str(self.input_pdf.parent / f"{self.input_pdf.stem}_sanitizado.pdf")
        self.btn_sanitize.configure(state="disabled", text="Sanitizando...")
        self.progress_bar.set(0)

        def task():
            try:
                self.after(0, lambda: self.progress_bar.set(0.5))
                result = sanitize_pdf(str(self.input_pdf), output,
                                     remove_js=self.remove_js_var.get(),
                                     remove_forms=self.remove_forms_var.get(),
                                     remove_metadata=self.remove_metadata_var.get())
                self.last_output = output
                items = result["items_removed"]
                self.after(0, lambda: self.status_label.configure(
                    text=f"\u2705 {items} elemento(s) eliminado(s)",
                    text_color=_theme_color("success")))
                self.after(0, lambda: self.progress_bar.set(1))
                self.after(0, lambda: self.btn_save.configure(state="normal"))
            except Exception as ex:
                error_msg = str(ex)
                self.after(0, lambda err=error_msg: self.status_label.configure(
                    text=f"\u274c Error: {err}", text_color=_theme_color("error")))
            self.after(0, lambda: self.btn_sanitize.configure(state="normal", text="\U0001f6e1\ufe0f Sanitizar"))

        threading.Thread(target=task, daemon=True).start()

    def save_as(self):
        path = customtkinter.filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar PDF sanitizado")
        if path and self.last_output:
            import shutil
            shutil.copy2(self.last_output, path)
            self.status_label.configure(text=f"\U0001f4be Guardado: {path}",
                                        text_color=_theme_color("success"))


class DecryptPanel(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.input_pdf = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        _panel_title(self, "\U0001f513", "Descifrar PDF",
                     "Elimina la protecci\u00f3n por contrase\u00f1a de un PDF")

        input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        _action_btn(input_frame, "Seleccionar PDF", self.select_file).pack(side="left", padx=(0, 10))
        self.file_label = customtkinter.CTkLabel(input_frame, text="Ning\u00fan archivo seleccionado",
                                                 font=customtkinter.CTkFont(size=12),
                                                 text_color=_theme_color("text_secondary"))
        self.file_label.pack(side="left")

        self.status_info = customtkinter.CTkLabel(self, text="",
                                                  font=customtkinter.CTkFont(size=11))
        self.status_info.pack(padx=20, anchor="w")

        pw_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        pw_frame.pack(fill="x", padx=20, pady=8)
        customtkinter.CTkLabel(pw_frame, text="Contrase\u00f1a:").pack(side="left", padx=(0, 10))
        self.password_var = customtkinter.StringVar()
        self.pw_entry = customtkinter.CTkEntry(pw_frame, textvariable=self.password_var, width=200, show="*")
        self.pw_entry.pack(side="left")
        self.show_pw_var = customtkinter.BooleanVar(value=False)
        customtkinter.CTkCheckBox(pw_frame, text="Mostrar", variable=self.show_pw_var,
                                  command=self.toggle_password).pack(side="left", padx=10)

        self.btn_decrypt = _action_btn(self, "\U0001f513 Descifrar", self.start_decrypt)
        self.btn_decrypt.pack(pady=10, padx=20, fill="x")

        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label = customtkinter.CTkLabel(self, text="",
                                                   font=customtkinter.CTkFont(size=11),
                                                   text_color=_theme_color("text_secondary"))
        self.status_label.pack()

        self.btn_save = _secondary_btn(self, "Guardar como...", self.save_as, width=120)
        self.btn_save.configure(state="disabled")
        self.btn_save.pack(pady=5)
        self.last_output = None

    def toggle_password(self):
        self.pw_entry.configure(show="" if self.show_pw_var.get() else "*")

    def select_file(self):
        path = customtkinter.filedialog.askopenfilename(title="Seleccionar PDF", filetypes=[("PDF", "*.pdf")])
        if path:
            self.input_pdf = Path(path)
            info = get_pdf_info(path)
            enc = "Protegido con contrase\u00f1a" if info["encrypted"] else "Sin protecci\u00f3n"
            self.file_label.configure(text=f"{self.input_pdf.name} ({info['pages']} p\u00e1gs)",
                                      text_color=_theme_color("text"))
            color = _theme_color("warning") if info["encrypted"] else _theme_color("success")
            self.status_info.configure(text=f"\U0001f512 {enc}", text_color=color)

    def start_decrypt(self):
        if not self.input_pdf:
            messagebox.showwarning("Aviso", "Selecciona un archivo PDF primero.")
            return
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("Aviso", "Ingresa la contrase\u00f1a.")
            return
        output = str(self.input_pdf.parent / f"{self.input_pdf.stem}_descifrado.pdf")
        self.btn_decrypt.configure(state="disabled", text="Descifrando...")
        self.progress_bar.set(0)

        def task():
            try:
                self.after(0, lambda: self.progress_bar.set(0.5))
                result = decrypt_pdf(str(self.input_pdf), output, password)
                if result["success"]:
                    self.last_output = output
                    msg = f"\u2705 PDF descifrado: {result['pages']} p\u00e1ginas"
                    self.after(0, lambda: self.status_label.configure(text=msg, text_color=_theme_color("success")))
                    self.after(0, lambda: self.progress_bar.set(1))
                    self.after(0, lambda: self.btn_save.configure(state="normal"))
                else:
                    err = result.get("error", "Error desconocido")
                    self.after(0, lambda e=err: self.status_label.configure(
                        text=f"\u274c {e}", text_color=_theme_color("error")))
            except Exception as ex:
                error_msg = str(ex)
                self.after(0, lambda err=error_msg: self.status_label.configure(
                    text=f"\u274c Error: {err}", text_color=_theme_color("error")))
            self.after(0, lambda: self.btn_decrypt.configure(state="normal", text="\U0001f513 Descifrar"))

        threading.Thread(target=task, daemon=True).start()

    def save_as(self):
        path = customtkinter.filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar PDF descifrado")
        if path and self.last_output:
            import shutil
            shutil.copy2(self.last_output, path)
            self.status_label.configure(text=f"\U0001f4be Guardado: {path}",
                                        text_color=_theme_color("success"))


class BatchPanel(customtkinter.CTkFrame):
    def __init__(self, master, on_batch_convert=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_batch_convert = on_batch_convert
        self.folder_path = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        _panel_title(self, "\U0001f4e6", "Conversi\u00f3n por Lotes",
                     "Convierte todos los archivos compatibles de una carpeta")

        folder_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(fill="x", padx=20, pady=5)
        _action_btn(folder_frame, "Seleccionar Carpeta", self.select_folder).pack(side="left", padx=(0, 10))
        self.folder_label = customtkinter.CTkLabel(folder_frame, text="Ninguna carpeta seleccionada",
                                                   font=customtkinter.CTkFont(size=12),
                                                   text_color=_theme_color("text_secondary"))
        self.folder_label.pack(side="left")

        mode_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=8)
        self.mode_var = customtkinter.StringVar(value="pdf2word")
        customtkinter.CTkRadioButton(mode_frame, text="PDF a Word", variable=self.mode_var, value="pdf2word").pack(side="left", padx=(0, 12))
        customtkinter.CTkRadioButton(mode_frame, text="Word a PDF", variable=self.mode_var, value="word2pdf").pack(side="left")
        self.recursive_var = customtkinter.BooleanVar(value=False)
        customtkinter.CTkCheckBox(mode_frame, text="Incluir subcarpetas", variable=self.recursive_var).pack(side="left", padx=(20, 0))

        self.btn_convert = _action_btn(self, "\U0001f4e6 Convertir Lote", self.start_batch)
        self.btn_convert.pack(pady=10, padx=20, fill="x")

        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label = customtkinter.CTkLabel(self, text="",
                                                   font=customtkinter.CTkFont(size=11),
                                                   text_color=_theme_color("text_secondary"))
        self.status_label.pack()

        self.count_label = customtkinter.CTkLabel(self, text="",
                                                  font=customtkinter.CTkFont(size=11),
                                                  text_color=_theme_color("text_secondary"))
        self.count_label.pack(pady=5)

    def select_folder(self):
        path = customtkinter.filedialog.askdirectory(title="Seleccionar carpeta")
        if path:
            self.folder_path = Path(path)
            ext = self.mode_var.get()
            if ext == "pdf2word":
                count = len(list(self.folder_path.glob("*.pdf")))
                ext_label = "PDF"
            else:
                count = len(list(self.folder_path.glob("*.docx"))) + len(list(self.folder_path.glob("*.doc")))
                ext_label = "DOCX/DOC"
            self.folder_label.configure(text=f"{self.folder_path.name} ({count} archivos {ext_label})",
                                        text_color=_theme_color("text"))

    def start_batch(self):
        if not self.folder_path:
            messagebox.showwarning("Aviso", "Selecciona una carpeta primero.")
            return
        if not self.on_batch_convert:
            messagebox.showerror("Error", "Callback de conversi\u00f3n por lotes no configurado.")
            return
        self.btn_convert.configure(state="disabled", text="Procesando...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Encolando archivos...")

        def task():
            try:
                success, msg, job_ids = self.on_batch_convert(self.folder_path, self.mode_var.get(), self.recursive_var.get())
                if success:
                    self.after(0, lambda: self.status_label.configure(text=f"\u2705 {msg}",
                                                                      text_color=_theme_color("success")))
                    self.after(0, lambda: self.progress_bar.set(1))
                    self.after(0, lambda n=len(job_ids): self.count_label.configure(text=f"{n} archivos encolados"))
                else:
                    self.after(0, lambda m=msg: self.status_label.configure(text=m,
                                                                           text_color=_theme_color("warning")))
            except Exception as ex:
                error_msg = str(ex)
                self.after(0, lambda err=error_msg: self.status_label.configure(
                    text=f"\u274c Error: {err}", text_color=_theme_color("error")))
            self.after(0, lambda: self.btn_convert.configure(state="normal", text="\U0001f4e6 Convertir Lote"))

        threading.Thread(target=task, daemon=True).start()


class EncryptPanel(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.input_pdf = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        _panel_title(self, "\U0001f512", "Cifrar PDF",
                     "Protege un PDF con contrase\u00f1a y permisos de acceso")

        input_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        _action_btn(input_frame, "Seleccionar PDF", self.select_file).pack(side="left", padx=(0, 10))
        self.file_label = customtkinter.CTkLabel(input_frame, text="Ning\u00fan archivo seleccionado",
                                                  font=customtkinter.CTkFont(size=12),
                                                  text_color=_theme_color("text_secondary"))
        self.file_label.pack(side="left")

        pw_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        pw_frame.pack(fill="x", padx=20, pady=5)
        customtkinter.CTkLabel(pw_frame, text="Contrase\u00f1a de usuario:",
                               font=customtkinter.CTkFont(size=12, weight="bold"),
                               text_color=_theme_color("text")).pack(anchor="w")
        self.user_pw = customtkinter.CTkEntry(pw_frame, placeholder_text="Requerida", show="\u2022")
        self.user_pw.pack(fill="x", pady=2)
        customtkinter.CTkLabel(pw_frame, text="Contrase\u00f1a de propietario (opcional):",
                               font=customtkinter.CTkFont(size=12, weight="bold"),
                               text_color=_theme_color("text")).pack(anchor="w")
        self.owner_pw = customtkinter.CTkEntry(pw_frame, placeholder_text="Si se omite, se iguala a la de usuario", show="\u2022")
        self.owner_pw.pack(fill="x", pady=2)

        enc_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        enc_frame.pack(fill="x", padx=20, pady=5)
        customtkinter.CTkLabel(enc_frame, text="Nivel de cifrado:",
                               font=customtkinter.CTkFont(size=12, weight="bold"),
                               text_color=_theme_color("text")).pack(anchor="w")
        self.enc_var = customtkinter.StringVar(value="aes_256")
        for val, label in [("aes_256", "AES-256 (recomendado)"), ("aes_128", "AES-128"), ("rc4_128", "RC4-128")]:
            customtkinter.CTkRadioButton(enc_frame, text=label, variable=self.enc_var, value=val).pack(anchor="w", pady=1)

        perms_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        perms_frame.pack(fill="x", padx=20, pady=5)
        customtkinter.CTkLabel(perms_frame, text="Permisos:",
                               font=customtkinter.CTkFont(size=12, weight="bold"),
                               text_color=_theme_color("text")).pack(anchor="w")
        self.print_var = customtkinter.BooleanVar(value=True)
        self.copy_var = customtkinter.BooleanVar(value=True)
        self.modify_var = customtkinter.BooleanVar(value=True)
        self.annotate_var = customtkinter.BooleanVar(value=True)
        customtkinter.CTkCheckBox(perms_frame, text="Permitir impresi\u00f3n", variable=self.print_var).pack(anchor="w", pady=1)
        customtkinter.CTkCheckBox(perms_frame, text="Permitir copia de texto", variable=self.copy_var).pack(anchor="w", pady=1)
        customtkinter.CTkCheckBox(perms_frame, text="Permitir modificaci\u00f3n", variable=self.modify_var).pack(anchor="w", pady=1)
        customtkinter.CTkCheckBox(perms_frame, text="Permitir anotaciones", variable=self.annotate_var).pack(anchor="w", pady=1)

        self.btn_encrypt = _action_btn(self, "\U0001f512 Cifrar PDF", self.start_encrypt)
        self.btn_encrypt.pack(pady=10, padx=20, fill="x")

        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.status_label = customtkinter.CTkLabel(self, text="",
                                                    font=customtkinter.CTkFont(size=11),
                                                    text_color=_theme_color("text_secondary"))
        self.status_label.pack()

    def select_file(self):
        path = customtkinter.filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.input_pdf = path
            self.file_label.configure(text=os.path.basename(path), text_color=_theme_color("text"))

    def start_encrypt(self):
        if not self.input_pdf:
            messagebox.showwarning("Aviso", "Selecciona un archivo PDF primero.")
            return
        user_pw = self.user_pw.get().strip()
        if not user_pw:
            messagebox.showwarning("Aviso", "La contrase\u00f1a de usuario es obligatoria.")
            return
        owner_pw = self.owner_pw.get().strip()
        out_path = customtkinter.filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
            initialfile=os.path.basename(self.input_pdf).replace(".pdf", "_cifrado.pdf"))
        if not out_path:
            return
        self.btn_encrypt.configure(state="disabled", text="Cifrando...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Cifrando PDF...")

        def task():
            try:
                result = encrypt_pdf(
                    self.input_pdf, out_path,
                    user_password=user_pw,
                    owner_password=owner_pw,
                    print_perm=self.print_var.get(),
                    copy_perm=self.copy_var.get(),
                    modify_perm=self.modify_var.get(),
                    annotate_perm=self.annotate_var.get(),
                    encryption_level=self.enc_var.get(),
                )
                if result["success"]:
                    self.after(0, lambda: self.status_label.configure(
                        text=f"\u2705 PDF cifrado: {os.path.basename(out_path)}",
                        text_color=_theme_color("success")))
                    self.after(0, lambda: self.progress_bar.set(1))
                else:
                    self.after(0, lambda: self.status_label.configure(
                        text=f"\u274c Error: {result.get('error', 'Desconocido')}",
                        text_color=_theme_color("error")))
            except Exception as ex:
                error_msg = str(ex)
                self.after(0, lambda err=error_msg: self.status_label.configure(
                    text=f"\u274c Error: {err}", text_color=_theme_color("error")))
            self.after(0, lambda: self.btn_encrypt.configure(state="normal", text="\U0001f512 Cifrar PDF"))

        threading.Thread(target=task, daemon=True).start()
