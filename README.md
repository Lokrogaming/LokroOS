# LokroOS – Modernes Linux-Betriebssystem von LOKRO

![Status](https://img.shields.io/badge/Meilenstein-M1%20Prototyp-cyan) ![Basis](https://img.shields.io/badge/Basis-Ubuntu%2024.04%20LTS-blue) ![Desktop](https://img.shields.io/badge/Desktop-KDE%20Plasma%20Wayland-blueviolet)

**LokroOS** ist eine eigenständige, moderne Linux-Distribution auf **Ubuntu-24.04-LTS**-Basis
(Noble Numbat, amd64) mit **KDE Plasma + Wayland**, eigenem dunklem **Glassmorphism-Designsystem**,
animiertem **Welcome-Erlebnis** und vorinstallierten Werkzeugen für **Entwickler und Gamer**.

> Meilenstein 1 (dieser Stand): reproduzierbarer, getesteter **Desktop-Prototyp** mit
> LokroOS-Branding, funktionierendem Welcome-Erlebnis, Glass-Card-Oberfläche und klarer
> Grundlage für die spätere bootfähige ISO. Die ISO selbst wird in M2 auf einer
> Ubuntu-Build-VM gebaut und in einer VM verifiziert – hier wird **nichts behauptet,
> was nicht getestet wurde** (siehe Status-Tabelle unten).

## Schnellstart (Prototyp ansehen)

```bash
# Option A: Web-Preview im Browser öffnen (funktioniert auf Windows/Linux)
start shell\web-preview\index.html        # Windows
xdg-open shell/web-preview/index.html     # Linux

# Option B: Welcome-Logik prüfen (braucht nur Python 3)
python shell/welcome/lokroos-welcome.py --json-only
LANG=en_US.UTF-8 python shell/welcome/lokroos-welcome.py --json-only

# Tests ausführen
python -m pytest tests/ -v
python scripts/verify-manifests.py --root .
python scripts/validate-tokens.py
```

## Projektstruktur

```
lokroos/
├── AGENTS.md / IDEAS.md / IMPORTANT.md  # Agent-Wissen, Roadmap, kritische Regeln
├── README.md / BUILD.md / ARCHITECTURE.md / KNOWN_LIMITATIONS.md
├── VERSION                               # 0.1.0
├── branding/      # tokens.json (Source of Truth), tokens.css, lokroos-logo.svg
├── shell/
│   ├── qml/       # Plasma-Shell (Main, Taskbar, Launcher, SystemOverview)
│   ├── welcome/   # lokroos-welcome.py + .desktop-Autostart + welcome.qml
│   └── web-preview/  # Ausführbarer Desktop-Prototyp (HTML/CSS/JS)
├── config/        # plasma-, sddm-, plymouth-Konfigurationen (Zielsystem)
├── packages/      # manifest-base/dev/gaming/vpn.json (versionierte Paketlisten)
├── iso/           # build-iso.sh (Guards + Manifest-Check; Pipeline in M2)
├── scripts/       # check-env, verify-manifests, validate-tokens
├── tests/         # pytest-Suite (welcome, Manifeste, Tokens, Preview)
└── docs/          # INSTALL.md, MAINTENANCE.md
```

Details: `ARCHITECTURE.md`. Build-Anleitung: `BUILD.md`. Kritische Regeln: `IMPORTANT.md`.

## Feature-Status (ehrlich)

| Bereich | Status | Bemerkung |
|---|---|---|
| Designsystem (Tokens, Glass Cards) | `IMPLEMENTED` | tokens.json/css + Preview verifiziert |
| Web-Preview (Dashboard, Tabs, Charts, i18n) | `IMPLEMENTED` (Preview!) | Daten simuliert (Badge); Struktur-Tests grün |
| Welcome-Backend (User, Sprache, Fail-safe) | `IMPLEMENTED` | **Linux-verifiziert** (WSL 24.04.5); 20/20 Tests Win+Linux |
| Stats-Backend (CPU/RAM/GPU/Net/Tasks) | `IMPLEMENTED` | **Linux-verifiziert**: 16 Kerne, RTX 4060 erkannt |
| QML-Shell (Taskbar/Launcher/Übersicht/Dashboard) | `PARTIAL` | Gerüst steht (QtQuick 2.15 ✓ für Noble); Sitzungstest fehlt |
| SDDM/Plymouth/Plasma-Configs | `PARTIAL` | Configs geschrieben, Zielsystem-Test fehlt |
| Manifeste + Provisionierung (Node/npm/Wine) | `PARTIAL` | Manifeste verifiziert; `provision-lokroos.sh` dry-run ok |
| ISO-Build (live-build/Cubic) | `PLANNED` | Skript-Guards implementiert, Pipeline in M2 |
| VM-Boot-Test (Live, Installer) | `PLANNED` | WSL-Ubuntu steht; Nutzer-VM für Boot-Test vorgesehen |

Legende: `IMPLEMENTED` = implementiert + überprüft · `PARTIAL` = teilweise ·
`PLANNED` = geplant · `BLOCKED` = blockiert · `UNVERIFIED` = vorhanden, nicht ausreichend getestet.

## Sicherheit in einem Satz

Keine destruktiven Host-Eingriffe, keine Secrets im Repo, keine `.exe`-Auto-Assoziation,
privilegierte Aktionen nur via `loginctl`/PolicyKit/PackageKit – Details in `IMPORTANT.md`.
