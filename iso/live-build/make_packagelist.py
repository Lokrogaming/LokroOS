#!/usr/bin/env python3
"""LokroOS Paketlisten-Generator (importierbar + testbar).

Baut die live-build-Paketliste aus:
  packages/manifest-*.json + iso/live-build/extra-packages.txt
  MINUS iso/live-build/exclude-iso.txt
Dedupliziert, Reihenfolge stabil (Manifeste, dann Extras).

Gebrauch: make_packagelist.py <repo-root> <ziel-datei>
"""
import json
import pathlib
import sys


def _lines(path):
    """Nicht-leere, Kommentar-bereinigte Zeilen (Rohformat, ein Eintrag/Zeile)."""
    out = []
    for raw in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def build(repo_root):
    root = pathlib.Path(repo_root)
    pkgs, seen = [], set()

    def add(name):
        if name not in seen:
            seen.add(name)
            pkgs.append(name)

    for mf in sorted((root / "packages").glob("manifest-*.json")):
        data = json.loads(mf.read_text(encoding="utf-8"))
        for p in data.get("packages", []):
            add(str(p))
    extras = root / "iso" / "live-build" / "extra-packages.txt"
    if extras.is_file():
        for line in _lines(extras):
            add(line)
    excludes = root / "iso" / "live-build" / "exclude-iso.txt"
    if excludes.is_file():
        drop = {ln.split()[0] for ln in _lines(excludes)}
        pkgs = [p for p in pkgs if p.split(":")[0] not in drop
                and p not in drop]
    return pkgs


def main(argv):
    if len(argv) != 3:
        print("Gebrauch: make_packagelist.py <repo-root> <ziel-datei>")
        return 2
    pkgs = build(argv[1])
    header = ("# LokroOS Paketliste (generiert, NICHT von Hand editieren:"
              " make_packagelist.py)\n")
    pathlib.Path(argv[2]).write_text(header + "\n".join(pkgs) + "\n",
                                     encoding="utf-8")
    print(f"{len(pkgs)} Pakete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
