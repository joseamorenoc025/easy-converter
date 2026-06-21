"""
Tests para el módulo de seguridad.
Valida rutas, magic numbers y sanitización de nombres de archivo.
"""
import pytest
from pathlib import Path
import tempfile
import os

# Importar funciones a testear
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from utils.security import is_safe_path, validate_file_magic, sanitize_filename, get_user_local_paths


class TestIsSafePath:
    """Tests para validación de rutas seguras."""
    
    def test_home_directory_is_safe(self):
        """El directorio home del usuario debe ser seguro."""
        home = Path.home()
        test_file = home / "test_file.pdf"
        assert is_safe_path(test_file) is True
    
    def test_subdirectory_of_home_is_safe(self):
        """Subdirectorios del home deben ser seguros."""
        home = Path.home()
        test_file = home / "Documents" / "subdir" / "file.docx"
        # Crear path aunque no exista el archivo
        assert is_safe_path(str(test_file)) is True
    
    def test_absolute_path_required(self):
        """Rutas relativas deben ser rechazadas."""
        assert is_safe_path("relative/path/file.pdf") is False
        assert is_safe_path("./file.pdf") is False
    
    def test_nonexistent_path_still_validated(self):
        """La validación debe funcionar incluso si el path no existe."""
        # Paths absolutos dentro de home deberían pasar la validación de ruta
        # aunque el archivo no exista
        home = Path.home()
        fake_file = home / "nonexistent_folder" / "fake.pdf"
        # is_safe_path solo verifica que esté dentro de allowed_bases
        assert is_safe_path(fake_file) is True


class TestValidateFileMagic:
    """Tests para validación de magic numbers."""
    
    def test_valid_pdf_magic(self):
        """PDF válido debe pasar validación."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4 test content')
            temp_path = f.name
        
        try:
            is_valid, msg = validate_file_magic(temp_path, 'pdf')
            assert is_valid is True
            assert "válido" in msg.lower()
        finally:
            os.unlink(temp_path)
    
    def test_valid_docx_magic(self):
        """DOCX válido (ZIP) debe pasar validación."""
        # DOCX es un ZIP, empieza con PK\x03\x04
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            f.write(b'PK\x03\x04test zip content')
            temp_path = f.name
        
        try:
            is_valid, msg = validate_file_magic(temp_path, 'docx')
            assert is_valid is True
        finally:
            os.unlink(temp_path)
    
    def test_invalid_pdf_magic(self):
        """Archivo con extensión PDF pero contenido inválido debe fallar."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'This is not a PDF file at all')
            temp_path = f.name
        
        try:
            is_valid, msg = validate_file_magic(temp_path, 'pdf')
            assert is_valid is False
            assert "no parece" in msg.lower() or "inválido" in msg.lower()
        finally:
            os.unlink(temp_path)
    
    def test_nonexistent_file(self):
        """Archivo que no existe debe fallar."""
        is_valid, msg = validate_file_magic('/nonexistent/path/file.pdf', 'pdf')
        assert is_valid is False
        assert "no existe" in msg.lower()
    
    def test_directory_instead_of_file(self):
        """Directorio en lugar de archivo debe fallar."""
        is_valid, msg = validate_file_magic(tempfile.gettempdir(), 'pdf')
        assert is_valid is False
        assert "archivo" in msg.lower()


class TestSanitizeFilename:
    """Tests para sanitización de nombres de archivo."""
    
    def test_remove_invalid_chars_windows(self):
        """Caracteres inválidos de Windows deben ser removidos."""
        dirty = 'my<file>:name?.txt'
        clean = sanitize_filename(dirty)
        assert '<' not in clean
        assert '>' not in clean
        assert ':' not in clean
        assert '?' not in clean
        assert '*' not in clean
    
    def test_remove_invalid_chars_linux(self):
        """Caracteres especiales deben ser sanitizados."""
        dirty = 'file/name\\with|pipes.txt'
        clean = sanitize_filename(dirty)
        assert '/' not in clean
        assert '\\' not in clean
        assert '|' not in clean
    
    def test_trim_spaces_and_dots(self):
        """Espacios y puntos al inicio/final deben ser removidos."""
        assert sanitize_filename('  filename  ') == 'filename'
        assert sanitize_filename('...hidden_file') == 'hidden_file'
    
    def test_empty_result_gets_default(self):
        """Nombre vacío después de sanitizar debe tener default."""
        assert sanitize_filename('<>:?*') == 'archivo_sin_nombre'
        assert sanitize_filename('...') == 'archivo_sin_nombre'
    
    def test_clean_name_unchanged(self):
        """Nombre limpio debe permanecer igual."""
        assert sanitize_filename('clean_filename.pdf') == 'clean_filename.pdf'


class TestGetUserLocalPaths:
    """Tests para obtención de rutas locales del usuario."""
    
    def test_returns_list(self):
        """Debe retornar una lista."""
        paths = get_user_local_paths()
        assert isinstance(paths, list)
    
    def test_contains_home(self):
        """La lista debe contener al menos el home directory."""
        paths = get_user_local_paths()
        home = Path.home().resolve()
        assert any(p == home for p in paths)
    
    def test_all_paths_are_absolute(self):
        """Todas las rutas deben ser absolutas."""
        paths = get_user_local_paths()
        assert all(p.is_absolute() for p in paths)
