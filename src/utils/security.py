"""
Módulo de seguridad para validación de rutas y tipos de archivo.
Garantiza que las operaciones se realicen solo en entornos locales seguros
y que los archivos correspondan a sus extensiones declaradas.
"""
import os
import sys
import pathlib
from typing import Tuple, Union
import logging

logger = logging.getLogger(__name__)

# Magic numbers comunes para validación de archivos
FILE_SIGNATURES = {
    'pdf': b'%PDF-',
    'docx': b'PK\x03\x04',  # DOCX es un ZIP XML, empieza con PK
    'zip': b'PK\x03\x04',
}

def get_user_local_paths() -> list[pathlib.Path]:
    """
    Obtiene las rutas base permitidas (Entorno local del usuario).
    Incluye: Directorio de usuario, Directorio de datos de la app.
    """
    paths = []
    try:
        # Directorio home del usuario
        home = pathlib.Path.home().resolve()
        paths.append(home)
        
        # Directorio de datos de la aplicación (appdirs)
        # Importamos aquí para evitar circular imports si appdirs falla
        try:
            import appdirs
            app_data = pathlib.Path(appdirs.user_data_dir("EasyConverter")).resolve()
            paths.append(app_data)
            
            app_cache = pathlib.Path(appdirs.user_cache_dir("EasyConverter")).resolve()
            paths.append(app_cache)
        except ImportError:
            logger.warning("appdirs no disponible, usando solo home directory")
            
        # Directorio actual de trabajo
        paths.append(pathlib.Path.cwd().resolve())

        # Carpetas comunes de usuario en Windows (Documentos, Escritorio, Descargas)
        if sys.platform == "win32":
            try:
                from ctypes import windll, byref, wintypes
                from uuid import UUID
                # KNOWNFOLDERID como estructura GUID
                class _GUID(wintypes.Structure):  # type: ignore[name-defined]
                    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                                ("Data3", wintypes.WORD), ("Data4", wintypes.BYTE * 8)]
                known_folders = {
                    "FDD39AD0-238F-46AF-ADB4-6C85480369C7",  # Documents
                    "B4BFCC3A-DB2C-424C-B029-7FE99A87C641",  # Desktop
                    "374DE290-123F-4565-9164-39C4925E467B",  # Downloads
                }
                for fid_str in known_folders:
                    u = UUID(fid_str)
                    guid = _GUID(u.time_low, u.time_mid, u.time_hi_version,
                                 (wintypes.BYTE * 8)(*u.bytes[8:]))
                    p_path = wintypes.LPWSTR()
                    if windll.shell32.SHGetKnownFolderPath(byref(guid), 0, None, byref(p_path)) == 0:
                        paths.append(pathlib.Path(p_path.value).resolve())
                        windll.ole32.CoTaskMemFree(p_path)
            except Exception:
                # Fallback: rutas estándar bajo %USERPROFILE%
                fallbacks = ["Documents", "Desktop", "Downloads"]
                for folder in fallbacks:
                    p = pathlib.Path(os.environ.get("USERPROFILE", "")) / folder
                    if p.exists():
                        paths.append(p.resolve())

    except Exception as e:
        logger.error(f"Error obteniendo rutas locales: {e}")
        # Fallback seguro: solo el directorio actual si todo falla (muy restrictivo)
        paths.append(pathlib.Path.cwd().resolve())
        
    return paths

def is_safe_path(file_path: Union[str, pathlib.Path]) -> bool:
    """
    Valida que una ruta sea segura para operar.
    Rechaza rutas relativas (path traversal) y rutas de red UNC.
    Cualquier ruta absoluta local es aceptada.
    """
    try:
        original_path = pathlib.Path(file_path)
        # Rechazar rutas relativas (path traversal)
        if not original_path.is_absolute():
            logger.warning(f"Ruta relativa detectada y rechazada: {file_path}")
            return False
        # Rechazar rutas de red UNC (\\server\share)
        if str(original_path).startswith("\\\\"):
            logger.warning(f"Ruta de red UNC rechazada: {file_path}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error validando ruta {file_path}: {e}")
        return False

def validate_file_magic(file_path: Union[str, pathlib.Path], expected_extension: str) -> Tuple[bool, str]:
    """
    Valida que el contenido real del archivo coincida con su extensión.
    
    Args:
        file_path: Ruta del archivo.
        expected_extension: Extensión esperada (ej: 'pdf', 'docx').
        
    Returns:
        Tuple[bool, str]: (Es válido, Mensaje de error o éxito)
    """
    path_obj = pathlib.Path(file_path)
    
    if not path_obj.exists():
        return False, "El archivo no existe"
    
    if not path_obj.is_file():
        return False, "La ruta no apunta a un archivo válido"
        
    try:
        with open(path_obj, 'rb') as f:
            header = f.read(8)  # Leer primeros 8 bytes
            
        expected_sig = FILE_SIGNATURES.get(expected_extension.lower())
        
        if not expected_sig:
            logger.warning(f"No hay firma definida para extensión {expected_extension}, saltando validación de magia.")
            return True, "Validación omitida (firma desconocida)"
            
        if header.startswith(expected_sig):
            return True, "Archivo válido"
        else:
            # Caso especial: DOCX a veces tiene ligeras variaciones, pero PK es estándar
            logger.warning(f"Firma inválida para {expected_extension}. Esperado: {expected_sig!r}, Obtenido: {header[:5]!r}")
            return False, f"El archivo no parece ser un {expected_extension.upper()} válido (corrupto o tipo incorrecto)"
            
    except PermissionError:
        return False, "Permiso denegado para leer el archivo"
    except Exception as e:
        logger.error(f"Error leyendo cabecera de {file_path}: {e}")
        return False, f"Error al validar el archivo: {str(e)}"

def sanitize_filename(filename: str) -> str:
    """
    Elimina caracteres peligrosos o inválidos de un nombre de archivo.
    Útil para prevenir errores en renombrado o inyección de rutas.
    """
    # Caracteres prohibidos en Windows y Linux
    invalid_chars = '<>:"/\\|?*'
    
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '')
        
    # Eliminar espacios al inicio/final y puntos al inicio (archivos ocultos en Linux)
    sanitized = sanitized.strip().lstrip('.')
    
    if not sanitized:
        sanitized = "archivo_sin_nombre"
        
    return sanitized
