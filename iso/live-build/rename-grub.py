#!/usr/bin/env python3
"""LokroOS GRUB-Titel-Rename (schlicht, kein GfxTheme – Beschluss 2026-10-11).

Benennt in allen config/bootloaders/*/grub.cfg eines live-build-Baums um:
  - erster NICHT-safe-Eintrag  -> "Try or Install LokroOS"
  - safe-Eintraege (failsafe/safe/nomodeset in Titel oder Body)
                             -> "LokroOS (safe graphics)"
Fail-fast: fehlt danach ein Pflicht-Titel, Exit 1 (kein falsches ISO).

Gebrauch: rename-grub.py <build-dir>   (auch standalone testbar, siehe
tests/fixtures/grub-sample.cfg)
"""
import pathlib
import re
import sys

MAIN_TITLE = "Try or Install LokroOS"
SAFE_TITLE = "LokroOS (safe graphics)"


def is_safe(title: str, body: str) -> bool:
    blob = (title + " " + body).lower()
    return ("failsafe" in blob or "safe graphics" in blob
            or "nomodeset" in blob)


def rename_file(cfg: pathlib.Path) -> None:
    text = cfg.read_text(encoding="utf-8")
    pattern = re.compile(r'menuentry\s+"([^"]*)"\s*([^{]*)\{(.*?)\n\}',
                         re.DOTALL)
    entries = list(pattern.finditer(text))
    if not entries:
        raise SystemExit(f"FEHLER: {cfg}: keine menuentry gefunden")
    main_done = False
    for m in entries:
        if not is_safe(m.group(1), m.group(3)) and not main_done:
            text = text.replace(
                m.group(0),
                m.group(0).replace(f'"{m.group(1)}"', f'"{MAIN_TITLE}"', 1),
                1)
            main_done = True
    for m in list(pattern.finditer(text)):
        title = m.group(1)
        if (is_safe(title, m.group(3)) and title not in (SAFE_TITLE,
                                                         MAIN_TITLE)):
            text = text.replace(
                m.group(0),
                m.group(0).replace(f'"{title}"', f'"{SAFE_TITLE}"', 1),
                1)
    cfg.write_text(text, encoding="utf-8")


def main(workdir: str) -> int:
    work = pathlib.Path(workdir)
    files = sorted((work / "config" / "bootloaders").rglob("grub.cfg"))
    if not files:
        print("FEHLER: keine grub.cfg unter config/bootloaders gefunden.")
        return 1
    for cfg in files:
        rename_file(cfg)
        print(f"{cfg.relative_to(work)}: Titel gesetzt")
    full = "\n".join(p.read_text(encoding="utf-8") for p in files)
    for need in (MAIN_TITLE, SAFE_TITLE):
        if need not in full:
            print(f"FEHLER: Pflicht-Titel fehlt: {need}")
            return 1
    print("GRUB-Titel OK")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Gebrauch: rename-grub.py <build-dir>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
