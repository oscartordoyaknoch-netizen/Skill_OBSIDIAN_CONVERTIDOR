---
id: "2026060811220003"
title: "Parser"
original_file: "src/utils/parser.py"
created: 2026-06-08
status: imported
tags:
  - "#brain/imported"
  - "#source/code"
  - "#folder/src/utils"
type: note
---

# Parser

> 📄 **Origen:** `src/utils/parser.py`  |  🕐 **Importado:** 2026-06-08 11:22  |  🆔 `2026060811220003`

---

```python
"""Módulo de parsing de documentos."""

import re
from typing import Optional


def parse_document(text: str, lang: str = "es") -> dict:
    """
    Analiza un documento de texto y extrae sus componentes principales.
    
    Args:
        text: El texto a analizar.
        lang: Código de idioma (default: 'es').
    
    Returns:
        dict con keys: title, summary, keywords, word_count
    """
    lines = text.strip().split("\n")
    title = lines[0].strip() if lines else "Sin título"
    
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    # Extraer palabras clave (las más frecuentes, excluyendo stopwords)
    stopwords = {"el", "la", "de", "en", "y", "a", "que", "es"}
    freq: dict[str, int] = {}
    for w in words:
        if w not in stopwords and len(w) > 3:
            freq[w] = freq.get(w, 0) + 1
    
    keywords = sorted(freq, key=freq.get, reverse=True)[:5]
    
    return {
        "title": title,
        "summary": " ".join(lines[:3]),
        "keywords": keywords,
        "word_count": word_count,
        "lang": lang,
    }
```

---

*Nota importada automáticamente por `folder-to-zettel` v1.0.0*
*← Volver al índice: [[_MOC_Import_20260608_1122]]*
