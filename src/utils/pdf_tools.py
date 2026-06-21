import os
import fitz
from pathlib import Path
from typing import List, Optional, Dict, Any


def get_metadata(pdf_path: str) -> Dict[str, Any]:
    doc = fitz.open(pdf_path)
    try:
        metadata = doc.metadata or {}
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "pages": len(doc),
            "format": f"{doc.page_width(0):.0f}x{doc.page_height(0):.0f} pts" if len(doc) > 0 else "N/A",
            "encrypted": doc.is_encrypted,
        }
    finally:
        doc.close()


def get_page_count(pdf_path: str) -> int:
    doc = fitz.open(pdf_path)
    try:
        return len(doc)
    finally:
        doc.close()


def merge_pdfs(pdf_paths: List[str], output_path: str, progress_callback=None) -> str:
    merged = fitz.open()
    total = len(pdf_paths)
    try:
        for i, path in enumerate(pdf_paths):
            with fitz.open(path) as src:
                merged.insert_pdf(src)
            if progress_callback:
                progress_callback(int((i + 1) / total * 100), f"Combinando {i+1}/{total}")
        merged.save(output_path, deflate=True)
    finally:
        merged.close()
    return output_path


def split_pdf(pdf_path: str, output_dir: str, ranges: Optional[List[tuple]] = None, pages_per_file: int = 1) -> List[str]:
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    output_paths = []
    try:
        if ranges:
            for start, end in ranges:
                start = max(0, start)
                end = min(total_pages - 1, end)
                if start > end:
                    continue
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start, to_page=end)
                base = Path(pdf_path).stem
                out_path = os.path.join(output_dir, f"{base}_pag{start+1}-{end+1}.pdf")
                new_doc.save(out_path, deflate=True)
                new_doc.close()
                output_paths.append(out_path)
        else:
            for start in range(0, total_pages, pages_per_file):
                end = min(start + pages_per_file - 1, total_pages - 1)
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start, to_page=end)
                base = Path(pdf_path).stem
                out_path = os.path.join(output_dir, f"{base}_pag{start+1}-{end+1}.pdf")
                new_doc.save(out_path, deflate=True)
                new_doc.close()
                output_paths.append(out_path)
    finally:
        doc.close()
    return output_paths


def extract_text_with_ocr(pdf_path: str, lang: str = "spa") -> str:
    try:
        import pytesseract
        from PIL import Image
        import io
    except ImportError:
        return ""
    doc = fitz.open(pdf_path)
    text_parts = []
    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang=lang)
            text_parts.append(text)
    finally:
        doc.close()
    return "\n".join(text_parts)
