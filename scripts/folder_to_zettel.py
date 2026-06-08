#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  folder_to_zettel.py — Robot Convertidor de Carpetas a Obsidian Zettelkasten ║
║  Parte de la Skill: folder-to-zettel                                         ║
║  Versión: 1.0.0  |  Autor: Antigravity AI                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Requisito único: Python 3.8+                                                ║
║  El robot instala automáticamente todas sus dependencias la primera vez.     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Uso:                                                                        ║
║    python folder_to_zettel.py -i "C:/MiCarpeta" -o "D:/Obsidian/Imports"   ║
║    python folder_to_zettel.py -i "C:/MiCarpeta" -o "D:/Obsidian" --dry-run ║
║    python folder_to_zettel.py --help                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import subprocess
import importlib

# ── Fix Windows terminal encoding (CP1252 → UTF-8) ──────────────────────────
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    # Also set the PYTHONIOENCODING env var for subprocesses
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
# ─────────────────────────────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════════════════
# BOOTSTRAPPER ── Auto-instalación silenciosa de dependencias
# ══════════════════════════════════════════════════════════════════════════════

REQUIRED_PACKAGES = {
    "pathspec":           "pathspec>=0.12",
    "docx":               "python-docx>=1.1",
    "pypdf":              "pypdf>=4.0",
    "markdownify":        "markdownify>=0.12",
    "bs4":                "beautifulsoup4>=4.12",
    "charset_normalizer": "charset-normalizer>=3",
    "tqdm":               "tqdm>=4.65",
}


def bootstrap() -> None:
    """Detecta e instala silenciosamente las dependencias que falten."""
    missing = []
    for module, package in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(package)

    if not missing:
        return

    print(f"\n⚙️  Primera ejecución: instalando {len(missing)} dependencia(s)...", flush=True)
    for pkg in missing:
        print(f"   → {pkg}", flush=True)
        subprocess.run(
            [
                sys.executable, "-m", "pip", "install", pkg,
                "--quiet", "--disable-pip-version-check", "--no-warn-script-location"
            ],
            check=True,
            capture_output=True,
        )
    print("✅ Dependencias instaladas. Continuando...\n", flush=True)


bootstrap()  # Ejecutar antes de cualquier import externo

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS (post-bootstrap)
# ══════════════════════════════════════════════════════════════════════════════

import argparse
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import pathspec
from tqdm import tqdm
from charset_normalizer import from_path

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

VERSION = "1.0.0"

LANGUAGE_MAP: dict[str, str] = {
    # Web
    ".html": "html",  ".htm": "html",  ".css": "css",  ".scss": "scss",
    ".less": "less",  ".vue": "vue",   ".svelte": "svelte",
    # JS / TS
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "tsx", ".jsx": "jsx",
    # Python
    ".py": "python", ".pyw": "python",
    # Go / Rust / C / C++
    ".go": "go", ".rs": "rust", ".c": "c", ".h": "c",
    ".cpp": "cpp", ".cxx": "cpp", ".cc": "cpp", ".hpp": "cpp",
    # JVM
    ".java": "java", ".kt": "kotlin", ".scala": "scala", ".groovy": "groovy",
    # .NET
    ".cs": "csharp", ".vb": "vb",
    # Scripting
    ".rb": "ruby", ".php": "php", ".lua": "lua",
    ".sh": "bash", ".bash": "bash", ".zsh": "bash",
    ".ps1": "powershell", ".psm1": "powershell", ".psd1": "powershell",
    # Data / Config
    ".json": "json", ".jsonc": "json",
    ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml", ".ini": "ini", ".cfg": "ini",
    ".xml": "xml",  ".svg": "xml",
    ".sql": "sql",  ".graphql": "graphql", ".gql": "graphql",
    ".env": "bash", ".csv": "csv", ".tsv": "csv",
    # Systems
    ".swift": "swift", ".dart": "dart", ".r": "r",
    ".ex": "elixir", ".exs": "elixir",
    ".dockerfile": "dockerfile",
    # Infra
    ".tf": "hcl", ".hcl": "hcl",
}

TEXT_EXTENSIONS: set[str] = {
    ".txt", ".log", ".md", ".markdown", ".rst", ".tex",
    ".gitignore", ".gitattributes", ".editorconfig",
    ".prettierrc", ".eslintrc", ".babelrc", ".nvmrc",
    ".license", ".readme",
}

BINARY_EXTENSIONS: set[str] = {
    # Executables & libraries
    ".exe", ".dll", ".so", ".dylib", ".bin", ".o", ".a", ".lib",
    ".class", ".pyc", ".pyo",
    # Images
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".tiff", ".webp",
    ".svg_binary",
    # Audio / Video
    ".mp3", ".mp4", ".avi", ".mov", ".mkv", ".wav", ".flac", ".ogg",
    # Archives
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z",
    # Fonts
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    # Office binaries (old format)
    ".doc", ".xls", ".ppt",
    # Misc
    ".tmp", ".lock", ".db", ".sqlite", ".sqlite3",
}

IGNORED_DIRS: set[str] = {
    ".git", ".svn", ".hg",
    "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".tox",
    ".venv", "venv", "env", ".env", "virtualenv",
    "dist", "build", "out", ".next", ".nuxt", ".output",
    "coverage", ".nyc_output",
    "eggs", ".eggs", "*.egg-info",
    ".DS_Store",
}


# ══════════════════════════════════════════════════════════════════════════════
# SCANNER ── Recorre el árbol de carpetas filtrando archivos no deseados
# ══════════════════════════════════════════════════════════════════════════════

class FolderScanner:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._gitignore_spec = self._load_gitignore()

    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        gi = self.root / ".gitignore"
        if gi.exists():
            lines = gi.read_text(encoding="utf-8", errors="ignore").splitlines()
            return pathspec.PathSpec.from_lines("gitwildmatch", lines)
        return None

    def _is_ignored(self, path: Path) -> bool:
        rel = path.relative_to(self.root)
        # Check ignored directory names anywhere in the path
        for part in rel.parts:
            if part in IGNORED_DIRS or part.endswith(".egg-info"):
                return True
        # Check .gitignore rules
        if self._gitignore_spec and self._gitignore_spec.match_file(str(rel)):
            return True
        return False

    def scan(self) -> list[Path]:
        """Returns sorted list of all non-ignored files."""
        files = []
        for path in sorted(self.root.rglob("*")):
            if path.is_file() and not self._is_ignored(path):
                files.append(path)
        return files


# ══════════════════════════════════════════════════════════════════════════════
# CONVERTER ── Convierte cada formato a Markdown
# ══════════════════════════════════════════════════════════════════════════════

class FileConverter:

    @staticmethod
    def safe_read_text(path: Path) -> tuple[str, str]:
        """Lee texto con detección automática de encoding.
        Retorna (contenido, encoding_detectado)."""
        # charset-normalizer approach
        results = from_path(str(path))
        best = results.best()
        if best is not None:
            return str(best), best.encoding or "utf-8"
        # Fallback manual
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"):
            try:
                return path.read_text(encoding=enc, errors="replace"), enc
            except Exception:
                continue
        return "[ERROR: No se pudo decodificar el archivo]", "unknown"

    @staticmethod
    def convert_code(path: Path, text: str) -> str:
        lang = LANGUAGE_MAP.get(path.suffix.lower(), "")
        return f"```{lang}\n{text}\n```"

    @staticmethod
    def convert_html(path: Path) -> str:
        from markdownify import markdownify as md
        from bs4 import BeautifulSoup
        raw = path.read_bytes()
        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return md(str(soup), heading_style="ATX", bullets="-", newline_style="backslash")

    @staticmethod
    def convert_docx(path: Path) -> str:
        from docx import Document
        doc = Document(str(path))
        lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                lines.append("")
                continue
            style = para.style.name
            if "Heading 1" in style:
                lines.append(f"# {text}")
            elif "Heading 2" in style:
                lines.append(f"## {text}")
            elif "Heading 3" in style:
                lines.append(f"### {text}")
            elif "Heading 4" in style:
                lines.append(f"#### {text}")
            elif style in ("List Bullet", "List Bullet 2"):
                lines.append(f"- {text}")
            elif style in ("List Number", "List Number 2"):
                lines.append(f"1. {text}")
            else:
                lines.append(text)
        return "\n\n".join(l for l in lines if l is not None)

    @staticmethod
    def convert_pdf(path: Path) -> str:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(f"### Página {i}\n\n{text}")
        if not pages:
            return "> ⚠️ Este PDF no contiene texto extraíble (puede ser una imagen escaneada)."
        return "\n\n---\n\n".join(pages)

    def convert(self, path: Path) -> tuple[str, str]:
        """Convierte un archivo a Markdown.
        Retorna (contenido_md, status) donde status ∈ {'ok', 'ignored', 'error'}
        """
        suffix = path.suffix.lower()

        # Hard-skip binaries
        if suffix in BINARY_EXTENSIONS:
            return "", "ignored"

        # Skip very large files (> 5MB) — likely not useful text
        try:
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > 5:
                return f"> ⚠️ Archivo omitido: tamaño {size_mb:.1f}MB supera el límite de 5MB.", "ignored"
        except Exception:
            pass

        try:
            # HTML
            if suffix in (".html", ".htm"):
                return self.convert_html(path), "ok"

            # Word
            if suffix == ".docx":
                return self.convert_docx(path), "ok"

            # PDF
            if suffix == ".pdf":
                return self.convert_pdf(path), "ok"

            # Known code / data format
            if suffix in LANGUAGE_MAP:
                text, _ = self.safe_read_text(path)
                return self.convert_code(path, text), "ok"

            # Known text extensions or no extension
            if suffix in TEXT_EXTENSIONS or suffix == "":
                text, _ = self.safe_read_text(path)
                return text, "ok"

            # Unknown: try as plain text
            text, enc = self.safe_read_text(path)
            if text and "[ERROR" not in text:
                return text, "ok"

            return "", "ignored"

        except Exception as exc:
            return f"> ⚠️ **Error al convertir este archivo:** `{exc}`", "error"


# ══════════════════════════════════════════════════════════════════════════════
# ZETTEL FORMATTER ── Aplica el formato Obsidian Zettelkasten
# ══════════════════════════════════════════════════════════════════════════════

class ZettelFormatter:
    def __init__(self, root: Path, root_tag: str, run_ts: datetime) -> None:
        self.root = root
        self.root_tag = root_tag.lstrip("#").strip()
        self.run_ts = run_ts
        self._uid_seq = 0

    def generate_uid(self) -> str:
        """Genera un UID único basado en timestamp + secuencia."""
        self._uid_seq += 1
        return f"{self.run_ts.strftime('%Y%m%d%H%M')}{self._uid_seq:04d}"

    def path_to_tags(self, path: Path) -> list[str]:
        rel = path.relative_to(self.root)
        folder_parts = list(rel.parts[:-1])  # Sin el nombre de archivo
        suffix = path.suffix.lower()

        tags = [f"#{self.root_tag}"]

        # Tipo de fuente
        if suffix in LANGUAGE_MAP and suffix not in TEXT_EXTENSIONS:
            tags.append("#source/code")
        elif suffix == ".pdf":
            tags.append("#source/pdf")
        elif suffix == ".docx":
            tags.append("#source/document")
        elif suffix in (".html", ".htm"):
            tags.append("#source/web")
        elif suffix in TEXT_EXTENSIONS:
            tags.append("#source/text")
        else:
            tags.append("#source/other")

        # Tags jerárquicos de ruta de carpeta
        if folder_parts:
            clean_parts = [re.sub(r"[^\w\-]", "-", p) for p in folder_parts]
            tags.append(f"#folder/{'/'.join(clean_parts)}")

        return tags

    def clean_stem(self, stem: str) -> str:
        # 1. Corregir caracteres corruptos de español (acentos, eñes)
        corruptions = [
            (r'Aceptaci[^\w]n', 'Aceptación'),
            (r'Constituci[^\w]n', 'Constitución'),
            (r'CREACI[^\w]N', 'CREACIÓN'),
            (r'Invitaci[^\w]n', 'Invitación'),
            (r'Presentaci[^\w]n', 'Presentación'),
            (r'Gu[^\w]a', 'Guía'),
            (r'L[^\w]deres', 'Líderes'),
            (r'Ni[^\w]os', 'Niños'),
            (r'ni[^\w]os', 'niños'),
            (r'constituci[^\w]n', 'constitución'),
            (r'creaci[^\w]n', 'creación'),
            (r'invitaci[^\w]n', 'invitación'),
            (r'presentaci[^\w]n', 'presentación'),
            (r'gu[^\w]a', 'guía'),
            (r'l[^\w]deres', 'líderes'),
        ]
        for pattern, replacement in corruptions:
            stem = re.compile(pattern, re.IGNORECASE).sub(replacement, stem)

        # 2. Quitar prefijo numérico inicial (ej. "001_", "001_167_", "005__")
        stem = re.sub(r'^\d+(?:[\s_\-]+\d+)*[\s_\-]+', '', stem)

        # 3. Eliminar caracteres , \ufffd y signos de interrogación sobrantes (como ????)
        stem = stem.replace('\ufffd', ' ')
        stem = re.sub(r'\?+', ' ', stem)

        # 4. Quitar caracteres problemáticos para Obsidian
        stem = re.sub(r'[\\/:*?"<>|#\[\]]', ' ', stem)

        # 5. Limpiar espacios y guiones múltiples
        stem = re.sub(r'[\s_\-]+', ' ', stem)

        return stem.strip()

    def safe_title(self, path: Path) -> str:
        cleaned = self.clean_stem(path.stem)
        return cleaned.title()

    def safe_note_name(self, path: Path) -> str:
        """Nombre de la nota sin extensión, seguro para Obsidian."""
        cleaned = self.clean_stem(path.stem)
        return cleaned

    def format_note(self, path: Path, content: str, uid: str, moc_name: str) -> str:
        rel = path.relative_to(self.root)
        rel_str = str(rel).replace(os.sep, "/")
        tags = self.path_to_tags(path)
        title = self.safe_title(path)
        date_str = self.run_ts.strftime("%Y-%m-%d")
        ts_str = self.run_ts.strftime("%Y-%m-%d %H:%M")

        # Construir YAML tags
        tags_yaml = "\n".join(f'  - "{t}"' for t in tags)

        frontmatter = (
            f"---\n"
            f'id: "{uid}"\n'
            f'title: "{title}"\n'
            f'original_file: "{rel_str}"\n'
            f"created: {date_str}\n"
            f"status: imported\n"
            f"tags:\n{tags_yaml}\n"
            f"type: note\n"
            f"---"
        )

        header = f"# {title}"
        meta = f"> 📄 **Origen:** `{rel_str}`  |  🕐 **Importado:** {ts_str}  |  🆔 `{uid}`"
        divider = "---"
        footer = (
            f"*Nota importada automáticamente por `folder-to-zettel` v{VERSION}*\n"
            f"*← Volver al índice: [[{moc_name}]]*"
        )

        return f"{frontmatter}\n\n{header}\n\n{meta}\n\n{divider}\n\n{content}\n\n{divider}\n\n{footer}\n"


# ══════════════════════════════════════════════════════════════════════════════
# MOC GENERATOR ── Genera el Map of Content central
# ══════════════════════════════════════════════════════════════════════════════

class MocGenerator:
    def __init__(self, root: Path, root_tag: str, run_ts: datetime) -> None:
        self.root = root
        self.root_tag = root_tag.lstrip("#").strip()
        self.run_ts = run_ts

    def generate(self, processed: list[dict], stats: dict, moc_name: str) -> str:
        date_str = self.run_ts.strftime("%Y-%m-%d")
        ts_str = self.run_ts.strftime("%Y-%m-%d %H:%M:%S")
        uid = self.run_ts.strftime("%Y%m%d%H%M") + "0000"
        root_str = str(self.root).replace(os.sep, "/")

        # Agrupar notas por carpeta
        tree: dict[str, list[dict]] = {}
        for item in processed:
            folder = str(Path(item["original_path"]).parent).replace(os.sep, "/")
            tree.setdefault(folder, []).append(item)

        # Construir sección de árbol
        tree_lines = []
        for folder in sorted(tree.keys()):
            label = f"📁 `{self.root.name}/`  *(raíz)*" if folder == "." else f"📂 `{folder}/`"
            tree_lines.append(f"\n### {label}\n")
            for item in sorted(tree[folder], key=lambda x: x["title"]):
                note_link = f"[[{item['note_name']}]]"
                orig = item["original_path"]
                uid_short = item["uid"]
                tree_lines.append(f"- {note_link} — `{orig}` ·  🆔 `{uid_short}`")

        tree_section = "\n".join(tree_lines)

        # Tabla de estadísticas
        duration = stats.get("duration", 0)
        stats_table = (
            "| Métrica | Valor |\n"
            "|---------|-------|\n"
            f"| ✅ Notas generadas | **{stats['ok']}** |\n"
            f"| ⏭️ Archivos ignorados | {stats['ignored']} |\n"
            f"| ❌ Errores | {stats['error']} |\n"
            f"| 📁 Carpetas procesadas | {stats['folders']} |\n"
            f"| ⏱️ Tiempo de ejecución | {duration:.1f}s |\n"
            f"| 🕐 Timestamp | `{ts_str}` |"
        )

        frontmatter = (
            f"---\n"
            f'id: "{uid}"\n'
            f'title: "MOC Import — {date_str}"\n'
            f"created: {date_str}\n"
            f"status: MOC\n"
            f"tags:\n"
            f'  - "#brain/MOC"\n'
            f'  - "#{self.root_tag}"\n'
            f"type: MOC\n"
            f'source_folder: "{root_str}"\n'
            f"total_notes: {stats['ok']}\n"
            f"---"
        )

        return (
            f"{frontmatter}\n\n"
            f"# 🗺️ Mapa de Contenidos — Importación {date_str}\n\n"
            f"> **{stats['ok']} notas** importadas desde `{root_str}`\n"
            f"> Generado por `folder-to-zettel` v{VERSION} · {ts_str}\n\n"
            f"---\n\n"
            f"## 📋 Índice por Carpeta\n"
            f"{tree_section}\n\n"
            f"---\n\n"
            f"## 📊 Estadísticas de Importación\n\n"
            f"{stats_table}\n\n"
            f"---\n\n"
            f"*Este MOC es el **nodo central** de esta importación.*\n"
            f"*Ábrelo en Obsidian y activa el **Graph View** para ver tu red de conocimiento.*\n"
        )


# ══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR ── Coordina todo el proceso
# ══════════════════════════════════════════════════════════════════════════════

class FolderToZettel:
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        root_tag: str,
        mode: str,
        no_moc: bool,
        dry_run: bool,
    ) -> None:
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.root_tag = root_tag
        self.mode = mode
        self.no_moc = no_moc
        self.dry_run = dry_run
        self.run_ts = datetime.now()
        self.moc_name = f"_MOC_Import_{self.run_ts.strftime('%Y%m%d_%H%M')}"

        self.converter = FileConverter()
        self.formatter = ZettelFormatter(self.input_dir, root_tag, self.run_ts)

    def _output_path(self, source: Path) -> Path:
        rel = source.relative_to(self.input_dir)
        if self.mode == "flat":
            flat_name = "_".join(rel.parts)
            return self.output_dir / (flat_name + ".md")
        else:  # mirror
            return self.output_dir / rel.parent / (self.formatter.safe_note_name(source) + ".md")

    def _print_banner(self) -> None:
        w = 64
        print(f"\n{'━'*w}")
        print(f"  🤖  folder-to-zettel  v{VERSION}".center(w))
        print(f"{'━'*w}")
        print(f"  📂 Origen   → {self.input_dir}")
        print(f"  📥 Destino  → {self.output_dir}")
        print(f"  🏷️  Tag raíz → #{self.root_tag}")
        print(f"  📐 Modo     → {self.mode}")
        print(f"  🗺️  MOC      → {'No' if self.no_moc else 'Sí'}")
        if self.dry_run:
            print(f"  👁️  DRY-RUN  → ACTIVO (no se escribirá nada)")
        print(f"{'━'*w}\n")

    def run(self) -> None:
        self._print_banner()

        # Validaciones
        if not self.input_dir.exists():
            print(f"❌ La carpeta de origen no existe: {self.input_dir}")
            sys.exit(1)
        if not self.input_dir.is_dir():
            print(f"❌ La ruta de origen no es una carpeta: {self.input_dir}")
            sys.exit(1)

        # Crear destino
        if not self.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        # Escanear archivos
        print("🔍 Escaneando archivos...", flush=True)
        scanner = FolderScanner(self.input_dir)
        all_files = scanner.scan()
        print(f"   Encontrados: {len(all_files)} archivos\n", flush=True)

        if not all_files:
            print("⚠️  No se encontraron archivos para convertir.")
            return

        # Procesar
        start_ts = datetime.now()
        processed: list[dict] = []
        stats = {"ok": 0, "ignored": 0, "error": 0, "folders": 0}
        folders_seen: set[str] = set()
        errors: list[str] = []

        for file_path in tqdm(all_files, desc="Convirtiendo", unit="archivo", ncols=72):
            content_md, status = self.converter.convert(file_path)

            if status == "ignored":
                stats["ignored"] += 1
                continue

            uid = self.formatter.generate_uid()
            note_name = self.formatter.safe_note_name(file_path)
            rel_str = str(file_path.relative_to(self.input_dir)).replace(os.sep, "/")
            folder_str = str(file_path.relative_to(self.input_dir).parent).replace(os.sep, "/")
            folders_seen.add(folder_str)

            note_content = self.formatter.format_note(file_path, content_md, uid, self.moc_name)
            out_path = self._output_path(file_path)

            if not self.dry_run:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(note_content, encoding="utf-8")

            processed.append({
                "note_name": note_name,
                "title": self.formatter.safe_title(file_path),
                "original_path": rel_str,
                "uid": uid,
                "status": status,
            })

            if status == "error":
                stats["error"] += 1
                errors.append(rel_str)
            else:
                stats["ok"] += 1

        stats["folders"] = len(folders_seen)
        stats["duration"] = (datetime.now() - start_ts).total_seconds()

        # Generar MOC
        moc_path = None
        if not self.no_moc and processed:
            moc_gen = MocGenerator(self.input_dir, self.root_tag, self.run_ts)
            moc_content = moc_gen.generate(processed, stats, self.moc_name)
            moc_path = self.output_dir / f"{self.moc_name}.md"
            if not self.dry_run:
                moc_path.write_text(moc_content, encoding="utf-8")

        # Resumen final
        w = 64
        print(f"\n{'━'*w}")
        print(f"  🎉 ¡Conversión completada!")
        print(f"{'━'*w}")
        print(f"  ✅ Notas generadas :  {stats['ok']}")
        print(f"  ⏭️  Ignorados       :  {stats['ignored']}")
        print(f"  ❌ Errores         :  {stats['error']}")
        print(f"  ⏱️  Tiempo          :  {stats['duration']:.1f}s")
        if not self.dry_run:
            print(f"\n  📂 Notas en : {self.output_dir}")
            if moc_path:
                print(f"  🗺️  MOC en   : {moc_path}")
                print(f"\n  💡 Abre el MOC en Obsidian y activa el Graph View")
                print(f"     para ver tu red de conocimiento Zettelkasten.")
        if errors:
            print(f"\n  ⚠️  Archivos con errores:")
            for e in errors[:10]:
                print(f"     • {e}")
            if len(errors) > 10:
                print(f"     ... y {len(errors) - 10} más.")
        print(f"{'━'*w}\n")


# ══════════════════════════════════════════════════════════════════════════════
# CLI ── Punto de entrada
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="folder_to_zettel",
        description=(
            "🤖 Robot Convertidor de Carpetas a Obsidian Zettelkasten\n"
            "Convierte carpetas completas de archivos en notas Markdown\n"
            "con UIDs únicos, tags jerárquicos y Map of Content (MOC)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            '  python folder_to_zettel.py -i "C:/MiProyecto" -o "D:/Obsidian/Imports"\n'
            '  python folder_to_zettel.py -i "C:/Docs" -o "D:/Vault" --tag "trabajo/docs"\n'
            '  python folder_to_zettel.py -i "C:/Codigo" -o "D:/Vault" --mode flat\n'
            '  python folder_to_zettel.py -i "C:/Codigo" -o "D:/Vault" --dry-run\n'
        ),
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Carpeta de origen a convertir (ruta absoluta o relativa)."
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="Carpeta de destino en tu bóveda de Obsidian."
    )
    parser.add_argument(
        "--tag", default="brain/imported",
        help="Etiqueta raíz Zettelkasten para todas las notas (sin '#'). Default: brain/imported"
    )
    parser.add_argument(
        "--mode", choices=["mirror", "flat"], default="mirror",
        help=(
            "mirror = replica la estructura de subcarpetas en el destino (default). "
            "flat = todas las notas en el mismo nivel."
        )
    )
    parser.add_argument(
        "--no-moc", action="store_true",
        help="No generar el archivo Map of Content (_MOC_Import.md)."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Modo preview: muestra qué haría sin escribir ningún archivo."
    )
    parser.add_argument(
        "--version", action="version", version=f"folder-to-zettel {VERSION}"
    )

    args = parser.parse_args()

    robot = FolderToZettel(
        input_dir=args.input,
        output_dir=args.output,
        root_tag=args.tag,
        mode=args.mode,
        no_moc=args.no_moc,
        dry_run=args.dry_run,
    )
    robot.run()


if __name__ == "__main__":
    main()
