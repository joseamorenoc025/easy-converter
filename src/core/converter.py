import gc
import logging
import pythoncom
import win32com.client
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional, Tuple
from pdf2docx import Converter
from core.error_handler import PermissionDeniedError
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
                    with open(docx_path, 'a'):
                        pass  # Verificar acceso de escritura
                except PermissionError:
                    raise PermissionDeniedError(f"No se puede escribir en {docx_path}. ¿Está abierto?")

            cv = Converter(str(pdf_path_obj))
            
            # Conversión por bloques o páginas si la librería lo permite, 
            # de lo contrario simulamos pasos lógicos basados en el total
            if progress_tracker:
                progress_tracker.update(10, f"Iniciando conversión de {total_pages} páginas...")
            
            # Callback nativo de pdf2docx
            def on_page_update(page_num, total_pages_cb):
                if progress_tracker:
                    percent = int((page_num / total_pages_cb) * 100)
                    progress_tracker.update(percent, f"Convirtiendo página {page_num}/{total_pages_cb}")

            cv.convert(str(docx_path), start=0, end=None, callbacks=[on_page_update])
            
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
        com_initialized = False
        word = None
        doc = None
        try:
            pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
            com_initialized = True
        except RuntimeError:
            pass
        try:
            docx_path_obj = Path(docx_path)
            if not docx_path_obj.exists():
                raise FileNotFoundError(f"No se encontró el archivo: {docx_path}")

            if progress_tracker:
                progress_tracker.start("Fase 1/3: Validando entorno...")

            WordChecker.check_word_or_fail()

            pdf_path = Path(output_path) if output_path else docx_path_obj.with_suffix('.pdf')

            if pdf_path.exists():
                try:
                    with open(pdf_path, 'a'):
                        pass
                except PermissionError:
                    raise PermissionDeniedError(f"No se puede escribir en {pdf_path}. ¿Está abierto?")

            if progress_tracker:
                progress_tracker.update(40, "Fase 2/3: Renderizando con Microsoft Word...")

            # Conversión directa con win32com (sin docx2pdf que causa freezes)
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False
            word.ScreenUpdating = False

            doc = word.Documents.Open(str(docx_path_obj))
            doc.SaveAs(str(pdf_path), FileFormat=17)  # 17 = wdFormatPDF
            doc.Close(False)

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
            if doc is not None:
                try:
                    doc.Close(False)
                except Exception:
                    pass
                doc = None
            if word is not None:
                try:
                    word.Quit()
                except Exception:
                    pass
                word = None
            gc.collect()
            if com_initialized:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
