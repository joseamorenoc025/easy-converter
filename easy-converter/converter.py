import os
from pdf2docx import Converter
from docx2pdf import convert as word_to_pdf_conv

class EasyConverter:
    @staticmethod
    def pdf_to_docx(pdf_path, callback=None):
        """
        Convierte un archivo PDF a DOCX manteniendo el layout.
        """
        try:
            docx_path = pdf_path.rsplit('.', 1)[0] + '.docx'
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()
            if callback:
                callback(True, docx_path)
            return True, docx_path
        except Exception as e:
            if callback:
                callback(False, str(e))
            return False, str(e)

    @staticmethod
    def docx_to_pdf(docx_path, callback=None):
        """
        Convierte un archivo DOCX a PDF usando docx2pdf.
        """
        try:
            pdf_path = docx_path.rsplit('.', 1)[0] + '.pdf'
            # En Windows requiere tener Microsoft Word instalado
            word_to_pdf_conv(docx_path, pdf_path)
            if callback:
                callback(True, pdf_path)
            return True, pdf_path
        except Exception as e:
            if callback:
                callback(False, str(e))
            return False, str(e)
