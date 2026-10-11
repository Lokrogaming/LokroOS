# LokroOS ISO-Build – Bericht (11.10.2026, Stand 15:40 Uhr)

## 1. Was gemacht wurde

- live-build-Pipeline ins Repo gebaut (`iso/live-build/`: `generate.sh`,
  `build.sh`, `make_packagelist.py`, 3 Hooks, `extra-packages.txt`,
  `exclude-iso.txt`, `cubic-preset.json`) – Pakete kommen aus einer Wahrheit
  (`packages/manifest-*.json`).
- live-build 3.0~a57 + Tooling (xorriso, debootstrap) im WSL-Ubuntu 24.04
  installiert (root, 954 GB frei, 14 GB RAM, 16 CPUs).
- 4 Build-Anläufe in `~/lokroos-build`; Anlauf 3+4 kamen bis in Chroot/Binary.
- **Ergebnis: noch kein ISO.** Chroot dagegen verifiziert (s. u.).

## 2. Was erkannt und wie gefixt wurde

| # | Erkenntnis (mit Beleg) | Fix (gepusht) |
|---|---|---|
| 1 | live-build 3.x-CLI ≠ Klassik (`--bootloaders`, `--username`, `--updates` … unbekannt; belegt via `lb config --help`) | `build.sh` auf `--bootloader grub`, `--bootappend-failsafe`, `--volatile`, `--initramfs casper`, Casper-Bootparameter (`username=lokro`) umgestellt |
| 2 | `--firmware-chroot` ist auf Ubuntu kaputt: lb parst Contents mit `awk '{print $2}'`, Ubuntu-Firmware-Dateinamen enthalten Leerzeichen („Xiaomi Inc-Mipad2…“) → Müll-Paketnamen → apt-Fehler (belegt per Byte-Analyse des 829-MB-Contents-Index) | `false`; Firmware kommt via Paket `linux-firmware` |
| 3 | lb 3.x findet Hooks NUR flach unter `config/hooks/` (`*.chroot`, `*.chroot_early`, `*.binary`) – `normal/`-Unterverzeichnis und `.hook.*`-Namen sind tot (belegt in `lb_chroot_early_hooks`/`lb_chroot_hooks`/`lb_binary_hooks`) | Hooks umbenannt, `generate.sh` kopiert flach, Regressions-Test |
| 4 | `LB_BOOTLOADER` wird aus MEHREREN Config-Dateien gelesen (spätere gewinnen): Override nur in `config/common` wurde von `config/binary` („grub“) geschlagen → Legacy-Pfad wollte `grub-legacy` installieren → `E: no installation candidate` (Log-Beleg) | Override in `common` UND `binary`, Fail-fast-Prüfung |
| 5 | Paket-Realität Noble: `steam` hat keinen Kandidaten (→ `steam-installer`), `bottles`/`proton-vpn-gnome-desktop` nicht in Archiven, `wine32`/`:i386` braucht i386-Arch, `nodejs`/`code`/`gh` brauchen Fremd-Repos (belegt via `apt-cache policy` + Build-Log) | Manifest korrigiert, ISO-Exclude-Liste, Early-Hook (i386 + Nodesource/VSCode/gh, fail-fast) |
| 6 | `.gitignore`-Zeile `live-build/` hat `iso/live-build/`-Quellen verschluckt (Push ohne Pipeline entdeckt via `git ls-tree`) | Ignore auf Outputs verengt + Tracking-Regressions-Test |
| 7 | Calamares-Deb legt kein `/etc/calamares` an → Brand-Hook lief ins Leere (belegt: Chroot-Probe) | `calamares-settings-ubuntu-common` als Settings-Basis ins ISO aufgenommen |

## 3. Verifizierter Zwischenstand (Chroot-Probe, kein Glaube)

- 2347 Pakete installiert: `kubuntu-desktop`, `nodejs`, `code`, `gh`, `wine32`,
  `steam-installer`, `calamares`, `casper`, `linux-firmware` → alle OK.
- `dpkg/arch`: `amd64` + `i386`; Backends + Plymouth-Theme deployed;
  Early-Hook lief bis „Early-Setup fertig.“; apt-Fehlerzähler: 0.
- Offen: Calamares-Brand-Ablage (fehlte Settings-Basis – Fix 7, noch nicht gebaut).

## 4. Aktuelles Problem (ehrlich)

Build 4 starb gegen **15:21 Uhr kommentarlos** in der Includes/Hook-Phase
(Log endet mitten in Dateiliste, kein Fehler, kein Abort).
Ausgeschlossen per Prüfung: OOM (dmesg leer), Platte voll (941 GB frei),
apt-Fehler (Zähler 0). Keine ISO erzeugt. Nächster Schritt: Resume im
bestehenden Build-Baum (Stages bleiben erhalten) und engmaschiges Polling;
bei Wiederholung sauberer Relaunch mit `setsid`-Abkopplung.

## 5. Rückschlüsse

- Fail-fast zahlt sich aus: Jeder Fehler wurde zur exakten Stelle (statt zu
  kaputtem ISO).
- live-build 3.0~a57 (Alpha) weicht an ≥5 Stellen von Doku/Klassik ab –
  nur lb-Quellcode lesen bringt belastbare Antworten.
- Tool-Lehre: Shell-Quoting durch die PowerShell→WSL-Kette ist unzuverlässig
  (Pipes/Muster werden gefressen); Log-Analyse nur noch per Probe-Skript-Dateien.
- WSL baut prinzipiell (Netz, Platz, Rechte ok) – Display/Boot-Test bleibt VM-Sache.

## 6. Nachtrag: ISO fertig (16:55 Uhr, verifiziert)

- `iso/output/lokroos-0.4.0-amd64.iso`: 3.549.546.496 Bytes, ISO 9660,
  Volume-ID `LokroOS`, El-Torito-bootfähig, `isohybrid` gesetzt.
- SHA-256: `731af5c4e2a4d8ae99d9860974cb39eec09b37fb1a8d91f41816215190cc042e`
  (Build-Baum und Windows-Kopie identisch).
- GRUB-Menü aus dem ISO extrahiert: „Try or Install LokroOS“,
  „LokroOS (safe graphics)“ (+ Kernel-Varianten), kein Debian-/Kubuntu-Text.
- Gelöste Blockaden auf dem Weg: SquashFS-Trim 4,2 → 3,3 GB
  (`iso/live-build/trim-packages.txt`), `binary/`-Layout versöhnt
  (`chroot/binary` → `./binary`), `syslinux-utils` (isohybrid) nachinstalliert.
- Offen: Live-Boot + Installer-Abnahme in der VM (Testmatrix `docs/INSTALL.md`).
