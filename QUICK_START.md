# 🚀 Inicio Rápido - Easy Converter v2.0.0

## Opción 1: Probar desde Código Fuente (Recomendado para Desarrollo)

### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Windows 10/11 (recomendado, algunas funciones son específicas de Windows)

### Pasos de Instalación

```bash
# 1. Clonar el repositorio (si aún no lo has hecho)
git clone https://github.com/TU_USUARIO/easy-converter.git
cd easy-converter

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
# source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar la aplicación
python src/main.py
```

### Verificar que Todo Funciona

```bash
# Ejecutar tests
pytest tests/ -v

# Ver cobertura
pytest tests/ --cov=src --cov-report=term-missing

# Linting
flake8 src/ tests/

# Type checking
mypy src/ --ignore-missing-imports
```

---

## Opción 2: Usar el Instalador (Usuario Final)

### Descarga
1. Ve a [Releases](https://github.com/TU_USUARIO/easy-converter/releases)
2. Descarga `EasyConverter-Setup-2.0.0.exe`

### Instalación
1. Ejecuta el instalador
2. Sigue el asistente
3. ✅ Marca "Instalar Tesseract OCR" si trabajas con PDFs escaneados
4. ✅ Marca "Agregar al menú contextual" para acceso rápido
5. Finaliza la instalación

### Primer Uso
1. La aplicación se iniciará automáticamente
2. Completa el asistente de bienvenida
3. ¡Listo para convertir!

---

## 🧪 Pruebas Rápidas Post-Instalación

### Test 1: Conversión Básica
1. Arrastra un archivo PDF a la ventana
2. Selecciona "Convertir a Word"
3. Click en "Iniciar Conversión"
4. Verifica que el archivo .docx se crea correctamente

### Test 2: Cambio de Idioma
1. Ve a Preferencias ⚙️
2. Cambia el idioma a Inglés
3. Reinicia la aplicación
4. Verifica que todos los textos están en inglés

### Test 3: Historial
1. Realiza una conversión
2. Ve a la pestaña "Historial"
3. Verifica que la conversión aparece listada

### Test 4: Deshacer
1. Convierte un archivo
2. Presiona `Ctrl+Z`
3. Verifica que la operación se revierte

---

## 🐛 Solución de Problemas Comunes

### Error: "No module named 'customtkinter'"
```bash
# Solución: Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error: "Word no está instalado"
- La aplicación requiere Microsoft Word para conversión DOCX
- Si no tienes Word, solo podrás convertir PDF → Word (no al revés)
- Considera instalar LibreOffice como alternativa (requiere configuración adicional)

### Error: "Tesseract no encontrado"
- Descarga e instala Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- Añade la ruta de Tesseract a las variables de entorno PATH
- O reinstala usando el instalador y marca la opción de Tesseract

### Error: "Permission denied" en registro de Windows
- Ejecuta la aplicación como Administrador
- O desmarca la opción "Agregar al menú contextual" en Preferencias

---

## 📚 Siguientes Pasos

- Lee la [Guía de Usuario](docs/USER_GUIDE.md) para funcionalidades avanzadas
- Consulta la [Arquitectura](docs/ARCHITECTURE.md) si eres desarrollador
- Reporta bugs en [Issues](https://github.com/TU_USUARIO/easy-converter/issues)

---

**¡Disfruta convirtiendo!** 🎉
