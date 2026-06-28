# Easy Converter v2.1.0

**Fecha:** Junio 2026
**Tipo:** Release con fixes de tests y modo portable

---

## Cambios en v2.1.0

### Correcciones de Tests (137/137 passing)
- Fix: ConfigManager fixture con thread lock para tests
- Fix: PyMuPDF API actualizado (page.rect.width en vez de page_width)
- Fix: single instance tests con aislamiento de modulos
- Fix: error handler context logging verificado en archivo de log
- Fix: PathManager test con directorio custom real
- Fix: UI test resilient a errores de Tcl

### Modo Portable
- ConfigManager guarda config junto al `.exe` cuando se ejecuta desde ubicacion no estandar (USB, Downloads, etc.)
- ErrorHandler guarda logs junto al `.exe` en modo portable
- Sin necesidad de marker file — se detecta automaticamente

### Documentacion
- README.md actualizado con Python 3.9+, todas las features, estructura completa
- QUICK_START.md actualizado con instrucciones de modo portable
- URLs corregidas al repositorio real

### Build y CI/CD
- Inno Setup 6 integrado en pipeline de build
- Version bump a 2.1.0 en spec, setup.iss, release_info.json
- Test dependencies agregadas a requirements.txt (pytest, pytest-cov, pytest-mock)

---

## Descarga

### Instalador
`EasyConverter-Setup-2.1.0.exe` — Incluye Tesseract OCR como componente opcional

### Portable
`EasyConverter.exe` — Ejecutable unico, funciona desde USB sin instalacion

---

## Requisitos
- Windows 10/11
- Microsoft Word (para conversion Word a PDF)
- Tesseract OCR (opcional, para PDFs escaneados)

---

## Creditos
Desarrollado por joseamorenoc025
