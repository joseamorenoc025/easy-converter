# Easy Converter

Conversor de escritorio bidireccional entre **PDF** y **Word (DOCX)** con flujo de trabajo automatizado.

## Caracteristicas

- **Conversion PDF a Word y Word a PDF** — mantiene tablas, imagenes y formato
- **OCR con Tesseract** — extrae texto de PDFs escaneados (opcional)
- **Combinar, dividir, comprimir y cifrar PDFs** — merge, split, compresion y proteccion con contrasena
- **Sanitizacion de PDFs** — elimina scripts JavaScript, formularios y metadatos peligrosos
- **Flujos de trabajo inteligentes** — perfiles con reglas de renombrado, mover, copiar
- **Carpetas monitorizadas** — conversion automatica al copiar archivos a una carpeta
- **Interfaz moderna** — customtkinter con drag & drop, temas personalizables
- **Notificaciones nativas** — alertas de Windows al completar conversiones
- **Instalador con Tesseract** — Inno Setup incluye OCR como componente opcional
- **Modo portable** — ejecutable unico funciona desde USB sin instalacion

## Requisitos

- **Windows 10/11**
- **Python 3.9+** (solo para ejecutar desde codigo fuente)
- **Microsoft Word** (obligatorio para Word a PDF)
- **Tesseract OCR** (opcional, para PDFs escaneados — se incluye en el instalador)

## Instalacion

### Opcion 1: Instalador (Usuario Final)

1. Descarga `EasyConverter-Installer-2.2.0.exe` desde [Releases](https://github.com/joseamorenoc025/easy-converter/releases/tag/v2.2.0)
2. Ejecuta el instalador
3. Marca "Instalar Tesseract OCR" si trabajas con PDFs escaneados
4. Marca "Agregar al menu contextual" para acceso rapido desde el explorador

### Opcion 2: Portable (USB / Sin Instalar)

1. Descarga `Easy Converter Portable.exe` desde [Releases](https://github.com/joseamorenoc025/easy-converter/releases/tag/v2.2.0)
2. Copia el `.exe` a tu USB o carpeta preferida
3. Ejecuta directamente — la configuracion se guarda junto al executable

### Opcion 3: Codigo Fuente (Desarrolladores)

```bash
git clone https://github.com/joseamorenoc025/easy-converter.git
cd easy-converter
pip install -r requirements.txt
python src/main.py
```

## Uso

### Conversion Basica
1. Arrastra un archivo PDF o DOCX a la ventana
2. Selecciona la direccion de conversion (PDF a Word o Word a PDF)
3. Haz clic en "Iniciar Conversion"

### OCR (PDFs Escaneados)
1. Marca la casilla "OCR" en el panel lateral
2. Selecciona el idioma del documento
3. Arrastra el PDF escaneado y conviertelo — el texto se extraera automaticamente

### Combinar PDFs
1. Ve a la pestana "Herramientas"
2. Selecciona "Combinar" y agrega los archivos PDF
3. Elige la ruta de salida y ejecuta

### Dividir PDFs
1. Ve a la pestana "Herramientas"
2. Selecciona "Dividir" y configura paginas por archivo o rangos
3. Ejecuta — se generan los archivos separados

### Cifrar PDF
1. Ve a la pestana "Herramientas"
2. Selecciona "Cifrar" y carga el PDF
3. Configura contrasena, nivel de cifrado (AES-256/128) y permisos
4. Ejecuta — el PDF queda protegido

### Sanitizar PDF
1. Ve a la pestana "Herramientas"
2. Selecciona "Sanitizar" y carga el PDF
3. Marca las opciones (scripts, formularios, metadatos)
4. Ejecuta — se elimina el contenido peligroso

### Flujos de Trabajo
1. Ve a la pestana "Flujos"
2. Crea un perfil y selecciona una carpeta para monitorear
3. Activa "Monitorear" — cualquier archivo compatible se convertira automaticamente

## Estructura del Proyecto

```
src/
  main.py              — Punto de entrada, single instance lock
  core/
    controller.py      — AppController con inyeccion de dependencias
    interfaces.py      — Contratos abstractos (IConverter, IQueueManager, etc.)
    converter.py       — Motor de conversion PDF/Word
    converter_adapter.py — Adaptador IConverter -> EasyConverter
    queue_manager.py   — Cola de procesamiento con Worker
    queue_adapter.py   — Adaptador IQueueManager -> ConversionQueue
    workflow.py        — Perfiles y reglas de post-procesamiento
    workflow_adapter.py — Adaptador IWorkflowEngine -> WorkflowManager
    file_manager.py    — Resolucion de rutas de salida
    error_handler.py   — Manejo de errores con logging
    watcher.py         — Monitoreo de carpetas con watchdog
    progress.py        — Barra de progreso
  ui/
    main_window.py     — Ventana principal con customtkinter
    components.py      — Componentes UI reutilizables
    themes.py          — Temas oscuro/claro/alto contraste + personalizables
    notifications.py   — Notificaciones nativas de Windows
    workflow_panel.py  — Panel de flujos de trabajo
    pdf_operations.py  — Panel de operaciones PDF (merge/split/cifrar/sanitizar)
  utils/
    config.py          — Persistencia de configuracion (portable + appdirs)
    security.py        — Validacion de rutas y magic numbers
    platform_service.py — Servicios de plataforma Windows
    pdf_tools.py       — Metadatos, merge, split, cifrar, sanitizar PDFs
    word_checker.py    — Deteccion de Microsoft Word
    context_menu.py    — Registro de menu contextual de Windows
build/
  easy_converter.spec  — Configuracion PyInstaller (onefile)
  setup.iss            — Script Inno Setup para instalador
  build.ps1            — Script de automatizacion de build
  cert.pfx             — Certificado autofirmado para firma de codigo
tests/                 — 183 tests unitarios y de integracion
```

## Ejecutar Tests

```bash
pytest tests/ -v --cov=src
```

## Build

```powershell
# Generar ejecutable + instalador
.\build\build.ps1

# Solo ejecutable (sin instalador)
.\build\build.ps1 -SkipInstaller

# Sin firma de codigo
.\build\build.ps1 -SkipSign
```

## Licencia

MIT License — ver [LICENSE](LICENSE) para detalles.

---
*Desarrollado por joseamorenoc025*
