# Easy Converter 📄↔️📝

Un conversor de escritorio inteligente y bidireccional entre **PDF** y **Word (DOCX)**. Ahora no solo convierte archivos, sino que gestiona tu flujo de trabajo de forma automatizada.

## ✨ Características
- **Conversión de Alta Calidad:** Mantiene tablas, imágenes y párrafos con precisión.
- **Flujos de Trabajo Inteligentes (¡NUEVO!):** Define perfiles con reglas de post-procesamiento.
- **Carpetas Inteligentes (¡NUEVO!):** Monitoreo automático de carpetas para conversión desatendida.
- **Reglas Automatizadas:** Renombrado automático (con fechas/patrones), mover o copiar archivos tras la conversión.
- **Interfaz Moderna:** Pestañas separadas para control manual y gestión de flujos (basada en `customtkinter`).
- **Arrastrar y Soltar:** Soporte nativo para `Drag & Drop`.
- **Procesamiento en Segundo Plano:** Multihilo para no bloquear la interfaz.

## 🛠️ Requisitos
- **Python 3.10** o superior.
- **Microsoft Word** instalado (obligatorio para Word a PDF en Windows).

## 🚀 Instalación

1. Clona el repositorio.
2. Abre una terminal en la carpeta del proyecto.
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Uso

Ejecuta el script principal:
```bash
python src/main.py
```

### Gestión de Flujos:
1. Ve a la pestaña **"Flujos de Trabajo"**.
2. Crea un **"Nuevo Perfil"** y elige una carpeta para monitorear.
3. Activa el interruptor **"Monitorear"**.
4. ¡Cualquier archivo compatible que copies a esa carpeta se convertirá y procesará automáticamente!

## 📦 Bibliotecas Principales
- [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx): PDF a DOCX.
- [docx2pdf](https://github.com/AlJohri/docx2pdf): DOCX a PDF.
- [watchdog](https://github.com/gorakhargosh/watchdog): Monitoreo de carpetas en tiempo real.
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter): Interfaz gráfica.

---
*Desarrollado con ❤️ por Gemini CLI*
