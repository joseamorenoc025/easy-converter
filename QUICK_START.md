# Inicio Rapido - Easy Converter v2.1.0

## Opcion 1: Instalador (Recomendado para Usuarios Finales)

### Descarga
1. Ve a [Releases](https://github.com/joseamorenoc025/easy-converter/releases/tag/v2.1.0)
2. Descarga `EasyConverter-Setup-2.1.0.exe`

### Instalacion
1. Ejecuta el instalador
2. Sigue el asistente
3. Marca "Instalar Tesseract OCR" si trabajas con PDFs escaneados
4. Marca "Agregar al menu contextual" para acceso rapido
5. Finaliza la instalacion — la app se iniciara automaticamente

---

## Opcion 2: Portable (USB / Sin Instalar)

### Descarga
1. Ve a [Releases](https://github.com/joseamorenoc025/easy-converter/releases/tag/v2.1.0)
2. Descarga `EasyConverter.exe`
3. Copia el `.exe` a tu USB o carpeta preferida
4. Ejecuta directamente — no requiere instalacion

### Nota sobre Portabilidad
- La configuracion se guarda junto al `.exe` automaticamente
- Funciona en cualquier PC con Windows 10/11
- Microsoft Word debe estar instalado para conversion Word a PDF
- Tesseract OCR debe estar instalado separadamente si necesitas OCR

---

## Opcion 3: Codigo Fuente (Desarrolladores)

### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Windows 10/11

### Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/joseamorenoc025/easy-converter.git
cd easy-converter

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicacion
python src/main.py
```

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Build del Ejecutable

```powershell
# Generar ejecutable + instalador
.\build\build.ps1

# Solo ejecutable
.\build\build.ps1 -SkipInstaller
```

---

## Pruebas Rapidas Post-Instalacion

### Test 1: Conversion Basica
1. Arrastra un archivo PDF a la ventana
2. Selecciona "Convertir a Word"
3. Click en "Iniciar Conversion"
4. Verifica que el archivo .docx se crea correctamente

### Test 2: OCR
1. Marca la casilla "OCR" en el panel lateral
2. Arrastra un PDF escaneado
3. Convierte — el texto de las imagenes se extraera

### Test 3: Combinar PDFs
1. Ve a "Herramientas PDF"
2. Selecciona "Combinar"
3. Agrega multiples PDFs
4. Ejecuta — se genera un solo archivo

---

## Solucion de Problemas

### "No module named 'customtkinter'"
```bash
pip install -r requirements.txt --force-reinstall
```

### "Word no esta instalado"
- La aplicacion requiere Microsoft Word para conversion DOCX a PDF
- Sin Word, solo podras convertir PDF a Word

### "Tesseract no encontrado"
- Descarga Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- O reinstala con el instalador y marca la opcion de Tesseract

### La app no inicia
- Verifica que Python 3.9+ este instalado: `python --version`
- Reinstala dependencias: `pip install -r requirements.txt`
