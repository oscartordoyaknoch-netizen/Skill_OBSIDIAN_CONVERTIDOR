# 🤖 folder-to-zettel

> Convierte carpetas completas de archivos en notas Markdown optimizadas para
> **Obsidian** con el método **Zettelkasten**. Diseñado como Skill nativa para
> agentes de IA (Antigravity, Codex).

---

## ✨ Características

- **Zero-setup**: Solo necesitas Python 3.8+. El robot instala sus dependencias solo.
- **Obsidian-nativo**: Genera YAML frontmatter, UIDs únicos, tags jerárquicos y wikilinks.
- **Map of Content (MOC)**: Nota índice central con árbol de todas las notas importadas.
- **Multi-formato**: Código, HTML, PDF, Word, texto plano, JSON, YAML y más.
- **Seguro**: Respeta `.gitignore`, ignora binarios, sin pérdida de datos.
- **Fail-safe**: Si un archivo falla, el proceso continúa sin detenerse.
- **Renombrado Inteligente**: Limpia automáticamente prefijos numéricos (como `001_`, `011_`) y repara caracteres corruptos de acentos en español en los nombres de archivo y títulos.

---

## 🧠 Renombrado Inteligente (Smart Renaming)

El robot incluye lógica avanzada para limpiar los nombres de los archivos antes de escribirlos en tu bóveda de Obsidian:
- **Limpieza de códigos y secuencias**: Si un archivo se llama `001_167 Greenside Solutions - - Cot.pdf`, la nota en Obsidian se guardará como `Greenside Solutions Cot.md`.
- **Restauración de acentos en español**: Repara automáticamente codificaciones erróneas o dañadas por sistemas de archivos heredados, transformándolos en palabras correctas (ej. `Aceptacin` → `Aceptación`, `Constitucin` → `Constitución`, `Organico` → `Orgánico`, `Nios` → `Niños`).
- **Limpieza de símbolos**: Elimina signos de interrogación repetidos (`????`) y comprime espacios o guiones dobles.

---

## 📁 Estructura de la Skill

```
folder-to-zettel/
├── SKILL.md                          ← Instrucciones para el agente de IA
├── scripts/
│   └── folder_to_zettel.py           ← El Robot (auto-suficiente)
├── examples/
│   └── sample_output/
│       ├── _MOC_Import_20260608_1122.md   ← Ejemplo de MOC generado
│       └── utils/
│           └── parser.md             ← Ejemplo de nota generada
└── resources/
    └── .zettel_defaults.json         ← Configuración por defecto
```

---

## 🚀 Instalación

Puedes instalar la Skill globalmente en tu sistema directamente desde el repositorio de GitHub para tenerla siempre disponible:

### Opción A — Clonando con Git (Recomendado)
```powershell
git clone "https://github.com/oscartordoyaknoch-netizen/Skill_OBSIDIAN_CONVERTIDOR.git" "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel"
```

### Opción B — Descarga directa vía PowerShell (si no tienes Git)
```powershell
# Descargar, extraer e instalar en la ruta de Skills de Antigravity
Invoke-WebRequest -Uri "https://github.com/oscartordoyaknoch-netizen/Skill_OBSIDIAN_CONVERTIDOR/archive/refs/heads/main.zip" -OutFile "$env:TEMP/skill.zip"
Expand-Archive -Path "$env:TEMP/skill.zip" -DestinationPath "$env:TEMP/skill_temp" -Force
New-Item -ItemType Directory -Force -Path "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel"
Copy-Item -Recurse -Force "$env:TEMP/skill_temp/Skill_OBSIDIAN_CONVERTIDOR-main/*" "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel"
Remove-Item -Recurse -Force "$env:TEMP/skill.zip", "$env:TEMP/skill_temp"
```


### Opción 2 — Uso Directo (sin instalar)

```powershell
python "C:/Users/WIN/.gemini/antigravity/scratch/folder-to-zettel/scripts/folder_to_zettel.py" `
  -i "CARPETA_ORIGEN" -o "CARPETA_DESTINO"
```

---

## 📖 Uso

### Sintaxis

```powershell
python folder_to_zettel.py -i "ORIGEN" -o "DESTINO" [opciones]
```

### Opciones

| Flag | Descripción | Default |
|------|-------------|---------|
| `-i` / `--input` | Carpeta de origen **(requerido)** | — |
| `-o` / `--output` | Carpeta destino en Obsidian **(requerido)** | — |
| `--tag` | Etiqueta raíz Zettelkasten (sin `#`) | `brain/imported` |
| `--mode` | `mirror` o `flat` | `mirror` |
| `--no-moc` | No generar el Map of Content | `False` |
| `--dry-run` | Preview sin escribir archivos | `False` |

### Ejemplos

```powershell
# Conversión básica
python folder_to_zettel.py -i "C:/MiProyecto" -o "D:/Obsidian/Imports"

# Con tag personalizado
python folder_to_zettel.py -i "C:/MiProyecto" -o "D:/Obsidian" --tag "proyectos/activos"

# Preview primero (sin escribir)
python folder_to_zettel.py -i "C:/MiProyecto" -o "D:/Obsidian" --dry-run

# Todo en un nivel plano
python folder_to_zettel.py -i "C:/MiProyecto" -o "D:/Obsidian" --mode flat
```

---

## 📄 Formatos Soportados

| Categoría | Extensiones |
|-----------|-------------|
| **Código fuente** | `.py` `.js` `.ts` `.tsx` `.go` `.rs` `.java` `.c` `.cpp` `.cs` `.rb` `.php` `.sh` `.ps1` `.sql` `.swift` `.kt` `.dart` y 20+ más |
| **Datos / Config** | `.json` `.yaml` `.yml` `.toml` `.xml` `.ini` `.env` `.csv` |
| **Texto** | `.txt` `.log` `.md` `.rst` |
| **Web** | `.html` `.htm` |
| **Documentos** | `.docx` |
| **PDF** | `.pdf` |
| **Ignorados** | Imágenes, ejecutables, archivos de audio/video, archivos comprimidos |

---

## 🗺️ Formato de Salida (Obsidian Zettelkasten)

### Cada nota generada incluye:

```markdown
---
id: "202606081122_0001"        ← UID único Zettelkasten
title: "Parser"
original_file: "src/utils/parser.py"
created: 2026-06-08
status: imported               ← Filtrable con Dataview
tags:
  - "#brain/imported"
  - "#source/code"
  - "#folder/src/utils"        ← Tag jerárquico de la ruta
type: note
---

# Parser

> 📄 Origen: src/utils/parser.py | 🕐 Importado: 2026-06-08 11:22

---

[Contenido convertido]

---
*← Volver al índice: [[_MOC_Import_20260608_1122]]*
```

---

## 🧰 Dependencias (Auto-instaladas)

El robot instala automáticamente lo que necesita en la primera ejecución:

| Paquete | Uso |
|---------|-----|
| `pathspec` | Parseo de reglas `.gitignore` |
| `python-docx` | Lectura de archivos `.docx` |
| `pypdf` | Extracción de texto de PDFs |
| `markdownify` | Conversión HTML → Markdown |
| `beautifulsoup4` | Limpieza de HTML |
| `charset-normalizer` | Detección automática de encoding |
| `tqdm` | Barra de progreso en terminal |

---

## 📋 Requisitos

- **Python 3.8+** (único requisito manual)
- Conexión a internet en la primera ejecución (para instalar dependencias)

---

*Skill `folder-to-zettel` v1.0.0 — Creada por Antigravity AI*
