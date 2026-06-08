# 🤖 Guía de Integración para Agentes de IA / AI Agent Integration Guide
### Skill: `folder-to-zettel`

*Este archivo está diseñado para que asistentes de código de IA (Claude, GPT, Gemini, Codex, etc.) entiendan, instalen y ejecuten esta herramienta de forma autónoma.*
*This file is designed for AI coding assistants to automatically read, install, and run this tool.*

---

## 📋 Manifest / Ficha Técnica (For LLM parsing)
- **Tool Name**: `folder-to-zettel`
- **Description**: Convierte una carpeta de origen con múltiples formatos (PDF, Word, código, HTML, TXT) en notas Markdown estructuradas bajo el método Zettelkasten para Obsidian, aplicando renombrado inteligente (limpieza de códigos y restauración de acentos).
- **Global Install Location**: `C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel`
- **Robot Script Path**: `C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel/scripts/folder_to_zettel.py`
- **Auto-bootstrap**: El script instala sus propias dependencias de Python en su primera ejecución. No requiere que el agente o el usuario instalen librerías manualmente.

---

## 🛠️ Instrucciones para la IA / Instructions for the AI Agent

### Paso 1: Verificar existencia / Verify installation
Antes de proceder, verifica si el script del robot está instalado ejecutando este comando en la terminal:
```powershell
Test-Path "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel/scripts/folder_to_zettel.py"
```

### Paso 2: Instalar (si no existe) / Install (if missing)
Si el comando anterior devuelve `False`, puedes clonar la Skill directamente desde el repositorio de GitHub usando Git, o descargar el ZIP si Git no está instalado.

#### Opción A: Clonando con Git (Recomendado)
```powershell
git clone "https://github.com/oscartordoyaknoch-netizen/Skill_OBSIDIAN_CONVERTIDOR.git" "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel"
```

#### Opción B: Descarga directa del ZIP (Si Git no está instalado)
```powershell
# Descargar el ZIP temporalmente
Invoke-WebRequest -Uri "https://github.com/oscartordoyaknoch-netizen/Skill_OBSIDIAN_CONVERTIDOR/archive/refs/heads/main.zip" -OutFile "$env:TEMP/skill.zip"

# Extraer el archivo comprimido
Expand-Archive -Path "$env:TEMP/skill.zip" -DestinationPath "$env:TEMP/skill_temp" -Force

# Crear la carpeta de Skills globales
New-Item -ItemType Directory -Force -Path "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel"

# Copiar los archivos a la ubicación global
Copy-Item -Recurse -Force "$env:TEMP/skill_temp/Skill_OBSIDIAN_CONVERTIDOR-main/*" "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel"

# Limpiar archivos temporales
Remove-Item -Recurse -Force "$env:TEMP/skill.zip", "$env:TEMP/skill_temp"
```


### Paso 3: Ejecución / Run the conversion
Para realizar la conversión de archivos de tu cliente, ejecuta este comando sustituyendo `<ORIGEN>` y `<DESTINO>`:
```powershell
python "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel/scripts/folder_to_zettel.py" `
  -i "<ORIGEN>" `
  -o "<DESTINO>"
```

#### Parámetros soportados:
- `-i` / `--input`: Carpeta de archivos origen (ej. un pen drive `E:\Documentos`).
- `-o` / `--output`: Carpeta de la bóveda de Obsidian (ej. `C:\Users\WIN\OneDrive\8.- Horus\SEGUNDA MEMORIA OTK\MEMORY\BDS\Cliente`).
- `--tag`: Tag raíz para las notas (default: `brain/imported`).
- `--mode`: Modo de copia. `mirror` (replica carpetas, recomendado) o `flat` (vuelca todo en la raíz).

---

## 📄 Ejemplos de prompts que el usuario te puede dar:
* *"Tengo una carpeta en E:\Trabajo. Usa la skill folder-to-zettel instalada para pasarla a mi bóveda en C:\Users\WIN\OneDrive\...\MEMORY\BDS\Trabajo"*
* *"Ejecuta la skill folder-to-zettel para el pen drive F:\Docs al directorio de BDS en mi memoria"*

---

*Skill `folder-to-zettel` v1.0.0 · Creada por Antigravity AI*
