#!/usr/bin/env python3
"""Umgebungs-Check für LokroOS-Entwicklung (Windows-Host / Ubuntu-Build-VM).
Gibt eine Zusammenfassung aus und warnt vor fehlenden Build-Voraussetzungen.
Nie destruktiv, fragt nichts, ändert nichts."""
import platform
import shutil
import sys

print(f"OS: {platform.system()} {platform.release()} ({platform.machine()})")
print(f"Python: {sys.version.split()[0]}")

tools = ["git", "gh", "python3", "node", "npm", "wsl", "VBoxManage", "docker", "lb", "qemu-system-x86_64"]
for t in tools:
    print(f"  {t}: {shutil.which(t) or 'NICHT GEFUNDEN'}")

print("\nHinweise:")
if platform.system() != "Linux":
    print("  - ISO-Builds laufen NUR auf einer Ubuntu-24.04-Build-VM (WSL2/VM).")
    print("  - Auf diesem Host: Prototyp (Web-Preview, QML-Review, Tests) entwickeln.")
else:
    print("  - Auf Linux: siehe BUILD.md für live-build/Cubic-Setup.")
