---
name: folder-to-zettel
description: >
  Use this skill when the user wants to convert a folder, directory, or project
  of files into Markdown notes formatted for Obsidian using the Zettelkasten method.
  Activate on requests like: "convert folder to markdown", "importar carpeta a obsidian",
  "convertir proyecto a zettelkasten", "crear notas de esta carpeta", "pasar mis archivos
  a obsidian", "robot convertidor a markdown". This skill runs a local self-installing
  Python robot that requires zero technical configuration from the user.
---

# Skill: Folder → Zettelkasten (Obsidian)

Convierte carpetas completas de archivos (código, documentos, HTML, PDF, Word, texto)
en notas Markdown listas para Obsidian con UIDs únicos, tags jerárquicos y un
Map of Content (MOC) central. Usa el método Zettelkasten.

---

## 1. Localizar el Robot

El robot vive en esta ruta fija del sistema del usuario:

```
C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel/scripts/folder_to_zettel.py
```

Antes de ejecutar, confirma que existe:

```powershell
Test-Path "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel/scripts/folder_to_zettel.py"
```

Si devuelve `False`, **no ejecutes nada más**: informa al usuario que la Skill no está
instalada y que debe ejecutar el instalador (ver sección Reinstalación).

---

## 2. Ejecutar el Robot

Usa exactamente este patrón de comando. Sustituye las rutas con los valores del usuario:

```powershell
python "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel/scripts/folder_to_zettel.py" `
  -i "RUTA_CARPETA_ORIGEN" `
  -o "RUTA_CARPETA_DESTINO_OBSIDIAN"
```

### Opciones Completas

| Flag | Descripción | Default |
|------|-------------|---------|
| `-i` / `--input` | Carpeta de origen a convertir **(REQUERIDO)** | — |
| `-o` / `--output` | Carpeta destino en bóveda Obsidian **(REQUERIDO)** | — |
| `--tag` | Etiqueta raíz Zettelkasten (sin `#`) | `brain/imported` |
| `--mode` | `mirror` = replica estructura de carpetas / `flat` = todo al mismo nivel | `mirror` |
| `--no-moc` | Omitir la generación del Map of Content | `False` |
| `--dry-run` | Preview: muestra qué haría sin escribir ningún archivo | `False` |

### Ejemplos de Uso

```powershell
# Conversión básica
python folder_to_zettel.py -i "C:/MiProyecto" -o "D:/Obsidian/Imports"

# Con tag raíz personalizado
python folder_to_zettel.py -i "C:/MiProyecto" -o "D:/Obsidian/Imports" --tag "proyectos/activos"

# Preview sin escribir (ideal para mostrar al usuario qué se convertirá)
python folder_to_zettel.py -i "C:/MiProyecto" -o "D:/Obsidian/Imports" --dry-run

# Todo en un nivel plano (sin subcarpetas en el destino)
python folder_to_zettel.py -i "C:/MiProyecto" -o "D:/Obsidian/Imports" --mode flat
```

---

## 3. Qué Genera el Robot

### Por cada archivo compatible → una nota `.md` con:
- **Renombrado Inteligente (Smart Renaming)**: Remueve automáticamente prefijos numéricos de secuencia (como `001_`, `011_`, `001_167_`), repara codificaciones dañadas de acentos y eñes (ej. `Aceptacin` → `Aceptación`), y limpia caracteres extraños.
- **YAML frontmatter**: `id` (UID único YYYYMMDDHHmmSSS), `title`, `original_file`,
  `created`, `status: imported`, `tags` jerárquicos, `type: note`
- **Cabecera con origen y fecha de importación**
- **Contenido convertido al formato Markdown correcto** (bloque de código, texto limpio, etc.)
- **Backlink al MOC** al pie de la nota

### Un archivo maestro `_MOC_Import_YYYYMMDD_HHMM.md` con:
- Árbol de todas las notas agrupadas por carpeta, con `[[wikilinks]]` de Obsidian
- Tabla de estadísticas (archivos procesados, ignorados, errores, tiempo)

---

## 4. Formatos Soportados

| Categoría | Extensiones |
|-----------|-------------|
| Código fuente | `.py` `.js` `.ts` `.tsx` `.go` `.rs` `.java` `.c` `.cpp` `.cs` `.rb` `.php` `.sh` `.ps1` `.sql` `.swift` `.kt` `.dart` y más |
| Datos / Config | `.json` `.yaml` `.yml` `.toml` `.xml` `.ini` `.env` `.csv` |
| Texto plano | `.txt` `.log` `.md` `.rst` |
| Web | `.html` `.htm` |
| Documentos Word | `.docx` |
| PDF | `.pdf` |
| **Ignorados** | `.exe` `.dll` `.jpg` `.png` `.zip` `.mp4` y todos los binarios |

---

## 5. Comportamiento Automático del Robot

- **Auto-instala dependencias**: La primera ejecución instala `pypdf`, `python-docx`,
  `markdownify`, `pathspec`, `tqdm` y `charset-normalizer` silenciosamente (~10s).
  No requiere intervención del usuario.
- **Respeta `.gitignore`**: Archivos y carpetas listados en `.gitignore` se omiten.
- **Ignora carpetas basura**: `node_modules`, `.git`, `__pycache__`, `.venv`, `dist`,
  `build`, `coverage` se saltan automáticamente.
- **Detección de encoding**: Lee archivos UTF-8, Latin-1, CP1252 sin errores.
- **Idempotente**: Puede ejecutarse múltiples veces. Sobreescribe notas existentes
  (no duplica).
- **Fail-safe**: Si un archivo falla, lo registra y continúa sin detenerse.

---

## 6. Informar al Usuario

Tras la ejecución, reporta siempre:
1. ✅ Número de notas generadas
2. 📂 Ruta exacta donde se guardaron
3. 🗺️ Nombre del archivo MOC generado (para que lo abra en Obsidian primero)
4. ⚠️ Si hubo errores, qué archivos fallaron y por qué
5. 💡 Sugerencia: "Abre el MOC en Obsidian y activa el Graph View para ver tu red de notas"

---

## 7. Reinstalación del Robot

Si el robot no existe en la ruta esperada, ejecuta este comando de reinstalación:

```powershell
# Crear estructura de directorios
New-Item -ItemType Directory -Force -Path "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel/scripts"

# Copiar desde scratch si existe ahí
Copy-Item "C:/Users/WIN/.gemini/antigravity/scratch/folder-to-zettel/scripts/folder_to_zettel.py" `
  -Destination "C:/Users/WIN/.gemini/antigravity/skills/folder-to-zettel/scripts/folder_to_zettel.py" `
  -Force
```

---

*Skill `folder-to-zettel` v1.0.0 — Creada por Antigravity AI*
*Compatible con: Antigravity, Codex CLI, y cualquier agente que lea SKILL.md*
