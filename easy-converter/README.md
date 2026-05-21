# Easy Converter 📄↔️📝

Un conversor de escritorio bidireccional entre **PDF** y **Word (DOCX)**, diseñado para ser ligero, moderno y fácil de usar.

## ✨ Características
- **Conversión de Alta Calidad:** Utiliza análisis de layout avanzado para mantener tablas, imágenes y párrafos.
- **Interfaz Moderna:** Basada en `customtkinter` para un look profesional.
- **Arrastrar y Soltar:** Soporte nativo para `Drag & Drop`.
- **Detección Automática:** Cambia el modo de conversión según el archivo que arrastres.
- **Procesamiento en Segundo Plano:** No bloquea la interfaz durante conversiones pesadas.

## 🛠️ Requisitos
- **Python 3.10** o superior.
- **Microsoft Word** instalado (obligatorio para la conversión de Word a PDF en Windows).

## 🚀 Instalación

1. Clona o descarga este repositorio.
2. Abre una terminal en la carpeta del proyecto.
3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Uso

Simplemente ejecuta el script principal:
```bash
python app.py
```

### Instrucciones:
1. Selecciona el modo: **PDF a Word** o **Word a PDF**.
2. Arrastra tu archivo a la zona central o usa el diálogo de selección.
3. Haz clic en **CONVERTIR AHORA**.
4. Al finalizar, podrás abrir la carpeta donde se guardó el resultado (mismo directorio que el original).

## 📦 Bibliotecas Principales
- [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx): Conversión de PDF a DOCX.
- [docx2pdf](https://github.com/AlJohri/docx2pdf): Conversión de DOCX a PDF.
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter): Interfaz gráfica moderna.
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2): Soporte de Drag & Drop.

---
*Desarrollado con ❤️ por Gemini CLI*
