#!/usr/bin/env python3
"""LokroOS Manifest-Verifikation: prüft packages/manifest-*.json auf
Konsistenz (doppelte Pakete über Manifeste, Node-Einfachheit, i386-Flag).
Exit 0 = OK, Exit 1 = Fehler. Keine Netzwerkzugriffe, keine Root-Rechte nötig.
"""
import argparse
import json
import sys
from pathlib import Path


def load_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"FEHLER: {path.name} ist kein gültiges JSON: {exc}")
        raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root)
    pkgdir = root / "packages"
    errors: list[str] = []
    seen: dict[str, str] = {}

    for mf in sorted(pkgdir.glob("manifest-*.json")):
        data = load_manifest(mf)
        pkgs = data.get("packages", [])
        if not isinstance(pkgs, list) or not pkgs:
            errors.append(f"{mf.name}: 'packages' fehlt oder leer")
            continue
        for p in pkgs:
            base = str(p).split(":")[0]
            if base in seen and seen[base] != mf.name:
                # Duplikate über Manifeste sind Warnung, kein Fehler (Basis vs. Gaming teilen mesa o.ä.)
                print(f"HINWEIS: Paket '{p}' in {seen[base]} und {mf.name}")
            seen.setdefault(base, mf.name)

    # Regel: genau EINE Node-Quelle (keine konkurrierenden Node-Versionen)
    dev = load_manifest(pkgdir / "manifest-dev.json") if (pkgdir / "manifest-dev.json").exists() else {}
    repos = [r.get("name", "") for r in dev.get("repos", [])]
    if sum("node" in r for r in repos) > 1:
        errors.append("manifest-dev.json: mehrere Node-Quellen – nur eine erlaubt")
    if "nodejs" not in [str(p) for p in dev.get("packages", [])]:
        errors.append("manifest-dev.json: 'nodejs' fehlt")

    gaming = load_manifest(pkgdir / "manifest-gaming.json") if (pkgdir / "manifest-gaming.json").exists() else {}
    if gaming and not gaming.get("enable_i386"):
        errors.append("manifest-gaming.json: enable_i386 muss true sein (Steam/Proton brauchen 32-Bit)")

    if errors:
        print("MANIFEST-FEHLER:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"Manifeste OK: {len(seen)} eindeutige Paketeinträge über alle Manifeste.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
