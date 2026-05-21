import customtkinter
import os
import threading
from tkinterdnd2 import TkinterDnD, DND_FILES
from converter import EasyConverter
from tkinter import messagebox

# Configuración estética global
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # Configuración de ventana
        self.title("Easy Converter - PDF ↔ Word")
        self.geometry("600x450")
        self.resizable(False, False)

        # Variables de estado
        self.selected_file = None
        self.conversion_mode = "pdf2word" # Default

        self.setup_ui()

    def setup_ui(self):
        # Título principal
        self.label_title = customtkinter.CTkLabel(
            self, text="EASY CONVERTER", 
            font=customtkinter.CTkFont(size=24, weight="bold")
        )
        self.label_title.pack(pady=(30, 10))

        self.label_subtitle = customtkinter.CTkLabel(
            self, text="Conversor rápido y ligero", 
            font=customtkinter.CTkFont(size=13),
            text_color="gray"
        )
        self.label_subtitle.pack(pady=(0, 20))

        # Selector de modo
        self.mode_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.mode_frame.pack(pady=10)

        self.btn_pdf2word = customtkinter.CTkButton(
            self.mode_frame, text="PDF a Word", 
            command=lambda: self.set_mode("pdf2word"),
            width=120, height=35, corner_radius=10,
            fg_color="#1f538d" # Active color
        )
        self.btn_pdf2word.grid(row=0, column=0, padx=10)

        self.btn_word2pdf = customtkinter.CTkButton(
            self.mode_frame, text="Word a PDF", 
            command=lambda: self.set_mode("word2pdf"),
            width=120, height=35, corner_radius=10,
            fg_color="gray30"
        )
        self.btn_word2pdf.grid(row=0, column=1, padx=10)

        # Zona de Arrastre (Drop Zone)
        self.drop_frame = customtkinter.CTkFrame(self, width=500, height=180, corner_radius=15)
        self.drop_frame.pack(pady=(20, 10), padx=50)
        self.drop_frame.pack_propagate(False)

        self.drop_label = customtkinter.CTkLabel(
            self.drop_frame, 
            text="Arrastra tu archivo aquí\no haz clic para seleccionar",
            font=customtkinter.CTkFont(size=14)
        )
        self.drop_label.pack(expand=True)

        # Hacer que el frame y el label respondan al clic
        self.drop_frame.bind("<Button-1>", lambda e: self.select_file_dialog())
        self.drop_label.bind("<Button-1>", lambda e: self.select_file_dialog())

        # Habilitar Drag & Drop en el frame
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

        # Barra de progreso (oculta por defecto)
        self.progress_bar = customtkinter.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        
        # Estado y Botón de Acción
        self.status_label = customtkinter.CTkLabel(self, text="", font=customtkinter.CTkFont(size=12))
        self.status_label.pack(pady=5)

        self.convert_button = customtkinter.CTkButton(
            self, text="CONVERTIR AHORA", 
            command=self.start_conversion,
            state="disabled",
            width=200, height=45, font=customtkinter.CTkFont(size=14, weight="bold")
        )
        self.convert_button.pack(pady=10)

    def select_file_dialog(self):
        file_path = customtkinter.filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Archivos compatibles", "*.pdf *.docx *.doc"), ("PDF", "*.pdf"), ("Word", "*.docx *.doc")]
        )
        if file_path:
            self.process_selected_file(file_path)

    def handle_drop(self, event):
        file_path = event.data
        # Limpieza de ruta en Windows
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        self.process_selected_file(file_path)

    def process_selected_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            self.set_mode("pdf2word")
            self.selected_file = file_path
        elif ext in ['.docx', '.doc']:
            self.set_mode("word2pdf")
            self.selected_file = file_path
        else:
            messagebox.showwarning("Archivo no válido", "Por favor, selecciona solo archivos PDF o Word.")
            return

        self.drop_label.configure(text=f"Archivo seleccionado:\n{os.path.basename(file_path)}")
        self.convert_button.configure(state="normal")
        self.status_label.configure(text="Listo para convertir", text_color="green")

    def set_mode(self, mode):
        self.conversion_mode = mode
        if mode == "pdf2word":
            self.btn_pdf2word.configure(fg_color="#1f538d")
            self.btn_word2pdf.configure(fg_color="gray30")
        else:
            self.btn_word2pdf.configure(fg_color="#1f538d")
            self.btn_pdf2word.configure(fg_color="gray30")
        self.update_status()

    def update_status(self):
        if self.selected_file:
            # Si cambiamos el modo manualmente, verificamos si el archivo actual es compatible con ese modo
            ext = os.path.splitext(self.selected_file)[1].lower()
            is_valid = False
            if self.conversion_mode == "pdf2word" and ext == ".pdf":
                is_valid = True
            elif self.conversion_mode == "word2pdf" and ext in [".docx", ".doc"]:
                is_valid = True
            
            if is_valid:
                self.convert_button.configure(state="normal")
                self.status_label.configure(text="Listo para convertir", text_color="green")
            else:
                self.convert_button.configure(state="disabled")
                self.status_label.configure(text="El modo no coincide con el archivo", text_color="orange")
        else:
            self.convert_button.configure(state="disabled")

    def start_conversion(self):
        self.convert_button.configure(state="disabled")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        self.status_label.configure(text="Convirtiendo... por favor espere", text_color="orange")
        
        # Ejecutar conversión en un hilo separado para no congelar la UI
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()

    def run_conversion(self):
        if self.conversion_mode == "pdf2word":
            success, result = EasyConverter.pdf_to_docx(self.selected_file)
        else:
            success, result = EasyConverter.docx_to_pdf(self.selected_file)

        self.after(0, lambda: self.finish_conversion(success, result))

    def finish_conversion(self, success, result):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.convert_button.configure(state="normal")

        if success:
            self.status_label.configure(text="¡Conversión exitosa!", text_color="green")
            if messagebox.askyesno("Éxito", f"Archivo guardado en:\n{result}\n\n¿Deseas abrir la carpeta?"):
                os.startfile(os.path.dirname(result))
        else:
            self.status_label.configure(text="Error en la conversión", text_color="red")
            messagebox.showerror("Error", f"Ocurrió un error:\n{result}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
