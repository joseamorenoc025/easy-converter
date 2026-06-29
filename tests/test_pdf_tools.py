"""Tests para pdf_tools."""
import pytest
import fitz
from pathlib import Path
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from utils.pdf_tools import (
    get_metadata, get_page_count, merge_pdfs, split_pdf,
    compress_pdf, sanitize_pdf, decrypt_pdf, get_pdf_info,
)


@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello World")
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def multi_pdf(tmp_path):
    pdf_path = tmp_path / "multi.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.new_page()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


class TestPdfTools:
    def test_get_metadata(self, sample_pdf):
        meta = get_metadata(str(sample_pdf))
        assert meta["pages"] == 1
        assert meta["encrypted"] is False

    def test_get_page_count(self, sample_pdf):
        count = get_page_count(str(sample_pdf))
        assert count == 1

    def test_merge_pdfs(self, sample_pdf, tmp_path):
        output = tmp_path / "merged.pdf"
        result = merge_pdfs([str(sample_pdf), str(sample_pdf)], str(output))
        assert Path(result).exists()
        doc = fitz.open(result)
        assert len(doc) == 2
        doc.close()

    def test_merge_with_callback(self, sample_pdf, tmp_path):
        output = tmp_path / "merged.pdf"
        callback = MagicMock()
        merge_pdfs([str(sample_pdf)], str(output), progress_callback=callback)
        callback.assert_called()

    def test_split_pdf_single_pages(self, multi_pdf, tmp_path):
        results = split_pdf(str(multi_pdf), str(tmp_path), pages_per_file=1)
        assert len(results) == 3

    def test_split_pdf_ranges(self, multi_pdf, tmp_path):
        results = split_pdf(str(multi_pdf), str(tmp_path), ranges=[(0, 1)])
        assert len(results) >= 1

    def test_split_empty_ranges(self, sample_pdf, tmp_path):
        results = split_pdf(str(sample_pdf), str(tmp_path), ranges=[(5, 10)])
        assert len(results) == 0

    def test_metadata_with_custom_fields(self, sample_pdf):
        meta = get_metadata(str(sample_pdf))
        assert "title" in meta
        assert "author" in meta
        assert "pages" in meta

    def test_page_count_multi_page(self, multi_pdf):
        assert get_page_count(str(multi_pdf)) == 3

    def test_merge_single_pdf(self, sample_pdf, tmp_path):
        output = tmp_path / "merged.pdf"
        result = merge_pdfs([str(sample_pdf)], str(output))
        assert Path(result).exists()


class TestCompressPdf:
    def test_compress_medium(self, sample_pdf, tmp_path):
        output = tmp_path / "compressed.pdf"
        result = compress_pdf(str(sample_pdf), str(output), quality="medium")
        assert result["success"] is True
        assert Path(output).exists()
        assert result["original_size"] > 0
        assert result["compressed_size"] > 0

    def test_compress_low(self, sample_pdf, tmp_path):
        output = tmp_path / "compressed_low.pdf"
        result = compress_pdf(str(sample_pdf), str(output), quality="low")
        assert result["success"] is True
        assert result["ratio"] >= 0

    def test_compress_high(self, sample_pdf, tmp_path):
        output = tmp_path / "compressed_high.pdf"
        result = compress_pdf(str(sample_pdf), str(output), quality="high")
        assert result["success"] is True

    def test_compress_invalid_quality_falls_back(self, sample_pdf, tmp_path):
        output = tmp_path / "compressed_fallback.pdf"
        result = compress_pdf(str(sample_pdf), str(output), quality="invalid")
        assert result["success"] is True


class TestSanitizePdf:
    def test_sanitize_basic(self, sample_pdf, tmp_path):
        output = tmp_path / "sanitized.pdf"
        result = sanitize_pdf(str(sample_pdf), str(output))
        assert result["success"] is True
        assert Path(output).exists()
        assert result["original_size"] > 0

    def test_sanitize_remove_metadata(self, sample_pdf, tmp_path):
        output = tmp_path / "sanitized_meta.pdf"
        result = sanitize_pdf(str(sample_pdf), str(output), remove_metadata=True)
        assert result["success"] is True
        assert result["items_removed"] >= 1

    def test_sanitize_no_forms(self, sample_pdf, tmp_path):
        output = tmp_path / "sanitized_noforms.pdf"
        result = sanitize_pdf(str(sample_pdf), str(output), remove_forms=False)
        assert result["success"] is True


class TestDecryptPdf:
    def test_decrypt_non_encrypted(self, sample_pdf, tmp_path):
        output = tmp_path / "decrypted.pdf"
        result = decrypt_pdf(str(sample_pdf), str(output), password="any")
        assert result["success"] is True
        assert result["was_encrypted"] is False

    def test_decrypt_wrong_password(self, sample_pdf, tmp_path):
        doc = fitz.open()
        doc.new_page()
        encrypted_path = tmp_path / "encrypted.pdf"
        doc.save(str(encrypted_path), encryption=fitz.PDF_ENCRYPT_AES_128,
                 user_pw="secret", owner_pw="secret")
        doc.close()
        output = tmp_path / "decrypted.pdf"
        result = decrypt_pdf(str(encrypted_path), str(output), password="wrong")
        assert result["success"] is False
        assert result["was_encrypted"] is True

    def test_decrypt_correct_password(self, sample_pdf, tmp_path):
        doc = fitz.open(str(sample_pdf))
        encrypted_path = tmp_path / "encrypted.pdf"
        doc.save(str(encrypted_path), encryption=fitz.PDF_ENCRYPT_AES_128,
                 user_pw="secret", owner_pw="secret")
        doc.close()
        output = tmp_path / "decrypted.pdf"
        result = decrypt_pdf(str(encrypted_path), str(output), password="secret")
        assert result["success"] is True
        assert result["was_encrypted"] is True
        assert result["pages"] == 1


class TestGetPdfInfo:
    def test_info_basic(self, sample_pdf):
        info = get_pdf_info(str(sample_pdf))
        assert info["pages"] == 1
        assert info["encrypted"] is False
        assert info["size_bytes"] > 0
        assert info["size_mb"] >= 0

    def test_info_multi_page(self, multi_pdf):
        info = get_pdf_info(str(multi_pdf))
        assert info["pages"] == 3
