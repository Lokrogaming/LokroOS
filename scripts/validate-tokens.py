#!/usr/bin/env python3
"""Prüft branding/tokens.json gegen erwartete Struktur (Farben, Radien, Motion).
Wird in CI/Tests und vor ISO-Builds ausgeführt."""
import json
import sys
from pathlib import Path

REQUIRED = [
    ("color", "surface", "black"),
    ("color", "accent", "cyan"),
    ("color", "text", "primary"),
    ("radius", "lg"),
    ("motion", "base"),
    ("typography", "font-family"),
]

root = Path(__file__).resolve().parents[1]
tokens_path = root / "branding" / "tokens.json"
try:
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
except Exception as exc:  # noqa: BLE001
    print(f"FEHLER: tokens.json ungültig: {exc}")
    raise SystemExit(1)

missing = []
for path in REQUIRED:
    node = tokens
    for key in path:
        if isinstance(node, dict) and key in node:
            node = node[key]
        else:
            missing.append(".".join(path))
            break

if missing:
    print("Fehlende Design-Tokens:", ", ".join(missing))
    raise SystemExit(1)
print(f"Design-Tokens OK ({tokens_path.name}, v{tokens.get('meta', {}).get('version', '?')}).")
