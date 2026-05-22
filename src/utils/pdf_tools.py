"""
Utilidades PDF usando PyMuPDF (fitz).
Funciones de alto nivel para extraer metadatos, texto, imágenes y previsualizar.
"""
import logging
from pathlib import Path
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

def get_page_count(pdf_path: str) -> int:
    """Retorna el número de páginas de un PDF."""
    import fitz
    try:
        with fitz.open(str(pdf_path)) as doc:
            return len(doc)
    except Exception as e:
        logger.error(f"Error contando páginas: {e}")
        return 0


def get_pdf_info(pdf_path: str) -> dict:
    """Retorna metadatos básicos del PDF."""
    import fitz
    try:
        with fitz.open(str(pdf_path)) as doc:
            meta = doc.metadata
            return {
                "pages": len(doc),
                "title": meta.get("title", ""),
                "author": meta.get("author", ""),
                "subject": meta.get("subject", ""),
                "creator": meta.get("creator", ""),
                "encrypted": doc.is_encrypted,
            }
    except Exception as e:
        logger.error(f"Error extrayendo metadatos: {e}")
        return {}


def extract_text_page(pdf_path: str, page_num: int) -> str:
    """Extrae el texto de una página específica."""
    import fitz
    try:
        with fitz.open(str(pdf_path)) as doc:
            if 0 <= page_num < len(doc):
                return doc[page_num].get_text()
            return ""
    except Exception as e:
        logger.error(f"Error extrayendo texto página {page_num}: {e}")
        return ""


def extract_all_text(pdf_path: str) -> str:
    """Extrae todo el texto del PDF."""
    import fitz
    try:
        with fitz.open(str(pdf_path)) as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        logger.error(f"Error extrayendo texto: {e}")
        return ""


def render_thumbnail(pdf_path: str, page_num: int = 0, size: Tuple[int, int] = (200, 280)) -> Optional[bytes]:
    """
    Genera un thumbnail PNG de una página del PDF.
    Retorna bytes PNG o None si falla.
    """
    import fitz
    try:
        with fitz.open(str(pdf_path)) as doc:
            if 0 <= page_num < len(doc):
                page = doc[page_num]
                mat = fitz.Matrix(size[0] / page.rect.width, size[1] / page.rect.height)
                pix = page.get_pixmap(matrix=mat)
                return pix.tobytes("png")
            return None
    except Exception as e:
        logger.error(f"Error generando thumbnail: {e}")
        return None


def is_valid_pdf(pdf_path: str) -> bool:
    """Verifica rápidamente si el archivo es un PDF válido."""
    import fitz
    try:
        with fitz.open(str(pdf_path)) as doc:
            return len(doc) > 0
    except Exception:
        return False


def get_pdf_images(pdf_path: str, page_num: int) -> List[dict]:
    """Lista las imágenes嵌入adas en una página específica."""
    import fitz
    try:
        with fitz.open(str(pdf_path)) as doc:
            if 0 <= page_num < len(doc):
                images = []
                for img_index, img in enumerate(doc[page_num].get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    images.append({
                        "index": img_index,
                        "xref": xref,
                        "width": base_image["width"],
                        "height": base_image["height"],
                        "colorspace": base_image["colorspace"],
                        "bpc": base_image["bpc"],
                        "ext": base_image["ext"],
                    })
                return images
            return []
    except Exception as e:
        logger.error(f"Error extrayendo imágenes página {page_num}: {e}")
        return []