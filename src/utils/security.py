"""
Módulo de seguridad para validación de rutas y tipos de archivo.
Garantiza que las operaciones se realicen solo en entornos locales seguros
y que los archivos correspondan a sus extensiones declaradas.
"""
import os
import sys
import pathlib
from typing import Tuple, Optional, Union
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
                # Preferir ctypes.SHGetKnownFolderPath para rutas redirigidas
                from ctypes import windll, create_unicode_buffer, byref, wintypes
                FOLDERID_Documents = "FDD39AD0-238F-46AF-ADB4-6C85480369C7"
                FOLDERID_Desktop = "B4BFCC3A-DB2C-424C-B029-7FE99A87C641"
                FOLDERID_Downloads = "374DE290-123F-4565-9164-39C4925E467B"
                for fid in (FOLDERID_Documents, FOLDERID_Desktop, FOLDERID_Downloads):
                    buf = create_unicode_buffer(wintypes.MAX_PATH)
                    if windll.shell32.SHGetKnownFolderPath(create_unicode_buffer(fid), 0, None, byref(buf)) == 0:
                        paths.append(pathlib.Path(buf.value).resolve())
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

def is_safe_path(file_path: Union[str, pathlib.Path], allowed_bases: Optional[list[pathlib.Path]] = None) -> bool:
    """
    Valida que una ruta esté dentro de los directorios permitidos del usuario.
    Previene Path Traversal y acceso a unidades de red o sistema.
    
    Args:
        file_path: Ruta del archivo a validar.
        allowed_bases: Lista de rutas base permitidas. Si es None, usa las por defecto.
        
    Returns:
        True si la ruta es segura, False en caso contrario.
    """
    try:
        path_obj = pathlib.Path(file_path).resolve()
        
        # Verificar si es una ruta absoluta
        if not path_obj.is_absolute():
            logger.warning(f"Ruta relativa detectada y rechazada: {file_path}")
            return False
            
        # Determinar bases permitidas
        if allowed_bases is None:
            allowed_bases = get_user_local_paths()
            
        # Verificar que la ruta resuelta comience con alguna de las bases permitidas
        for base in allowed_bases:
            try:
                # Verifica si path_obj es subpath de base
                path_obj.relative_to(base)
                return True
            except ValueError:
                continue
                
        logger.warning(f"Ruta fuera del entorno local permitido: {path_obj}")
        return False
        
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
        sanitized = sanitized.replace(char, '_')
        
    # Eliminar espacios al inicio/final y puntos al inicio (archivos ocultos en Linux)
    sanitized = sanitized.strip().lstrip('.')
    
    if not sanitized:
        sanitized = "archivo_sin_nombre"
        
    return sanitized
