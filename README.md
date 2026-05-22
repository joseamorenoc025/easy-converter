# Easy Converter 📄↔️📝

**Easy Converter** es una potente herramienta de escritorio diseñada para convertir documentos bidireccionalmente entre **PDF** y **Word (DOCX/DOC)** sin perder calidad, estructura, ni formatos. Con una interfaz moderna (Cyber/Neon) y automatización profunda de carpetas, tu trabajo pesado se hace en segundos.

## ✨ Características Principales
- **Conversión de Alta Fidelidad:** Mantiene intactas las tablas, imágenes y la estructura de los párrafos.
- **Carpetas Automáticas (Workflow):** Configura una carpeta y la aplicación convertirá instantáneamente cualquier archivo que dejes ahí, sin que tengas que hacer clics.
- **Soporte Universal Word:** Compatible con `.docx` modernos y `.doc` antiguos gracias al fallback inteligente de motor COM.
- **Integración con Windows:** Haz clic derecho en cualquier archivo de tu sistema operativo para convertirlo mediante el menú contextual automático.
- **Dashboard en Tiempo Real:** Estadísticas de los documentos convertidos e indicadores de carga procesada visualmente.
- **100% Multihilo:** Procesamiento veloz en segundo plano sin que la aplicación se "cuelgue".

## 🛠️ Requisitos del Sistema
- Sistema Operativo: Windows 10/11.
- Microsoft Word (Obligatorio instalado en el sistema para permitir la inter-operatividad de COM).

## 🚀 Instalación y Uso Rápido
### Opción 1: Versión Portable (.exe)
Visita la sección de [Releases](../../releases) y descarga la última versión en `.zip`. Descomprime y ejecuta `EasyConverter.exe`. ¡No necesitas instalar nada más!

### Opción 2: Para Desarrolladores (Código Fuente)
1. Clona el repositorio.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la aplicación:
   ```bash
   python src/main.py
   ```

## 📚 ¿Cómo funcionan las Carpetas Automáticas?
1. Ve a la pestaña **"Carpetas Automáticas"**.
2. Crea un **"Nuevo Perfil"**, elige qué carpeta vigilar (Ej. `Descargas`).
3. Activa el interruptor **"Monitorear"**.
4. ¡Listo! Cualquier PDF o Word que caiga ahí, se procesará automáticamente y se guardará según tus reglas (como renombrar o mover a la nube).

---
⭐ Si este software te ha salvado horas de trabajo, **¡considera dejarle una estrella al repositorio!**

*Desarrollado y mantenido por [José Moreno](https://github.com/joseamorenoc025).*
