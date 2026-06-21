# 🚀 Guía de Publicación del Release v2.0.0

Esta guía te ayudará a publicar oficialmente Easy Converter v2.0.0 en GitHub.

---

## 📋 Checklist Pre-Release

### ✅ Verificaciones Finales

1. **Tests Locales**
   ```bash
   pytest tests/ -v --cov=src
   # Asegúrate de que la cobertura sea >90%
   ```

2. **Linting y Type Checking**
   ```bash
   flake8 src/ tests/
   mypy src/ --ignore-missing-imports
   black src/ tests/ --check
   ```

3. **Build Local (Opcional pero recomendado)**
   ```bash
   pyinstaller build/easy_converter.spec --clean
   # Verifica que el .exe se genera correctamente
   ```

4. **Documentación Actualizada**
   - ✅ README.md actualizado
   - ✅ RELEASE_NOTES_v2.0.0.md creado
   - ✅ Archivos de traducción completos (locales/)
   - ✅ CHANGELOG actualizado

5. **Versiones Consistentes**
   - ✅ `release_info.json`: version = "2.0.0"
   - ✅ `build/easy_converter.spec`: versión actualizada
   - ✅ `build/setup.iss`: versión actualizada
   - ✅ `src/__init__.py`: __version__ = "2.0.0"

---

## 🎯 Pasos para Publicar el Release

### Paso 1: Commit Final
```bash
git add .
git commit -m "chore: Release v2.0.0 - Major update with i18n, MVC architecture, and enhanced security"
git tag -a v2.0.0 -m "Easy Converter v2.0.0 - Production Ready"
```

### Paso 2: Push a GitHub
```bash
git push origin main
git push origin v2.0.0
```

### Paso 3: Crear Release en GitHub

#### Opción A: Desde GitHub Web UI
1. Ve a: https://github.com/TU_USUARIO/easy-converter/releases/new
2. **Tag version:** Selecciona `v2.0.0`
3. **Release title:** `Easy Converter v2.0.0 - Production Ready`
4. **Description:** Copia el contenido de `RELEASE_NOTES_v2.0.0.md`
5. **Pre-release:** ❌ Desmarcado (es release estable)
6. **Publish release:** ✅ Click en "Publish release"

#### Opción B: Desde CLI con gh (GitHub CLI)
```bash
gh release create v2.0.0 \
  --title "Easy Converter v2.0.0 - Production Ready" \
  --notes-file RELEASE_NOTES_v2.0.0.md \
  --repo TU_USUARIO/easy-converter
```

### Paso 4: Configurar Secrets en GitHub (Requerido para CI/CD)

Ve a: https://github.com/TU_USUARIO/easy-converter/settings/secrets/actions

Añade los siguientes secrets:

| Secret Name | Valor | Descripción |
|-------------|-------|-------------|
| `SONAR_TOKEN` | [Tu token de SonarCloud](https://sonarcloud.io/account/security/) | Para integración con SonarCloud |
| `CODECOV_TOKEN` | [Tu token de Codecov](https://app.codecov.io/account/repos) | Opcional, para Codecov |

> **Nota:** El `GITHUB_TOKEN` se genera automáticamente por GitHub Actions.

### Paso 5: Verificar CI/CD Pipeline

1. Ve a: https://github.com/TU_USUARIO/easy-converter/actions
2. Deberías ver el workflow ejecutándose automáticamente
3. Espera a que:
   - ✅ Tests pasen (>90% coverage)
   - ✅ Linting pase sin errores
   - ✅ Build de Windows se complete
   - ✅ Installer se genere y suba al release

### Paso 6: Verificar Release Assets

Después de que el pipeline termine:
1. Ve a: https://github.com/TU_USUARIO/easy-converter/releases/tag/v2.0.0
2. Verifica que aparezca el archivo:
   - ✅ `EasyConverter-Setup-2.0.0.exe` (o similar)
3. Descarga y prueba el instalador en una máquina limpia

---

## 🔍 Post-Release Verification

### En una Máquina Limpia (VM recomendada)

1. **Descargar Instalador**
   - Ve a la página de releases y descarga el `.exe`

2. **Instalar**
   - Ejecuta el instalador
   - Acepta instalar Tesseract OCR

3. **Pruebas Críticas**
   - [ ] La app inicia correctamente
   - [ ] Aparece el asistente de bienvenida
   - [ ] Puedes cambiar el idioma
   - [ ] Conversión PDF → Word funciona
   - [ ] Conversión Word → PDF funciona
   - [ ] El historial guarda conversiones
   - [ ] Ctrl+Z deshace la última operación
   - [ ] Los perfiles rápidos funcionan

4. **Verificar Actualización Automática**
   - Simula una nueva versión futura
   - Verifica que el checker de versiones funcione

---

## 📢 Anuncio del Release

### Plantilla para Redes Sociales / Foros

```
🎉 ¡Easy Converter v2.0.0 ya está disponible! ✨

Novedades principales:
🌍 Multi-idioma (ES, EN, PT, FR, DE)
🏗️ Nueva arquitectura MVC
🔒 Seguridad reforzada
📜 Historial persistente
↩️ Sistema de deshacer
⚡ Perfiles rápidos
🔄 Actualizaciones automáticas

Descárgalo aquí: https://github.com/TU_USUARIO/easy-converter/releases/tag/v2.0.0

#Python #PDF #Word #OpenSource #Windows
```

### Email a Usuarios Existentes (si aplica)

```
Asunto: 🎉 Easy Converter v2.0.0 - Gran Actualización Disponible

Hola [Nombre],

¡Tenemos grandes noticias! Easy Converter v2.0.0 ya está disponible con:

✨ Características nuevas:
- Soporte para 5 idiomas
- Asistente de bienvenida
- Historial de conversiones
- Sistema de deshacer
- Y mucho más...

📥 Descarga gratuita: [Enlace al Release]

Gracias por ser parte de nuestra comunidad.

Saludos,
El equipo de Easy Converter
```

---

## 🐛 Si Algo Sale Mal

### Problema: Tests Fallan en CI/CD
```bash
# Ejecuta tests localmente para debug
pytest tests/ -v --tb=short
# Corrige errores y haz push nuevamente
```

### Problema: Build de PyInstaller Falla
```bash
# Prueba build local
pyinstaller build/easy_converter.spec --clean --noconfirm
# Revisa logs en build/ y ajusta hiddenimports si es necesario
```

### Problema: Installer No Se Genera
```bash
# Verifica que Inno Setup esté instalado en el runner
# O usa un runner self-hosted con ISCC instalado
```

### Rollback de Emergencia
```bash
# Eliminar tag remoto
git push origin --delete v2.0.0
# Eliminar tag local
git tag -d v2.0.0
# Corregir errores y crear nuevo tag
git tag -a v2.0.1 -m "Hotfix for critical issue"
git push origin v2.0.1
```

---

## 📊 Monitoreo Post-Release

### Métricas a Seguir (Primera Semana)

1. **Descargas:** https://github.com/TU_USUARIO/easy-converter/releases
2. **Issues Reportados:** https://github.com/TU_USUARIO/easy-converter/issues
3. **Stars/Forks:** https://github.com/TU_USUARIO/easy-converter/stargazers
4. **CI/CD Success Rate:** https://github.com/TU_USUARIO/easy-converter/actions

### Respuesta Rápida a Issues

- Prioriza bugs críticos (crashes, pérdida de datos)
- Responde a todos los issues en <48 horas
- Crea milestone `v2.0.1` para hotfixes urgentes

---

## 🎉 ¡Éxito!

Si has seguido todos estos pasos, tu release v2.0.0 debería estar:
- ✅ Publicado en GitHub Releases
- ✅ Con instalador funcional
- ✅ Con CI/CD configurado para futuros releases
- ✅ Listo para distribución masiva

**¡Felicidades por el lanzamiento de Easy Converter v2.0.0!** 🚀

---

*Última actualización: 2024*
*Documento creado para Easy Converter v2.0.0 Release*
