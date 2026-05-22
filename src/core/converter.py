import os
import logging
import pythoncom
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional, Tuple
from pdf2docx import Converter
from docx2pdf import convert as word_to_pdf_conv
from core.error_handler import PermissionDeniedError, FileCorruptedError, EasyConverterError
from utils.word_checker import WordChecker

# Configuración de logging
logger = logging.getLogger(__name__)

class EasyConverter:
    @staticmethod
    def pdf_to_docx(pdf_path: str, output_path: Optional[str] = None, progress_tracker=None) -> Tuple[bool, str]:
        """
        Convierte un archivo PDF a DOCX con seguimiento de progreso basado en páginas.
        """
        try:
            pdf_path_obj = Path(pdf_path)
            if not pdf_path_obj.exists():
                raise FileNotFoundError(f"No se encontró el archivo: {pdf_path}")
            
            docx_path = Path(output_path) if output_path else pdf_path_obj.with_suffix('.docx')
            
            if progress_tracker:
                progress_tracker.start("Analizando PDF...")

            # Obtener número de páginas para progreso real
            with fitz.open(str(pdf_path_obj)) as doc:
                total_pages = len(doc)
            
            # Verificar permisos
            if docx_path.exists():
                try:
                    with open(docx_path, 'a'): pass
                except PermissionError:
                    raise PermissionDeniedError(f"No se puede escribir en {docx_path}. ¿Está abierto?")

            cv = Converter(str(pdf_path_obj))
            
            # Conversión por bloques o páginas si la librería lo permite, 
            # de lo contrario simulamos pasos lógicos basados en el total
            if progress_tracker:
                progress_tracker.update(10, f"Iniciando conversión de {total_pages} páginas...")
            
            if progress_tracker:
                progress_tracker.update(50, f"Convirtiendo PDF a Word...")

            cv.convert(str(docx_path), start=0, end=None)
            
            cv.close()
            
            if progress_tracker:
                progress_tracker.update(100, "¡Conversión finalizada!")
                progress_tracker.complete(str(docx_path))
                
            return True, str(docx_path)
            
        except Exception as e:
            logger.error(f"Error en pdf_to_docx: {str(e)}")
            if progress_tracker:
                progress_tracker.error(e)
            raise e

    @staticmethod
    def docx_to_pdf(docx_path: str, output_path: Optional[str] = None, progress_tracker=None) -> Tuple[bool, str]:
        """
        Convierte un archivo DOCX a PDF manejando el contexto COM de Windows y fases de progreso.
        """
        # Inicialización de COM — verificar estado para evitar crash en threads donde ya está inicializado
        com_was_init = False
        try:
            pythoncom.CoInitialize()
        except pythoncom.com_error:
            com_was_init = True
        try:
            docx_path_obj = Path(docx_path)
            if not docx_path_obj.exists():
                raise FileNotFoundError(f"No se encontró el archivo: {docx_path}")

            if progress_tracker:
                progress_tracker.start("Fase 1/3: Validando entorno...")

            WordChecker.check_word_or_fail()

            pdf_path = Path(output_path) if output_path else docx_path_obj.with_suffix('.pdf')

            # Verificar permisos en destino
            if pdf_path.exists():
                try:
                    with open(pdf_path, 'a'): pass
                except PermissionError:
                    raise PermissionDeniedError(f"No se puede escribir en {pdf_path}. ¿Está abierto?")

            if progress_tracker:
                progress_tracker.update(40, "Fase 2/3: Renderizando con Microsoft Word...")

            # Conversión real
            word = None
            doc = None
            if docx_path_obj.suffix.lower() == '.doc':
                # docx2pdf no soporta .doc, usamos COM directo
                import win32com.client
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                doc = word.Documents.Open(str(docx_path_obj))
                doc.SaveAs(str(pdf_path), FileFormat=17) # 17 = wdFormatPDF
                doc.Close()
                doc = None
            else:
                word_to_pdf_conv(str(docx_path_obj), str(pdf_path))
            
            if progress_tracker:
                progress_tracker.update(100, "Fase 3/3: ¡Conversión finalizada!")
                progress_tracker.complete(str(pdf_path))
                
            return True, str(pdf_path)
            
        except Exception as e:
            logger.error(f"Error en docx_to_pdf: {str(e)}")
            if progress_tracker:
                progress_tracker.error(e)
            raise e
        finally:
            # Cerrar Word correctamente para evitar WINWORD.EXE zombies
            if doc is not None:
                try:
                    doc.Close()
                except Exception:
                    pass
                doc = None
            if word is not None:
                try:
                    word.Quit()
                except Exception:
                    pass
                word = None
            import gc
            gc.collect()
            # Solo liberar COM si no nosotros lo inicializamos
            if not com_was_init:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
