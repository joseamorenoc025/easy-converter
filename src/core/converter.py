import os
from pathlib import Path
from pdf2docx import Converter
from docx2pdf import convert as word_to_pdf_conv
from core.error_handler import PermissionDeniedError, FileCorruptedError, EasyConverterError
from utils.word_checker import WordChecker

class EasyConverter:
    @staticmethod
    def pdf_to_docx(pdf_path, output_path=None, progress_tracker=None):
        """
        Convierte un archivo PDF a DOCX con seguimiento de progreso.
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"No se encontró el archivo: {pdf_path}")
            
            # Si no se provee output_path, usar el default (misma carpeta)
            docx_path = Path(output_path) if output_path else pdf_path.with_suffix('.docx')
            
            if progress_tracker:
                progress_tracker.start("Analizando PDF...")

            # Verificar permisos
            if docx_path.exists():
                try:
                    with open(docx_path, 'a'): pass
                except PermissionError:
                    raise PermissionDeniedError(f"No se puede escribir en {docx_path}. ¿Está abierto?")

            cv = Converter(str(pdf_path))
            
            if progress_tracker:
                progress_tracker.update(20, "Extrayendo texto e imágenes...")
            
            cv.convert(str(docx_path), start=0, end=None)
            
            if progress_tracker:
                progress_tracker.update(80, "Reconstruyendo estilos y tablas...")
            
            cv.close()
            
            if progress_tracker:
                progress_tracker.update(100, "¡Conversión finalizada!")
                progress_tracker.complete(str(docx_path))
                
            return True, str(docx_path)
            
        except Exception as e:
            if progress_tracker:
                progress_tracker.error(e)
            raise e

    @staticmethod
    def docx_to_pdf(docx_path, output_path=None, progress_tracker=None):
        """
        Convierte un archivo DOCX a PDF con seguimiento de progreso.
        """
        try:
            docx_path = Path(docx_path)
            if not docx_path.exists():
                raise FileNotFoundError(f"No se encontró el archivo: {docx_path}")

            if progress_tracker:
                progress_tracker.start("Validando entorno...")

            WordChecker.check_word_or_fail()

            # Si no se provee output_path, usar el default (misma carpeta)
            pdf_path = Path(output_path) if output_path else docx_path.with_suffix('.pdf')

            if progress_tracker:
                progress_tracker.update(30, "Abriendo Microsoft Word...")

            # Verificar permisos
            if pdf_path.exists():
                try:
                    with open(pdf_path, 'a'): pass
                except PermissionError:
                    raise PermissionDeniedError(f"No se puede escribir en {pdf_path}. ¿Está abierto?")

            if progress_tracker:
                progress_tracker.update(50, "Renderizando páginas...")

            word_to_pdf_conv(str(docx_path), str(pdf_path))
            
            if progress_tracker:
                progress_tracker.update(100, "¡Conversión finalizada!")
                progress_tracker.complete(str(pdf_path))
                
            return True, str(pdf_path)
            
        except Exception as e:
            if progress_tracker:
                progress_tracker.error(e)
            raise e
