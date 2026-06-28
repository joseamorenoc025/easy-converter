"""Tests para pdf_tools."""
import pytest
import fitz
from pathlib import Path
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from utils.pdf_tools import get_metadata, get_page_count, merge_pdfs, split_pdf


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
