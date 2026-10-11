# LokroOS live-build-Pipeline (Schicht 4)

Reproduzierbarer ISO-Build auf Ubuntu 24.04 (root, WSL oder VM). Baut ein
**bootfähiges Hybrid-ISO**: Live-Session (Casper) + Calamares mit LokroOS-Brand.

## Bausteine

| Datei | Zweck |
|---|---|
| `extra-packages.txt` | ISO-Extras über Manifeste hinaus (ein Paket/Zeile) |
| `generate.sh --root REPO --out BUILD` | Paketliste aus Manifesten (dedup) + Brand-Quellen nach `config/includes.chroot/opt/lokroos` + Hook kopieren |
| `hooks/0900-lokroos-brand.hook.chroot` | Deployment im Ziel-Rootfs (Plymouth, GRUB-Config, SDDM, Backends, Calamares-Brand, Install-Icon) |
| `hooks/0910-lokroos-grub-titles.hook.binary` | ISO-Bootmenü-Titel (Debian → LokroOS, fail-fast; läuft nach lb_binary_grub2) |
| `build.sh --root REPO --work DIR` | Gesamtablauf: generate → `lb config` → grub2-Override → `lb build` |

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
