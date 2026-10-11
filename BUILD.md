# LokroOS BUILD.md – Build-, Test- und ISO-Anleitung

Stand: 2026-10-11 · Version: 0.4.0 · Basis: Ubuntu 24.04 LTS (Noble), amd64.

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

## 4. Build-Prozess (verifiziert 2026-10-11, WSL-Ubuntu 24.04)

Voraussetzungen (einmalig): `sudo apt-get install -y live-build xorriso isolinux
syslinux-utils git python3` (isohybrid kommt aus `syslinux-utils`).

```bash
git clone https://github.com/Lokrogaming/LokroOS.git && cd LokroOS
sudo ./iso/live-build/build.sh --root . --work ~/lokroos-build
# → lokroos-0.4.0-amd64.iso (3,3 GB) + Build-Log
```

Verifiziert am Erst-Build: ISO 9660, Volume-ID `LokroOS`, El Torito bootfähig,
GRUB-Menü („Try or Install LokroOS“, „LokroOS (safe graphics)“), SHA-256 im Log.
Bekannte lb-3.x-Fallstricke (Details: `iso/live-build/README.md`): grub2-Override
in allen Config-Dateien, Firmware-Scrape aus, i386 + Fremd-Repos per Early-Hook,
SquashFS < 4 GiB (Trim-Liste), `binary/`-Layout ggf. manuell versöhnen.

## 4b. Cubic-Prototyp-ISO (in der Kubuntu-VM, GUI vorhanden)

Vorlage: `iso/cubic-preset.json` (manuell in Cubic umsetzen – kein Maschinenformat).

1. Cubic installieren: `sudo apt-add-repository universe && sudo apt install --no-install-recommends cubic`
   (oder PPA `cubic-wizard/release` für neuere Version).
2. Basis-ISO `kubuntu-24.04.5-desktop-amd64.iso` wählen, Chroot öffnen.
3. Im Chroot die Provisionsschritte aus `iso/provision-lokroos.sh` übernehmen
   (Repos, Kern-Pakete, Shell-Deploy, **Plymouth-Theme, GRUB-Config, Calamares-Brand**).
4. Vor dem Packen prüfen: `plymouth-set-default-theme` → `lokroos`,
   `grep branding /etc/calamares/settings.conf` → `lokroos`, `node/npm/wine --version`.
5. Boot-Tab: Einträge aus `config/grub/iso-entries.cfg.snippet`
   („Try or Install LokroOS“, „LokroOS (safe graphics)“) – Kernel-Pfade setzt Cubic.
6. ISO packen → in neuer VM booten → Bootmenü, Splash (installiert), Installer-Brand prüfen.

Bekannte Einschränkung (Cubic-Upstream, ab 23.04): Der **Live**-Boot nutzt die
Original-Initrd der Basis-ISO – unser Plymouth-Theme greift dort erst nach
eigenem Initrd-Neubau; das **installierte** System zeigt es sofort. Deshalb ist
der Live-Splash bewusst später eingeplant (siehe `ARCHITECTURE.md` §5).

Trennung Live/installed: Live-Session via Casper (`try LokroOS`), Installer
Calamares mit eigenem Branding; keine Dev-Dateien/Secrets im Image
(`.gitignore` + Manifest-Audit, siehe `ARCHITECTURE.md`).

## 5. Tests (M1, auf diesem Host ausführbar)

```bash
python -m pytest tests/ -v          # 33 Tests (Win + WSL-Linux ausführen!)
python branding/render-assets.py --check  # Plymouth-PNGs vorhanden/gültig
python scripts/check-env.py          # Umgebungsübersicht
# Linux-Gegenprobe + Provision-Dry-Run (WSL, ungefährlich, ändert nichts):
wsl -d Ubuntu-24.04 -- bash -c "cd /mnt/c/Users/lokro/projekte/lokroos && python3 -m pytest tests/"
wsl -d Ubuntu-24.04 -- bash -c "cd /mnt/c/Users/lokro/projekte/lokroos && sudo ./iso/provision-lokroos.sh --dry-run"
```

## 6. Fehlerbehandlung

| Fehler | Ursache | Lösung |
|---|---|---|
| `ISO-Build nur auf Linux` | Skript auf Windows gestartet | Auf Build-VM ausführen (by design) |
| `Bitte mit Root-Rechten` | ohne sudo | `sudo` auf der VM (nie Host-Bootloader) |
| `MANIFEST-FEHLER` | Manifest inkonsistent | `verify-manifests.py`-Ausgabe folgen |
| `Fehlende Design-Tokens` | tokens.json unvollständig | `validate-tokens.py`-Ausgabe folgen |
