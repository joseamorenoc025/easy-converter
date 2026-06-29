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
            "format": f"{doc[0].rect.width:.0f}x{doc[0].rect.height:.0f} pts" if len(doc) > 0 else "N/A",
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
        from utils.platform_service import WindowsPlatformService
        tesseract_path = WindowsPlatformService().get_tesseract_path()
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = str(tesseract_path)
            os.environ["TESSDATA_PREFIX"] = str(tesseract_path.parent)
    except ImportError:
        return ""
    doc = fitz.open(pdf_path)
    text_parts = []
    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            text = pytesseract.image_to_string(img, lang=lang)
            text_parts.append(text)
    finally:
        doc.close()
    return "\n".join(text_parts)


def compress_pdf(input_path: str, output_path: str, quality: str = "medium") -> Dict[str, Any]:
    quality_settings = {
        "low": {"garbage": 4, "deflate": True, "clean": True},
        "medium": {"garbage": 3, "deflate": True, "clean": False},
        "high": {"garbage": 2, "deflate": True, "clean": False},
    }
    settings = quality_settings.get(quality, quality_settings["medium"])
    original_size = os.path.getsize(input_path)
    doc = fitz.open(input_path)
    try:
        doc.save(output_path, garbage=settings["garbage"],
                 deflate=settings["deflate"], clean=settings["clean"])
    finally:
        doc.close()
    compressed_size = os.path.getsize(output_path)
    ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
    return {
        "success": True,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "ratio": round(ratio, 1),
    }


def sanitize_pdf(input_path: str, output_path: str,
                 remove_js: bool = True, remove_forms: bool = True,
                 remove_metadata: bool = False) -> Dict[str, Any]:
    original_size = os.path.getsize(input_path)
    doc = fitz.open(input_path)
    items_removed = 0
    try:
        if remove_js:
            for page in doc:
                xref = page.xref
                try:
                    if doc.xref_get_key(xref, "OpenAction"):
                        doc.xref_set_key(xref, "OpenAction", "null")
                        items_removed += 1
                except Exception:
                    pass
                try:
                    if doc.xref_get_key(xref, "AA"):
                        doc.xref_set_key(xref, "AA", "null")
                        items_removed += 1
                except Exception:
                    pass
            try:
                cat_xref = doc.pdf_catalog()
                for key in ("JavaScript", "OpenAction", "AA"):
                    try:
                        val = doc.xref_get_key(cat_xref, key)
                        if val:
                            doc.xref_set_key(cat_xref, key, "null")
                            items_removed += 1
                    except Exception:
                        pass
            except Exception:
                pass
        if remove_forms:
            for page in doc:
                widgets = page.widgets()
                if widgets:
                    for widget in list(widgets):
                        page.delete_widget(widget)
                        items_removed += 1
        if remove_metadata:
            doc.set_metadata({})
            items_removed += 1
        doc.save(output_path, garbage=4, deflate=True)
    finally:
        doc.close()
    sanitized_size = os.path.getsize(output_path)
    return {
        "success": True,
        "original_size": original_size,
        "sanitized_size": sanitized_size,
        "items_removed": items_removed,
    }


def decrypt_pdf(input_path: str, output_path: str, password: str) -> Dict[str, Any]:
    doc = fitz.open(input_path)
    try:
        if not doc.is_encrypted:
            return {"success": True, "was_encrypted": False, "pages": len(doc)}
        auth_result = doc.authenticate(password)
        if auth_result == 0:
            return {"success": False, "was_encrypted": True, "error": "Contrasena incorrecta"}
        doc.save(output_path, garbage=4, deflate=True)
        pages = len(doc)
        return {"success": True, "was_encrypted": True, "pages": pages}
    except Exception as e:
        return {"success": False, "was_encrypted": True, "error": str(e)}
    finally:
        doc.close()


def get_pdf_info(pdf_path: str) -> Dict[str, Any]:
    doc = fitz.open(pdf_path)
    try:
        file_size = os.path.getsize(pdf_path)
        return {
            "path": pdf_path,
            "pages": len(doc),
            "encrypted": doc.is_encrypted,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "title": (doc.metadata or {}).get("title", ""),
            "author": (doc.metadata or {}).get("author", ""),
            "format": f"{doc[0].rect.width:.0f}x{doc[0].rect.height:.0f} pts" if len(doc) > 0 else "N/A",
        }
    finally:
        doc.close()


def encrypt_pdf(input_path: str, output_path: str,
                user_password: str, owner_password: str = "",
                print_perm: bool = True, copy_perm: bool = True,
                modify_perm: bool = True, annotate_perm: bool = True,
                encryption_level: str = "aes_256") -> Dict[str, Any]:
    if not user_password:
        return {"success": False, "error": "La contrase\u00f1a de usuario es obligatoria"}
    if not os.path.exists(input_path):
        return {"success": False, "error": "Archivo de entrada no encontrado"}

    enc_map = {
        "aes_256": fitz.PDF_ENCRYPT_AES_256,
        "aes_128": fitz.PDF_ENCRYPT_AES_128,
        "rc4_128": fitz.PDF_ENCRYPT_AES_128,
    }
    enc_method = enc_map.get(encryption_level, fitz.PDF_ENCRYPT_AES_256)

    perms = 0
    if print_perm:
        perms |= fitz.PDF_PERM_PRINT
    if copy_perm:
        perms |= fitz.PDF_PERM_COPY
    if modify_perm:
        perms |= fitz.PDF_PERM_MODIFY
    if annotate_perm:
        perms |= fitz.PDF_PERM_ANNOTATE

    owner_pw = owner_password if owner_password else user_password
    original_size = os.path.getsize(input_path)
    doc = fitz.open(input_path)
    try:
        doc.save(output_path, garbage=4, deflate=True,
                 encryption=enc_method,
                 permissions=perms,
                 owner_pw=owner_pw,
                 user_pw=user_password)
    finally:
        doc.close()

    return {
        "success": True,
        "original_size": original_size,
        "encrypted_size": os.path.getsize(output_path),
        "encryption_level": encryption_level,
    }
