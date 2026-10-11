# LokroOS AGENTS.md – Zentrale technische Wissensbasis

> **Pflichtlektüre für jeden Coding-Agent.** Lies zuerst `AGENTS.md`, `IMPORTANT.md`
> und bei Erweiterungen `IDEAS.md`. Prüfe danach gezielt nur aufgabenrelevante Dateien
> (Docs = Einstieg, nicht Ersatz für Codeprüfung). Stand: 2026-10-11, Version 0.4.0.
> Schichten strikt trennen (Preview ≠ Shell ≠ System ≠ ISO) – Details in `ARCHITECTURE.md` §0.

## 1. Projektziel & Designphilosophie

LokroOS ist eine eigenständige Linux-Distribution von LOKRO für Entwickler, Gamer und
technisch Interessierte: Ubuntu-LTS-Basis, KDE Plasma + Wayland, dunkles
Glassmorphism-Design (Schwarz/Anthrazit/tiefes Blau, Cyan-Akzente, dezente Glows),
Performance + Sicherheit + Wartbarkeit. **Kein generisches Linux-Theme** – Identität über
`branding/tokens.json` (Single Source of Truth für Farben, Typo, Radien, Schatten,
Blur, Motion), konsistent in CSS, QML und Docs.

## 2. Grundentscheidungen (verifiziert 2026-10-11)

- Basis: **Ubuntu 24.04 LTS (Noble, amd64)**, Support bis 06/2029. Ubuntu 26.04.1 LTS
  (Resolute, 27.08.2026) existiert, ist aber bewusst **nicht** M1-Basis (Tooling-Reife:
  Cubic/live-build/Calamares + Plasma 5.27). Evaluierung in M3.
- Desktop: KDE Plasma + Wayland (`kubuntu-desktop`, `plasma-workspace-wayland`), Login SDDM,
  Boot Plymouth, Installer Calamares. Dev-Host: Windows 11 (Ryzen 7 9700X, 32 GB) –
  ISO-Builds **nur** auf Ubuntu (WSL-Distro oder Build-VM).
- Shell-Stack (apt-verifiziert 2026-10-11 auf Noble): **QML2 (QtQuick 2.15, Qt 5.15.13)**
  auf **Plasma 5.27.12** + `layer-shell-qt`; C++ nur bei Bedarf (aktuell keins nötig),
  **kein** Custom-Kernel (Stock-Ubuntu-Kernel). Qt6/Plasma 6 erst beim 26.04-Rebase (M3+).
- Testumgebung: WSL-`Ubuntu-24.04` (24.04.5 LTS, Python 3.12) auf dem Dev-Host –
  Python-Backends laufen dort **echt** (keine VM nötig für Schicht 3).
- Sprache: DE/EN via Systemsprache (`$LANG`/Plasma-Locale), Fallback EN.
- Updates: **kein eigenes System** – APT + PackageKit/Discover.

## 3. Projektstruktur

```
VERSION                          # 0.2.0 (SemVer)
branding/tokens.json             # Design-Tokens (Wahrheit) | .css (Web) | logo.svg
shell/qml/Main|Taskbar|Launcher|SystemOverview|Dashboard.qml  # Native Shell (QML2, PARTIAL)
shell/welcome/lokroos-welcome.py # Welcome-Backend (IMPLEMENTED, Linux-verifiziert)
shell/stats/lokroos-stats.py     # Stats-Backend CPU/RAM/GPU/Net/Tasks (IMPLEMENTED, Linux-verifiziert)
shell/welcome/*.desktop, welcome.qml                 # Autostart + Overlay (modelless)
shell/web-preview/index.html|styles.css|app.js        # NUR visueller Prototyp (simulierte Daten!)
config/plasma| sddm| plymouth/   # Zielsystem-Konfigurationen (/etc)
packages/manifest-{base,dev,gaming,vpn}.json         # Versionierte Paketlisten
iso/build-iso.sh | iso/provision-lokroos.sh          # ISO-Guards / VM-Provisionierung (PARTIAL)
scripts/check-env|verify-manifests|validate-tokens.py
tests/test_welcome.py (6) | test_stats.py (8) | test_project.py (6)  # 20 Tests, Win+Linux grün
tests/fixtures/proc/             # Fake-/proc (stat, meminfo, net_dev)
docs/INSTALL.md | MAINTENANCE.md
README|BUILD|ARCHITECTURE|KNOWN_LIMITATIONS.md | AGENTS|IDEAS|IMPORTANT.md
```

## 4. Architektur & Kommunikation

Boot (Plymouth) → Login (SDDM) → Welcome-Overlay (modelless, Fail-safe) →
Plasma-Wayland + QML-Shell (Single-Instance via `flock`, Panel = Auto-Hide).
Shell↔System nur nativ: D-Bus/NetworkManager, PipeWire, PackageKit, `loginctl`
(PolicyKit) – kein Root-Daemon. Welcome→Shell: Einweg-JSON, kein Passwort.
VPN: nur App-Öffnung + lesender Status. Gaming: Steam (multiverse) + Proton via Steam,
Wine nur explizit („Mit Wine ausführen“/Bottles), **keine** `.exe`-Auto-Assoziation
(per Test erzwungen). Stats: `executable`-Datenquelle → `lokroos-stats.py --once`
(JSON, 2-s-Polling). Schichtenmodell + Belegmatrix: `ARCHITECTURE.md` §0–§1.

## 5. Designsystem (Kurzreferenz)

Schwarz `#06090F`, Anthrazit `#0E141D/#151D29`, Tiefblau `#0B1B33`, Cyan `#22D3EE`,
Hellblau `#7DD3FC`, Text `#F1F5F9/#94A3B8`. Glass: `rgba(14,20,29,.62)`, Blur 18/28px,
Radien 10/16/22/28px, Schatten Card/Glow, Motion 120/220/380ms + `cubic-bezier(.22,1,.36,1)`.
`prefers-reduced-motion`/`LOKROOS_NO_ANIM=1` → keine Animation. Konventionen: große
Glass-Cards, Pill-Badges, min. Kontrast Secondary-Text, Fokus-Ringe sichtbar.
Designrichtung: CasaOS-inspiriert (Dashboard-first, Kacheln, Status auf einen Blick),
aber eigene dunkle Identität + optionaler **Light Mode** (`tokens.json > theme.light`,
Preview-Umschalter). Details: `docs/DESIGN_CASAOS.md`. Regel: Versprochenes ausführen
oder als `Demo` kennzeichnen (Preview) bzw. weglassen (QML).

## 6. Boot-/Login-/Welcome-Ablauf

1. Plymouth (`config/plymouth/`): Logo + dezenter Spinner, textlos.
2. SDDM (`config/sddm/lokroos.conf`): Login, **kein** Autologin mit Secrets.
3. `lokroos-welcome.py` (Autostart): User + `$LANG` → JSON → `welcome.qml`-Overlay
   (Fade 600ms, Reveal 900ms, Loader ~1,2s, Selbst-Schluss ~3s, modelless, Exit 0 immer).

## 7. Feature-Status (ehrlich pflegen!)

- `IMPLEMENTED`: Tokens+CSS (Dark + Light), Web-Preview (Dashboard-Fenster, schließbare Tabs, Charts, i18n, Theme-Toggle),
  Welcome-Backend + Stats-Backend (**beide Linux-verifiziert** im WSL-Ubuntu 24.04.5),
  Plymouth-Theme (Assets generiert, Boot-Tests), GRUB-Snippets (schlicht).
- `PARTIAL`: QML-Shell (+Dashboard.qml), SDDM/Plasma-Configs, Manifeste,
  `provision-lokroos.sh` (inkl. Theme-/GRUB-/Calamares-Deploy, Echtlauf ausstehend),
  Calamares-Brand (`branding.desc` + `show.qml` API 2 DE/EN, Abnahme ausstehend),
  Installer-Spec (10 Schritte → Calamares-Module, `installer/INSTALLER_SPEC.md`).
- `PLANNED`: Cubic-ISO als Alternative, VM-Boot-Test (Live/Installer/Apps/Updates/Netz/Audio).
- `IMPLEMENTED` (Schicht 4): live-build-ISO `lokroos-0.4.0-amd64.iso`
  (3,3 GB, SHA-256 + GRUB-Titel verifiziert, Details `docs/BUILD-REPORT-2026-10-11-ISO.md` §6).
- `BLOCKED`: derzeit nichts (WSL-Ubuntu steht; echte Plasma-Wayland-Sitzung weiter ohne Display).
- `UNVERIFIED`: QML/SDDM/Plymouth ohne echte Wayland-Sitzung. – **Niemals Plan mit Funktionierendem verwechseln.**
- Tests: **grün auf Windows UND Linux** (ein Linux-spezifischer getpass-Fall wurde gefunden + gefixt).

## 8. Programme & Methoden

- Dev (`manifest-dev.json`): Node 22 LTS via NodeSource (**eine** Version) + npm gebündelt,
  Git, gh (offiz. Repo, ohne Credentials), VS Code (Microsoft-Repo), build-essential,
  Python 3, curl/wget/unzip, OpenSSH. Verify: `node/npm/git/gh/code/python3 --version`.
- Gaming (`manifest-gaming.json`): Steam (multiverse), Proton via Steam (+GE via ProtonUp-Qt
  optional), wine64/32 + winetricks, Bottles optional, mesa-vulkan (+i386, `enable_i386`),
  gamemode/mangohud. NVIDIA nur via `ubuntu-drivers` bei erkannter HW.
- VPN (`manifest-vpn.json`): offizielles ProtonVPN-Repo + GUI-Paket, Starter + lesender Status.

## 9. ISO & Installation

`iso/build-iso.sh` (Guards: nur Linux+Ubuntu+Root, sonst Abbruch ohne Änderung) →
Manifest-/Token-Checks → live-build (M2) / Cubic (Prototyp). Casper-Live vs.
Calamares-Postinstall getrennt; `.gitignore` + Audit gegen Secret-Leaks.
Handbuch: `docs/INSTALL.md`, Wartung: `docs/MAINTENANCE.md`, Anleitung: `BUILD.md`.

## 10. Technologien & Befehle

Python 3 (native Backends welcome/stats + Tests/Build-Helfer), QML2-Shell
(QtQuick 2.15 / Plasma 5.27, C++ nur bei begründeter Lücke), HTML/CSS/JS **nur**
für den visuellen Prototyp (simulierte Daten, fließt nie in ISO; kein Electron),
Bash (Provision/Build), Calamares, SDDM, Plymouth, APT/PackageKit.
```bash
python -m pytest tests/ -v                          # 20 Tests (Win + WSL-Linux ausführen!)
python scripts/verify-manifests.py --root . && python scripts/validate-tokens.py
python shell/welcome/lokroos-welcome.py --json-only
python shell/stats/lokroos-stats.py --check         # auf Linux: echte /proc-Werte
wsl -d Ubuntu-24.04 -- bash -c "cd /mnt/c/Users/lokro/projekte/lokroos && python3 -m pytest tests/"
sudo ./iso/provision-lokroos.sh --dry-run           # nur Ubuntu 24.04 (VM); Echtlauf mit --yes
sudo ./iso/build-iso.sh --profile noble --out iso/output   # nur Ubuntu-Build-VM!
```

## 11. Sicherheitsregeln (Kurzform, Details: IMPORTANT.md)

Kein Host-Eingriff (Bootloader/Partitionen/Netz), keine Secrets im Repo, eine Node-Version,
kein NVIDIA blind, keine `.exe`-Auto-Assoziation, kein eigenes Update-System, keine
Root-Daemons (nur loginctl/PolicyKit/PackageKit), Username nur via `text:`/`textContent`.
Schichtendisziplin: Web-Preview-Code darf **nie** in ISO/Shell wandern (nur Tokens/QML/Python).

## 12. Bekannte Schulden & Phase

Schulden: QML-Sitzungstest, Provision-/Calamares-Abnahme in VM, Cubic-ISO,
M2-Pipeline, VM-Matrix (Boot/Live/Installer/Login/Apps/Updates/Netz/Audio).
Phase: **M2+ (eigenständige Distro, Stufe A)**: Backends Linux-verifiziert,
Boot-Branding + Installer-Spec stehen; nächste Aufgaben: (1) Provision-Echtlauf
in VM, (2) `calamares -c`-Abnahme, (3) Cubic-ISO + Boot-Matrix. Blockierte Arbeit als `BLOCKED` markieren,
nicht scheinlösen. Einschränkungen: `KNOWN_LIMITATIONS.md`.

## 13. Regeln für Agents (verbindlich)

1. Lies zuerst `AGENTS.md`, `IMPORTANT.md`, bei Erweiterungen `IDEAS.md`.
2. Prüfe danach gezielt nur aufgabenrelevante Dateien.
3. Docs = Einstieg, nicht Ersatz für Codeprüfung.
4. Kein Full-Repo-Rescan ohne Grund.
5. Erfinde keine APIs/Dateien/Funktionen/Dienste – verifiziere Existenz im Code.
6. Prüfe vor Änderungen den echten Implementierungsstand (Status-Tabelle).
7. Erhalte Architektur + Designsystem (Tokens), außer explizit beauftragte Evolution.
8. Aktualisiere Docs bei Architektur-/Schnittstellen-/Build-/Status-Änderungen.
9. Keine Redundanz: kein Re-Implementieren, kein Analyse-Loop über Erledigtes.
10. Kleine, nachvollziehbare Änderungen + relevante Tests ausführen.
11. Bei unklar/destruktiv/sicherheitskritisch: **fragen**, nicht überschreiben.
12. Keine Secrets/Personendaten in Code, Docs oder Commits.

## 14. Änderungs-/Commit-Regeln

Kleine Commits (imperativ, z. B. `Add LokroOS M1 prototype (shell, manifests, tests)`),
kein Force-Push auf `main`, keine fremden Commits umschreiben, vor Push
`pytest` + `verify-manifests` grün. Doku als lebendiger Prozess: AGENTS/IDEAS/
IMPORTANT nur bei betroffenem Inhalt ändern, Duplikate/Widersprüche entfernen.
