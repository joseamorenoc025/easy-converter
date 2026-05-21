import os
from pathlib import Path
from utils.config import ConfigManager

class PathManager:
    def __init__(self, config: ConfigManager):
        self.config = config

    def resolve_output_path(self, input_path: Path, mode: str) -> Path:
        """
        Calcula la ruta de salida basada en las preferencias del usuario.
        """
        output_mode = self.config.get("output_mode")
        ext = ".docx" if mode == "pdf2word" else ".pdf"
        
        if output_mode == "same_folder":
            return input_path.with_suffix(ext)
        
        elif output_mode == "subfolder":
            subfolder = input_path.parent / "convertidos"
            subfolder.mkdir(exist_ok=True)
            return subfolder / (input_path.stem + ext)
            
        elif output_mode == "custom":
            custom_path = self.config.get("custom_path")
            if custom_path and os.path.isdir(custom_path):
                return Path(custom_path) / (input_path.stem + ext)
            return input_path.with_suffix(ext) # Fallback
            
        return input_path.with_suffix(ext)

    @staticmethod
    def open_in_explorer(path: Path):
        """Abre el explorador de Windows en la carpeta del archivo o carpeta dada"""
        try:
            if path.is_file():
                os.startfile(path.parent)
            else:
                os.startfile(path)
        except Exception as e:
            print(f"No se pudo abrir la carpeta: {e}")
