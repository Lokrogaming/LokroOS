# LokroOS KNOWN_LIMITATIONS.md – Bekannte Einschränkungen (ehrlich, Stand 2026-10-11)

## Umgebung (verifiziert)

- Dev-Host: Windows 11 Pro, Ryzen 7 9700X (amd64), 32 GB RAM – **kein Linux-Build-Host**.
- WSL2: installiert (v2), aber **keine Distribution** registriert → kein ISO-Build möglich.
- Kein Docker, kein VirtualBox/VMware, kein `lb` (live-build) auf dem Host.
- Folge: ISO-Build (`PLANNED`), VM-Boot-Test (`PLANNED`) und echte Plasma-Wayland-Sitzung
  (`UNVERIFIED` für QML/SDDM/Plymouth) sind bis zur Build-VM blockiert.

## Funktional

- Web-Preview ist ein **Prototyp** (Browser), keine native Plasma-Integration – bewusst so für M1.
- Paketinstallation (Node, Steam, Wine, ProtonVPN …) ist als Manifest + Methode definiert,
  aber auf dem Windows-Host **nicht ausführbar** → Verifikation erfolgt auf Build-VM (M2).
- Proton-GE-Updates via ProtonUp-Qt, Bottles-Flatpak und NVIDIA-Autoinstall sind dokumentiert,
  aber noch nicht end-to-end getestet.
- Anti-Cheat-Titel (EAC mit Fremd-Modulen, Vanguard) werden voraussichtlich **nicht** laufen –
  wird in `docs/INSTALL.md` dokumentiert.

## Nächste Schritte zur Behebung

1. Ubuntu-24.04-Build-VM aufsetzen (WSL2-Distro oder Hyper-V/VirtualBox).
2. `sudo ./iso/build-iso.sh` + Paketinstallation auf der VM ausführen.
3. ISO in VM booten: Live, Installer, Login, Desktop, Apps, Updates, Netzwerk, Audio prüfen.
4. Status in README/AGENTS von `PLANNED`/`UNVERIFIED` auf `IMPLEMENTED` heben – nur mit Beleg.
