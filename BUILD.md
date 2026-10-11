# LokroOS BUILD.md – Build-, Test- und ISO-Anleitung

Stand: 2026-10-11 · Version: 0.1.0 · Basis: Ubuntu 24.04 LTS (Noble), amd64.

## 1. Basisentscheidung (verifiziert am 2026-10-11)

| Option | Release | Support | Bewertung |
|---|---|---|---|
| **Ubuntu 24.04 LTS (Noble)** ✅ gewählt | 25.04.2024, aktuell 24.04.5 (10.09.2026) | bis 06/2029 | Reifes Tooling (Cubic, live-build, Calamares), Plasma 5.27 LTS stabil |
| Ubuntu 26.04 LTS (Resolute) | 23.04.2026, aktuell 26.04.1 (27.08.2026) | bis 05/2031 | Zu neu für Custom-Distro-M1; Evaluierung in M3 |

Quellen: ubuntu.com/project/docs/release-team/list-of-releases,
ubuntu.com/about/release-cycle (abgerufen 2026-10-11).

## 2. Was wird wo gebaut?

| Umgebung | Aufgabe | Befehle |
|---|---|---|
| **Windows-Dev-Host** (dieser PC) | Prototyp, Tests, Docs, QML-Review | `python -m pytest tests/ -v`, Preview im Browser |
| **Ubuntu-24.04-Build-VM** (M2) | ISO-Build, Paketinstallation, VM-Boot-Test | `sudo ./iso/build-iso.sh` |

> Auf dem Windows-Host wird **niemals** ein ISO-Build, Bootloader- oder
> Partitionseingriff versucht. `iso/build-iso.sh` bricht dort mit klarer
> Fehlermeldung ab (Guard verifiziert).

## 3. Voraussetzungen (Build-VM, M2)

```bash
sudo apt update && sudo apt install -y live-build calamares \
  git python3 pytest curl wget unzip build-essential
# ODER Prototyp-Weg: Cubic (https://github.com/PJ-Singh-001/Cubic) auf der VM.
```

## 4. Build-Prozess (M2, automatisiert)

```bash
git clone https://github.com/Lokrogaming/LokroOS.git
cd LokroOS
python3 scripts/verify-manifests.py --root .
python3 scripts/validate-tokens.py
sudo ./iso/build-iso.sh --profile noble --out iso/output
# → iso/output/lokroos-*.iso + Build-Log
```

Trennung Live/installed: Live-Session via Casper (`try LokroOS`), Installer
Calamares mit eigenem Branding; keine Dev-Dateien/Secrets im Image
(`.gitignore` + Manifest-Audit, siehe `ARCHITECTURE.md`).

## 5. Tests (M1, auf diesem Host ausführbar)

```bash
python -m pytest tests/ -v          # Welcome (6) + Projekt (5) = 11 Tests
python scripts/check-env.py          # Umgebungsübersicht
```

## 6. Fehlerbehandlung

| Fehler | Ursache | Lösung |
|---|---|---|
| `ISO-Build nur auf Linux` | Skript auf Windows gestartet | Auf Build-VM ausführen (by design) |
| `Bitte mit Root-Rechten` | ohne sudo | `sudo` auf der VM (nie Host-Bootloader) |
| `MANIFEST-FEHLER` | Manifest inkonsistent | `verify-manifests.py`-Ausgabe folgen |
| `Fehlende Design-Tokens` | tokens.json unvollständig | `validate-tokens.py`-Ausgabe folgen |
