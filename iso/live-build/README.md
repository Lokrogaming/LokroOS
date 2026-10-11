# LokroOS live-build-Pipeline (Schicht 4)

Reproduzierbarer ISO-Build auf Ubuntu 24.04 (root, WSL oder VM). Baut ein
**bootfähiges Hybrid-ISO**: Live-Session (Casper) + Calamares mit LokroOS-Brand.

## Bausteine

| Datei | Zweck |
|---|---|
| `extra-packages.txt` | ISO-Extras über Manifeste hinaus (ein Paket/Zeile) |
| `exclude-iso.txt` | ISO-Ausschlüsse mit Grund (z. B. `bottles`: nur Flathub; ProtonVPN: eigenes Repo, optional) |
| `make_packagelist.py` | Paketliste aus Manifesten + Extras − Excludes (importierbar, getestet) |
| `generate.sh --root REPO --out BUILD` | Schreibt Paketliste, Brand-Quellen (`includes.chroot/opt/lokroos`), Hooks |
| `hooks/0000-lokroos-repos.hook.chroot_early` | VOR Paketinstallation im Chroot: i386-Arch + Nodesource/VSCode/gh-Repos (fail-fast) |
| `hooks/0900-lokroos-brand.hook.chroot` | Deployment im Ziel-Rootfs (Plymouth, GRUB-Config, SDDM, Backends, Calamares-Brand, Install-Icon) |
| `hooks/0910-lokroos-grub-titles.hook.binary` | ISO-Bootmenü-Titel (Debian → LokroOS, fail-fast; läuft nach lb_binary_grub2) |
| `build.sh --root REPO --work DIR` | Gesamtablauf: generate → `lb config` → grub2-Override → `lb build` |

## Bekannte lb-3.x-Fallstricke (verifiziert 2026-10-11, live-build 3.0~a57)

- `--firmware-chroot` ist auf Ubuntu **kaputt**: lb parst den Contents-Index mit
  `awk '{print $2}'`, Ubuntu-Firmware-Dateinamen enthalten aber Leerzeichen
  („Xiaomi Inc-Mipad2…“) → Müll-Paketnamen → apt-Fehler. Darum `false`;
  Firmware kommt via Paket `linux-firmware`.
- `--bootloader` kennt nur `grub|syslinux|yaboot`; der casper-fähige Pfad braucht
  aber `LB_BOOTLOADER=grub2` → `build.sh` setzt Override mit Fail-fast.
- i386 + Fremd-Repos müssen VOR `install-packages` stehen → Early-Hook
  (normale Chroot-Hooks kämen zu spät), ebenfalls fail-fast.

## Ablauf (WSL-Beispiel)

```bash
sudo apt-get install -y live-build
git clone https://github.com/Lokrogaming/LokroOS.git && cd LokroOS
sudo ./iso/live-build/build.sh --root . --work ~/lokroos-build
# → ~/lokroos-build/lokroos-*.iso
```

Der Build lädt mehrere GB (Desktoppakete) und dauert je nach Maschine 30–90 Min.
`lb build` ist stufig (bootstrap/chroot/binary) – Wiederaufruf setzt fort.
Alle Schritte landen im Build-Log (`build-<version>-<datum>.log`).

## Ehrliche Grenzen

- Live-Boot-Splash: Die Live-Session nutzt die von live-build erzeugte Initrd –
  unser Plymouth-Theme liegt im Image; ob der Live-Splash es zeigt, entscheidet
  der Boot-Test (installiertes System: garantiert via `-R`-Rebuild im Hook).
- Installer-Start: `pkexec calamares` (Fallback `sudo -E calamares`) – Abnahme im
  Boot-Test (`docs/INSTALL.md`-Matrix).
- Secure Boot: Standard (`lb`-Default); bei Problemen `BUILD.md`-Fallback beachten.
